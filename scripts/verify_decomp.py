from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from claudescycles.io import load_decomposition
from claudescycles.verify import verify_decomposition


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Verify a 3-cycle arc decomposition of G_m.")
    ap.add_argument("path", help="Path to decomposition JSON (see artifacts/*.json)")
    ap.add_argument("--json", action="store_true", help="Emit machine-readable JSON report")
    args = ap.parse_args(argv)

    decomp = load_decomposition(args.path)
    report = verify_decomposition(decomp.m, decomp.dirs)

    if args.json:
        print(
            json.dumps(
                {
                    "ok": report.ok,
                    "m": report.m,
                    "n_vertices": report.n_vertices,
                    "arc_partition_ok": report.arc_partition_ok,
                    "arc_partition_violations": report.arc_partition_violations,
                    "cycle_checks": [
                        {
                            "cycle_index": cc.cycle_index,
                            "ok": cc.ok,
                            "error": cc.error,
                        }
                        for cc in report.cycle_checks
                    ],
                    "error": report.error,
                    "meta": decomp.meta,
                },
                indent=2,
                sort_keys=True,
            )
        )
    elif report.ok:
        print(
            f"PASS: m={report.m}, n={report.n_vertices}; "
            f"arc_partition_ok={report.arc_partition_ok}; "
            f"cycles_ok={all(cc.ok for cc in report.cycle_checks)}"
        )
    else:
        print(f"FAIL: {report.error}", file=sys.stderr)
        for cc in report.cycle_checks:
            if not cc.ok:
                print(f"  cycle {cc.cycle_index}: {cc.error}", file=sys.stderr)
        if not report.arc_partition_ok:
            print(
                f"  arc partition violations: "
                f"{report.arc_partition_violations}/{report.n_vertices}",
                file=sys.stderr,
            )

    return 0 if report.ok else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

