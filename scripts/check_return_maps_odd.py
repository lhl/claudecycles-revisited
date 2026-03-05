from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from claudescycles.constructions import _choose_a_odd_m


def _cycle_direction(cycle_index: int, a: int, v: int, w: int) -> int:
    if w == 0:
        if cycle_index == 0:
            return 2
        if cycle_index == 1:
            return 1 if v == 0 else 0
        return 0 if v == 0 else 1

    if w == 1:
        if cycle_index == 1:
            return 2
        if cycle_index == 0:
            return 1 if v == 0 else 0
        return 0 if v == 0 else 1

    if cycle_index == 2:
        return 2

    if 2 <= w <= a + 1:
        if cycle_index == 0:
            return 1 if v == 0 else 0
        return 0 if v == 0 else 1

    if cycle_index == 0:
        return 0 if v == 0 else 1
    return 1 if v == 0 else 0


def _step(m: int, cycle_index: int, a: int, u: int, v: int, w: int) -> tuple[int, int, int]:
    d = _cycle_direction(cycle_index, a, v, w)
    if d == 0:
        return (u + 1) % m, (v + 1) % m, (w + 1) % m
    if d == 1:
        return u, (v + 1) % m, (w + 1) % m
    return u, v, (w + 1) % m


def _delta0(m: int, a: int, v: int) -> int:
    if v == 1:
        return a + 1
    if v == 0 or v >= m - a:
        return a
    return a + 2


def _delta1(m: int, a: int, v: int) -> int:
    if v == 1:
        return m - a - 1
    if v >= m - a:
        return m - a
    return m - a - 2


def _delta2(m: int, v: int) -> int:
    return 1 if v in (0, m - 1) else 0


def _check_one_m(m: int) -> dict[str, object]:
    a = _choose_a_odd_m(m)
    formulas_ok = True
    details: list[dict[str, object]] = []

    for cycle_index in range(3):
        v_deltas_ok = True
        u_deltas_ok = True
        cycle_rows: list[dict[str, int]] = []
        total_u_shift = 0

        for start_v in range(m):
            u, v, w = 0, start_v, 0
            for _ in range(m):
                u, v, w = _step(m, cycle_index, a, u, v, w)
            if w != 0:
                raise AssertionError("return map did not return to w=0")

            expected_v = (start_v + 2) % m if cycle_index == 2 else (start_v - 1) % m
            if cycle_index == 0:
                expected_u = _delta0(m, a, start_v) % m
            elif cycle_index == 1:
                expected_u = _delta1(m, a, start_v) % m
            else:
                expected_u = _delta2(m, start_v) % m

            actual_u = u % m
            actual_v = v % m
            v_deltas_ok &= actual_v == expected_v
            u_deltas_ok &= actual_u == expected_u
            total_u_shift = (total_u_shift + actual_u) % m
            cycle_rows.append(
                {
                    "start_v": start_v,
                    "actual_u_delta": actual_u,
                    "expected_u_delta": expected_u,
                    "actual_v_after": actual_v,
                    "expected_v_after": expected_v,
                }
            )

        expected_total = {
            0: (-2 * a - 3) % m,
            1: (2 * a + 1) % m,
            2: 2 % m,
        }[cycle_index]
        totals_ok = total_u_shift == expected_total
        cycle_ok = v_deltas_ok and u_deltas_ok and totals_ok
        formulas_ok &= cycle_ok
        details.append(
            {
                "cycle_index": cycle_index,
                "ok": cycle_ok,
                "v_deltas_ok": v_deltas_ok,
                "u_deltas_ok": u_deltas_ok,
                "total_u_shift_mod_m": total_u_shift,
                "expected_total_u_shift_mod_m": expected_total,
                "rows": cycle_rows,
            }
        )

    return {"m": m, "A": a, "ok": formulas_ok, "cycles": details}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Check the odd-m return-map formulas used in the proof.")
    ap.add_argument("--m-values", type=int, nargs="*", default=None, help="Explicit odd m values to test")
    ap.add_argument("--m-min", type=int, default=5, help="Inclusive start when --m-values is omitted")
    ap.add_argument("--m-max", type=int, default=31, help="Inclusive end when --m-values is omitted")
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts") / "validation" / "odd_return_map_checks.json",
        help="Output JSON path",
    )
    args = ap.parse_args(argv)

    ms = list(args.m_values) if args.m_values is not None else [m for m in range(args.m_min, args.m_max + 1) if m % 2 == 1]
    results = [_check_one_m(m) for m in ms]
    all_ok = all(item["ok"] for item in results)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generator": "scripts/check_return_maps_odd.py",
        "argv": argv,
        "all_ok": all_ok,
        "results": results,
    }
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if all_ok:
        print(f"PASS: checked return-map formulas for {len(results)} odd m values; wrote {args.out}")
        return 0

    print(f"FAIL: wrote partial results to {args.out}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
