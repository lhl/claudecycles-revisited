from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Sequence

from ortools.sat.python import cp_model

from .core import Decomposition, n_vertices, succ_idx
from .verify import VerifyResult, verify_decomposition


def _status_outcome(status: int) -> str:
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return "HIT"
    if status == cp_model.INFEASIBLE:
        return "UNSAT"
    if status == cp_model.MODEL_INVALID:
        return "MODEL_INVALID"
    return "NO_HIT"


def _solve_cpsat_even_m(
    *,
    m: int,
    time_limit_sec: float,
    seed: int,
    num_workers: int,
    symmetry_break_vertex0: bool,
) -> tuple[int, Decomposition | None, VerifyResult | None, dict[str, Any]]:
    n = n_vertices(m)

    model = cp_model.CpModel()

    x: list[list[list[cp_model.IntVar]]] = [
        [
            [model.NewBoolVar(f"x_{v}_{c}_{d}") for d in range(3)]
            for c in range(3)
        ]
        for v in range(n)
    ]

    # Per-cycle outdegree=1 at every vertex.
    for v in range(n):
        for c in range(3):
            model.Add(sum(x[v][c][d] for d in range(3)) == 1)

    # Arc partition across cycles: every direction is used by exactly one cycle at each vertex.
    for v in range(n):
        for d in range(3):
            model.Add(sum(x[v][c][d] for c in range(3)) == 1)

    # Hamiltonicity: each cycle is a single directed Hamiltonian cycle (no subtours).
    for c in range(3):
        arcs: list[tuple[int, int, cp_model.IntVar]] = []
        for v in range(n):
            for d in range(3):
                arcs.append((v, succ_idx(v, d, m), x[v][c][d]))
        model.AddCircuit(arcs)

    if symmetry_break_vertex0:
        # Cycle-label symmetry breaking at vertex 000.
        model.Add(x[0][0][0] == 1)  # cycle 0 bumps i at (0,0,0)
        model.Add(x[0][1][1] == 1)  # cycle 1 bumps j at (0,0,0)
        model.Add(x[0][2][2] == 1)  # cycle 2 bumps k at (0,0,0)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(time_limit_sec)
    solver.parameters.random_seed = int(seed)
    solver.parameters.num_search_workers = int(num_workers)

    status = solver.Solve(model)
    stats: dict[str, Any] = {
        "m": m,
        "n_vertices": n,
        "solver": "ortools-cpsat",
        "time_limit_sec": float(time_limit_sec),
        "seed": int(seed),
        "num_workers": int(num_workers),
        "symmetry_breaking": {"vertex0_cycle_labels": bool(symmetry_break_vertex0)},
        "status_name": solver.StatusName(status),
        "outcome": _status_outcome(status),
        "wall_time_sec": float(solver.WallTime()),
        "num_conflicts": int(solver.NumConflicts()),
        "num_branches": int(solver.NumBranches()),
        "response_stats": solver.ResponseStats(),
    }

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return status, None, None, stats

    c0: list[int] = [0] * n
    c1: list[int] = [0] * n
    c2: list[int] = [0] * n
    cycles = (c0, c1, c2)

    for v in range(n):
        for c in range(3):
            chosen: int | None = None
            for d in range(3):
                if solver.Value(x[v][c][d]):
                    chosen = d
                    break
            if chosen is None:
                raise RuntimeError(f"internal error: no direction chosen for v={v} c={c}")
            cycles[c][v] = chosen

    decomp = Decomposition(m=m, cycle_dirs=(c0, c1, c2))
    verify = verify_decomposition(decomp)
    return status, decomp, verify, stats


def _cli(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Find even-m decompositions with OR-Tools CP-SAT (AddCircuit)."
    )
    p.add_argument("--m", type=int, required=True, help="target m (try 4 first)")
    p.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="artifact output directory (solution.json, verify.json, solver_stats.json)",
    )
    p.add_argument("--time-limit-sec", type=float, default=60.0)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--num-workers", type=int, default=8)
    p.add_argument(
        "--no-symmetry-break-vertex0",
        action="store_true",
        help="disable cycle-label symmetry breaking at vertex 000",
    )
    args = p.parse_args(argv)

    if args.m <= 2:
        raise SystemExit("m must be > 2")

    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    status, decomp, verify, stats = _solve_cpsat_even_m(
        m=args.m,
        time_limit_sec=args.time_limit_sec,
        seed=args.seed,
        num_workers=args.num_workers,
        symmetry_break_vertex0=(not args.no_symmetry_break_vertex0),
    )

    (out_dir / "solver_stats.json").write_text(
        json.dumps(stats, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    if decomp is None or verify is None:
        print(stats["outcome"])
        return 1

    payload: dict[str, Any] = {
        "m": decomp.m,
        "family": "cpsat",
        "params": {
            "time_limit_sec": float(args.time_limit_sec),
            "seed": int(args.seed),
            "num_workers": int(args.num_workers),
            "symmetry_breaking": {"vertex0_cycle_labels": (not args.no_symmetry_break_vertex0)},
            "solver_status_name": stats["status_name"],
            "solver_outcome": stats["outcome"],
        },
        "cycles": [{"dirs": list(c)} for c in decomp.cycle_dirs],
    }
    (out_dir / "solution.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out_dir / "verify.json").write_text(
        json.dumps(asdict(verify), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    if verify.ok:
        print("HIT")
        return 0
    print("HIT_BUT_VERIFY_FAIL")
    return 2


if __name__ == "__main__":
    raise SystemExit(_cli())

