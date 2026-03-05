from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from ortools.sat.python import cp_model
import ortools

from claudescycles.gm import n_vertices, succ_index
from claudescycles.io import Decomposition, save_decomposition
from claudescycles.verify import verify_decomposition


def _default_out_path(m: int) -> Path:
    return Path("artifacts") / "solutions" / f"cpsat_m{m}.json"


def solve_cp_sat(
    m: int, time_limit_s: float = 60.0, seed: int = 0, log: bool = False
) -> Decomposition | None:
    if m <= 2:
        raise ValueError("m must be > 2")

    n = n_vertices(m)
    heads = [[succ_index(u, d, m) for d in range(3)] for u in range(n)]

    model = cp_model.CpModel()
    x = [
        [
            [model.new_bool_var(f"x_c{c}_u{u}_d{d}") for d in range(3)]
            for u in range(n)
        ]
        for c in range(3)
    ]

    for u in range(n):
        for d in range(3):
            model.add(sum(x[c][u][d] for c in range(3)) == 1)

    for c in range(3):
        arcs = []
        for u in range(n):
            for d in range(3):
                arcs.append([u, heads[u][d], x[c][u][d]])
        model.add_circuit(arcs)

    model.add(x[0][0][0] == 1)
    model.add(x[1][0][1] == 1)
    model.add(x[2][0][2] == 1)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(time_limit_s)
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = int(seed)
    solver.parameters.log_search_progress = bool(log)

    status = solver.solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None

    dirs = []
    for c in range(3):
        dc = bytearray(n)
        for u in range(n):
            chosen = None
            for d in range(3):
                if solver.value(x[c][u][d]):
                    chosen = d
                    break
            if chosen is None:
                raise RuntimeError(
                    f"internal error: no outgoing arc chosen for cycle {c} at u={u}"
                )
            dc[u] = chosen
        dirs.append(dc)

    meta = {
        "generator": "scripts/search_cp_sat.py",
        "solver": "ortools.cpsat",
        "ortools_version": getattr(ortools, "__version__", None),
        "m": m,
        "n_vertices": n,
        "random_seed": seed,
        "time_limit_s": time_limit_s,
        "status": int(status),
        "wall_time_s": float(solver.wall_time),
        "branches": int(solver.num_branches),
        "conflicts": int(solver.num_conflicts),
        "symmetry_breaking": "x[0,0,0]=1; x[1,0,1]=1; x[2,0,2]=1",
        "argv": sys.argv[1:],
    }
    return Decomposition(m=m, dirs=dirs, meta=meta)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="Find a 3-cycle decomposition of G_m using OR-Tools CP-SAT."
    )
    ap.add_argument("m", type=int, help="modulus m (>2)")
    ap.add_argument(
        "--time-limit-s", type=float, default=60.0, help="CP-SAT wall-clock time limit"
    )
    ap.add_argument(
        "--seed",
        type=int,
        default=0,
        help="CP-SAT random seed (determinism with 1 worker)",
    )
    ap.add_argument(
        "--log", action="store_true", help="Enable CP-SAT search progress logging"
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output path (default: artifacts/solutions/cpsat_m{m}.json)",
    )
    ap.add_argument(
        "--overwrite", action="store_true", help="Overwrite output file if it exists"
    )
    args = ap.parse_args(argv)

    out_path = args.out if args.out is not None else _default_out_path(args.m)
    if out_path.exists() and not args.overwrite:
        print(
            f"Refusing to overwrite existing file: {out_path} (use --overwrite)",
            file=sys.stderr,
        )
        return 2

    decomp = solve_cp_sat(args.m, args.time_limit_s, args.seed, args.log)
    if decomp is None:
        print(f"UNSAT/UNKNOWN within time limit: m={args.m}", file=sys.stderr)
        return 1

    report = verify_decomposition(decomp.m, decomp.dirs)
    if not report.ok:
        print(
            f"Internal error: solver produced invalid decomposition: {report.error}",
            file=sys.stderr,
        )
        return 3

    save_decomposition(out_path, decomp)
    print(
        f"FOUND: m={args.m} in {decomp.meta.get('wall_time_s'):.3f}s; wrote {out_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

