from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence

from .claude import claude_decomposition
from .verify import VerifyResult, verify_decomposition


@dataclass(frozen=True)
class ScanRow:
    m: int
    ok: bool
    elapsed_sec: float
    errors: list[str]


@dataclass(frozen=True)
class ScanResult:
    family: str
    params: dict[str, Any]
    rows: list[ScanRow]


def _cli(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Validate a construction over an m range.")
    p.add_argument("--family", choices=["claude"], default="claude")
    p.add_argument("--m-min", type=int, required=True)
    p.add_argument("--m-max", type=int, required=True)
    p.add_argument("--step", type=int, default=1)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)

    if args.m_min <= 2:
        raise SystemExit("m-min must be > 2")
    if args.m_max < args.m_min:
        raise SystemExit("m-max must be >= m-min")
    if args.step <= 0:
        raise SystemExit("step must be positive")

    rows: list[ScanRow] = []
    for m in range(args.m_min, args.m_max + 1, args.step):
        t0 = time.perf_counter()
        if args.family == "claude":
            decomp = claude_decomposition(m)
        else:
            raise SystemExit(f"unhandled family: {args.family}")
        res: VerifyResult = verify_decomposition(decomp)
        elapsed = time.perf_counter() - t0
        rows.append(ScanRow(m=m, ok=res.ok, elapsed_sec=elapsed, errors=res.errors))

    result = ScanResult(family=args.family, params={"m_min": args.m_min, "m_max": args.m_max, "step": args.step}, rows=rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(asdict(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    all_ok = all(r.ok for r in rows)
    print("OK" if all_ok else "FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(_cli())

