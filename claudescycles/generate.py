from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence

from .claude import claude_decomposition
from .verify import verify_decomposition


@dataclass(frozen=True)
class GeneratedDecomposition:
    m: int
    family: str
    params: dict[str, Any]
    cycles: list[dict[str, list[int]]]


def _cli(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Generate a decomposition JSON for G_m.")
    p.add_argument("--m", type=int, required=True)
    p.add_argument("--family", choices=["claude"], default="claude")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--verify", action="store_true", help="run verifier after generating")
    p.add_argument("--verify-json-out", type=Path, default=None)
    args = p.parse_args(argv)

    if args.m <= 2:
        raise SystemExit("m must be > 2")

    if args.family == "claude":
        decomp = claude_decomposition(args.m)
        payload = GeneratedDecomposition(
            m=decomp.m,
            family="claude",
            params={},
            cycles=[{"dirs": list(c)} for c in decomp.cycle_dirs],
        )
    else:
        raise SystemExit(f"unhandled family: {args.family}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(asdict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.verify:
        res = verify_decomposition(decomp)
        if args.verify_json_out is not None:
            args.verify_json_out.parent.mkdir(parents=True, exist_ok=True)
            args.verify_json_out.write_text(
                json.dumps(asdict(res), indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
        if res.ok:
            print(f"OK: m={decomp.m}")
            return 0
        print(f"FAIL: m={decomp.m}")
        for e in res.errors:
            print(f"- {e}")
        return 2

    print(f"WROTE: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())

