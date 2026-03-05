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
    return Path("artifacts") / "constructions" / f"odd_m{m}.json"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="Generate the explicit odd-m (>=5) decomposition construction."
    )
    ap.add_argument("m", type=int, help="odd modulus m (>=5)")
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="output path (default: artifacts/constructions/odd_m{m}.json)",
    )
    ap.add_argument(
        "--overwrite", action="store_true", help="overwrite output file if it exists"
    )
    ap.add_argument(
        "--no-verify", action="store_true", help="skip verifier check (not recommended)"
    )
    args = ap.parse_args(argv)

    out_path = args.out if args.out is not None else _default_out_path(args.m)
    if out_path.exists() and not args.overwrite:
        print(
            f"Refusing to overwrite existing file: {out_path} (use --overwrite)",
            file=sys.stderr,
        )
        return 2

    decomp = construct_decomposition_odd_m(args.m)
    if not args.no_verify:
        report = verify_decomposition(decomp.m, decomp.dirs)
        if not report.ok:
            print(
                f"Construction produced invalid decomposition: {report.error}",
                file=sys.stderr,
            )
            return 3

    save_decomposition(out_path, decomp)
    print(f"WROTE: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

