from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence

from .constructions import CyclicShiftLinearMod3, iter_cyclic_shift_linear_mod3_params
from .csp import solve_csp
from .verify import verify_decomposition


@dataclass(frozen=True)
class SearchHit:
    m: int
    family: str
    params: dict[str, Any]


def _cli(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Search for small-m decompositions.")
    p.add_argument("--m", type=int, required=True, help="m > 2")
    p.add_argument(
        "--family",
        choices=["cyclic-shift-linear-mod3", "csp"],
        default="csp",
        help="construction family to search",
    )
    p.add_argument(
        "--max-nodes",
        type=int,
        default=2_000_000,
        help="(csp) backtracking node budget",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=None,
        help="optional JSON output path for first hit",
    )
    args = p.parse_args(argv)

    if args.m <= 2:
        raise SystemExit("m must be > 2")

    if args.family == "csp":
        run = solve_csp(args.m, max_solutions=1, max_nodes=args.max_nodes)
        if not run.solutions:
            print("NO_HIT")
            return 1
        decomp = run.solutions[0]
        res = verify_decomposition(decomp)
        if not res.ok:
            raise SystemExit("internal error: CSP solver returned invalid decomposition")
        payload: dict[str, Any] = {
            "m": decomp.m,
            "family": "csp",
            "params": {"max_nodes": args.max_nodes, "stats": asdict(run.stats)},
            "cycles": [{"dirs": list(c)} for c in decomp.cycle_dirs],
        }
        print("HIT", json.dumps({"m": decomp.m, "family": "csp"}, sort_keys=True))
        if args.out is not None:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
        return 0

    if args.family == "cyclic-shift-linear-mod3":
        for spec in iter_cyclic_shift_linear_mod3_params():
            decomp = spec.build(args.m)
            res = verify_decomposition(decomp)
            if res.ok:
                hit = SearchHit(
                    m=args.m,
                    family=args.family,
                    params={"a": spec.a, "b": spec.b, "c": spec.c, "offset": spec.offset},
                )
                payload = {
                    "m": decomp.m,
                    "family": args.family,
                    "params": asdict(hit)["params"],
                    "cycles": [{"dirs": list(c)} for c in decomp.cycle_dirs],
                }
                print("HIT", json.dumps(asdict(hit), sort_keys=True))
                if args.out is not None:
                    args.out.parent.mkdir(parents=True, exist_ok=True)
                    args.out.write_text(
                        json.dumps(payload, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8",
                    )
                return 0
        print("NO_HIT")
        return 1

    raise SystemExit(f"unhandled family: {args.family}")


if __name__ == "__main__":
    raise SystemExit(_cli())
