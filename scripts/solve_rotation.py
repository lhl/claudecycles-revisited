#!/usr/bin/env python3
"""
Rotation-based solver: find delta: Z_m^3 -> {0,1,2} such that
all three functional graphs (with directions (c + delta(v)) mod 3)
are Hamiltonian cycles.

This guarantees arc-disjointness automatically since at each vertex,
the 3 cycles use directions delta, (delta+1)%3, (delta+2)%3 = perm of {0,1,2}.

Much more efficient than the full solver since we only have m^3 variables
(delta per vertex) instead of 3*m^3 variables.
"""

import json
import sys
import time
from itertools import product

from ortools.sat.python import cp_model

from verify import (
    all_vertices,
    next_vertex,
    save_decomposition,
    verify_decomposition,
    print_decomposition_stats,
    vertex_index,
)


def solve_rotation(m, time_limit=300, num_workers=8, log=False):
    """Find delta such that all 3 rotated cycles are Hamiltonian."""
    n = m ** 3
    vertices = all_vertices(m)
    v2i = {v: vertex_index(m, *v) for v in vertices}

    model = cp_model.CpModel()

    # delta[v] in {0, 1, 2}
    delta = {v: model.new_int_var(0, 2, f"d_{v}") for v in vertices}

    # For each cycle c in {0,1,2}, the direction at v is (c + delta[v]) % 3
    # Add Hamiltonian circuit constraint for each cycle
    for c in range(3):
        arcs = []
        for v in vertices:
            vi = v2i[v]
            for d_val in range(3):
                # If delta[v] == d_val, then cycle c uses direction (c + d_val) % 3
                actual_dir = (c + d_val) % 3
                w = next_vertex(m, v, actual_dir)
                wi = v2i[w]
                b = model.new_bool_var(f"a_{c}_{v}_{d_val}")
                model.add(delta[v] == d_val).only_enforce_if(b)
                model.add(delta[v] != d_val).only_enforce_if(~b)
                arcs.append((vi, wi, b))
        model.add_circuit(arcs)

    # Symmetry breaking
    model.add(delta[(0, 0, 0)] == 0)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = num_workers
    if log:
        solver.parameters.log_search_progress = True

    t0 = time.time()
    status = solver.solve(model)
    elapsed = time.time() - t0

    stats = {
        "m": m,
        "status": solver.status_name(status),
        "time_seconds": round(elapsed, 3),
    }

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        delta_val = {v: solver.value(delta[v]) for v in vertices}

        # Build cycles
        cycles = []
        for c in range(3):
            path = []
            v = (0, 0, 0)
            for _ in range(n):
                path.append(v)
                d = (c + delta_val[v]) % 3
                v = next_vertex(m, v, d)
            cycles.append(path)

        stats["delta_counts"] = {
            i: sum(1 for v in vertices if delta_val[v] == i) for i in range(3)
        }

        return delta_val, cycles, stats
    return None, None, stats


def analyze_delta(m, delta_val):
    """Analyze the delta function for patterns."""
    from collections import Counter, defaultdict

    print(f"\nDelta analysis for m={m}:")
    counts = Counter(delta_val.values())
    print(f"  Value counts: {dict(sorted(counts.items()))}")

    # Check if delta depends on (x+y+z) mod m
    by_s = defaultdict(set)
    for v, d in delta_val.items():
        s = sum(v) % m
        by_s[s].add(d)
    s_dep = all(len(v) == 1 for v in by_s.values())
    print(f"  Depends only on s=(x+y+z)%{m}: {s_dep}")
    if s_dep:
        pattern = {s: list(v)[0] for s, v in sorted(by_s.items())}
        print(f"  Pattern: {pattern}")

    # Check if delta depends on (x+y+z) mod 3
    by_s3 = defaultdict(set)
    for v, d in delta_val.items():
        s = sum(v) % 3
        by_s3[s].add(d)
    s3_dep = all(len(v) == 1 for v in by_s3.values())
    print(f"  Depends only on (x+y+z)%3: {s3_dep}")
    if s3_dep:
        pattern = {s: list(v)[0] for s, v in sorted(by_s3.items())}
        print(f"  Pattern: {pattern}")

    # Check single-coordinate dependencies
    for coord in range(3):
        name = "xyz"[coord]
        by_c = defaultdict(set)
        for v, d in delta_val.items():
            by_c[v[coord]].add(d)
        if all(len(v) == 1 for v in by_c.values()):
            print(f"  Depends only on {name}: " +
                  str({k: list(v)[0] for k, v in sorted(by_c.items())}))

    # Check linear combinations mod 3
    for a in range(3):
        for b in range(3):
            for c in range(3):
                if a == b == c == 0:
                    continue
                by_lin = defaultdict(set)
                for v, d in delta_val.items():
                    val = (a * v[0] + b * v[1] + c * v[2]) % 3
                    by_lin[val].add(d)
                if all(len(v) == 1 for v in by_lin.values()):
                    pattern = {k: list(v)[0] for k, v in sorted(by_lin.items())}
                    print(f"  Depends on ({a}x+{b}y+{c}z)%3: {pattern}")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("m", type=int, nargs="*", default=[3, 5, 7])
    parser.add_argument("--time-limit", type=int, default=300)
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()

    for m in args.m:
        print(f"\n{'='*60}")
        print(f"Rotation solver for m={m}")
        print(f"{'='*60}")

        delta_val, cycles, stats = solve_rotation(m, time_limit=args.time_limit)
        print(f"Status: {stats['status']}, Time: {stats['time_seconds']}s")

        if cycles is not None:
            ok, msg = verify_decomposition(m, cycles)
            print(f"Verification: {msg}")
            if ok:
                print_decomposition_stats(m, cycles)
                print(f"Delta counts: {stats['delta_counts']}")
                analyze_delta(m, delta_val)

                if args.save:
                    save_decomposition(f"artifacts/rotation_m{m}.json", m, cycles)
        else:
            print("No rotation solution found!")


if __name__ == "__main__":
    main()
