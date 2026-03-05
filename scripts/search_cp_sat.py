from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from ortools import __version__ as ortools_version
from ortools.sat.python import cp_model

from claudescycles.gm import n_vertices, succ_index
from claudescycles.io import Decomposition, save_decomposition
from claudescycles.verify import verify_decomposition


def _default_out_path(m: int) -> Path:
    return Path("artifacts") / "solutions" / f"cpsat_m{m}.json"


def solve_cp_sat(
    m: int,
    time_limit_s: float = 60.0,
    seed: int = 0,
    log: bool = False,
) -> Decomposition | None:
    if m <= 2:
        raise ValueError("m must be > 2")

    n = n_vertices(m)
    heads = [[succ_index(u, d, m) for d in range(3)] for u in range(n)]

    model = cp_model.CpModel()
    x = [
        [
            [model.new_bool_var(f"x_{c}_{u}_{d}") for d in range(3)]
            for u in range(n)
        ]
        for c in range(3)
    ]

    for u in range(n):
        for d in range(3):
            model.add(sum(x[c][u][d] for c in range(3)) == 1)

    for c in range(3):
        arcs: list[tuple[int, int, cp_model.IntVar]] = []
        for u in range(n):
            for d in range(3):
                arcs.append((u, heads[u][d], x[c][u][d]))
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

    dirs: list[bytearray] = []
    for c in range(3):
        dc = bytearray(n)
        for u in range(n):
            chosen = None
            for d in range(3):
                if solver.value(x[c][u][d]):
                    chosen = d
                    break
            if chosen is None:
                raise RuntimeError(f"internal error: no outgoing arc chosen for cycle {c} at u={u}")
            dc[u] = chosen
        dirs.append(dc)

    meta = {
        "generator": "scripts/search_cp_sat.py",
        "solver": "ortools.cpsat",
        "ortools_version": ortools_version,
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
    ap = argparse.ArgumentParser(description="Search for a 3-cycle decomposition of G_m using OR-Tools CP-SAT.")
    ap.add_argument("m", type=int, help="Modulus m")
    ap.add_argument("--time-limit", type=float, default=60.0, help="Time limit in seconds")
    ap.add_argument("--seed", type=int, default=0, help="Random seed")
    ap.add_argument("--log", action="store_true", help="Enable OR-Tools search logging")
    ap.add_argument("--out", type=Path, default=None, help="Output JSON path")
    args = ap.parse_args(argv)

    out_path = args.out or _default_out_path(args.m)
    decomp = solve_cp_sat(args.m, time_limit_s=args.time_limit, seed=args.seed, log=args.log)
    if decomp is None:
        print(f"FAIL: no solution found for m={args.m} within {args.time_limit:.1f}s", file=sys.stderr)
        return 2

    report = verify_decomposition(args.m, decomp.dirs)
    if not report.ok:
        print(f"FAIL: solver output did not verify: {report.error}", file=sys.stderr)
        return 2

    save_decomposition(out_path, decomp)
    print(
        f"PASS: found verified decomposition for m={args.m}; "
        f"saved {out_path}; wall_time_s={decomp.meta['wall_time_s']:.3f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

