from __future__ import annotations

import argparse
import json
import time
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from claudescycles.constructions import construct_decomposition_odd_m
from claudescycles.verify import verify_decomposition


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="Validate the odd-m construction over a range of m."
    )
    ap.add_argument(
        "--m-max", type=int, default=101, help="Validate all odd m in [5, m-max]"
    )
    ap.add_argument(
        "--m-values",
        type=int,
        nargs="*",
        default=None,
        help="Explicit list of odd m values (overrides --m-max)",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts") / "validation" / "odd_construction_validation.json",
        help="Output JSON summary path",
    )
    args = ap.parse_args(argv)

    if args.m_values is None or len(args.m_values) == 0:
        ms = [m for m in range(5, args.m_max + 1) if m % 2 == 1]
    else:
        ms = list(args.m_values)

    results = []
    all_ok = True
    for m in ms:
        if m % 2 == 0 or m < 5:
            results.append({"m": m, "ok": False, "error": "requires odd m >= 5"})
            all_ok = False
            continue

        t0 = time.time()
        decomp = construct_decomposition_odd_m(m)
        report = verify_decomposition(m, decomp.dirs)
        dt = time.time() - t0

        item = {
            "m": m,
            "ok": report.ok,
            "error": report.error,
            "A": decomp.meta.get("A"),
            "seconds": dt,
        }
        results.append(item)
        if not report.ok:
            all_ok = False

    args.out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generator": "scripts/validate_construction_odd.py",
        "argv": argv,
        "all_ok": all_ok,
        "results": results,
    }
    args.out.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    if all_ok:
        print(f"PASS: validated {len(results)} m values; wrote {args.out}")
        return 0

    print(f"FAIL: wrote partial results to {args.out}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

