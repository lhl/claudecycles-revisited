from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from claudescycles.constructions import construct_decomposition_odd_m
from claudescycles.io import save_decomposition
from claudescycles.verify import verify_decomposition


def _default_out_path(m: int) -> Path:
    return Path("artifacts") / "solutions" / "odd_m" / f"m{m}.json"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Generate the explicit odd-m decomposition.")
    ap.add_argument("m", type=int, help="Odd modulus m >= 5")
    ap.add_argument("--out", type=Path, default=None, help="Output JSON path")
    args = ap.parse_args(argv)

    out_path = args.out or _default_out_path(args.m)
    decomp = construct_decomposition_odd_m(args.m)
    report = verify_decomposition(args.m, decomp.dirs)
    if not report.ok:
        print(f"FAIL: constructed decomposition did not verify: {report.error}", file=sys.stderr)
        return 2

    save_decomposition(out_path, decomp)
    print(f"PASS: generated verified odd-m decomposition for m={args.m}; saved {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

