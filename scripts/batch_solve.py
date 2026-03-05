#!/usr/bin/env python3
"""Batch solver: solve and verify for a range of m values. Produce summary."""

import json
import sys
import time

from verify import save_decomposition, verify_decomposition, print_decomposition_stats
from solve import solve_decomposition


def batch_solve(m_min, m_max, time_limit=120, output_dir="artifacts"):
    results = []
    for m in range(m_min, m_max + 1):
        if m < 2:
            continue
        print(f"\nm={m}: ", end="", flush=True)
        cycles, stats = solve_decomposition(m, time_limit=time_limit, log=False)
        if cycles:
            ok, msg = verify_decomposition(m, cycles)
            stats["verified"] = ok
            if ok:
                save_decomposition(f"{output_dir}/decomposition_m{m}.json", m, cycles)
                # Direction counts
                for c_idx, cyc in enumerate(cycles):
                    n = len(cyc)
                    from verify import next_vertex
                    dir_counts = [0, 0, 0]
                    for i in range(n):
                        v = cyc[i]
                        w = cyc[(i + 1) % n]
                        for d in range(3):
                            if next_vertex(m, v, d) == w:
                                dir_counts[d] += 1
                                break
                    stats[f"cycle_{c_idx}_dirs"] = dir_counts
            print(f"{'PASS' if ok else 'FAIL'} ({stats['time_seconds']}s)", end="")
        else:
            stats["verified"] = False
            print(f"NOSOL ({stats['time_seconds']}s)", end="")
        results.append(stats)

    # Save summary
    summary_path = f"{output_dir}/batch_summary.json"
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n\n{'='*60}")
    print(f"Summary: {m_min} <= m <= {m_max}")
    print(f"{'='*60}")
    solved = [r for r in results if r.get("verified")]
    failed = [r for r in results if not r.get("verified") and r["status"] in ("OPTIMAL", "FEASIBLE")]
    nosol = [r for r in results if r["status"] == "INFEASIBLE"]
    timeout = [r for r in results if r["status"] not in ("OPTIMAL", "FEASIBLE", "INFEASIBLE")]
    print(f"Solved & verified: {len(solved)} (m = {[r['m'] for r in solved]})")
    if nosol:
        print(f"Proven infeasible: {len(nosol)} (m = {[r['m'] for r in nosol]})")
    if timeout:
        print(f"Timeout/unknown: {len(timeout)} (m = {[r['m'] for r in timeout]})")

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--min", type=int, default=2)
    parser.add_argument("--max", type=int, default=30)
    parser.add_argument("--time-limit", type=int, default=120)
    args = parser.parse_args()
    batch_solve(args.min, args.max, args.time_limit)
