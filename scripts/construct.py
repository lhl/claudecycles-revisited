#!/usr/bin/env python3
"""
Attempt algebraic constructions for G_m decomposition into 3 Hamiltonian cycles.

Strategy: define a direction function d(v, c) for each vertex v and cycle c,
then verify each cycle is Hamiltonian by tracing.

A direction function assigns a permutation of {0,1,2} at each vertex.
"""

import json
import sys
from collections import Counter
from itertools import product

from verify import (
    all_vertices,
    direction_function_to_cycles,
    next_vertex,
    save_decomposition,
    verify_decomposition,
    print_decomposition_stats,
)


def trace_cycle(m, dfunc, cycle_idx, start=(0, 0, 0)):
    """Trace a single cycle and return (vertices, is_hamiltonian)."""
    n = m ** 3
    visited = []
    v = start
    seen = set()
    for _ in range(n):
        if v in seen:
            return visited, False
        seen.add(v)
        visited.append(v)
        d = dfunc[v][cycle_idx]
        v = next_vertex(m, v, d)
    return visited, (v == start and len(seen) == n)


def check_construction(m, dfunc):
    """Check if a direction function gives valid decomposition. Returns (ok, info)."""
    n = m ** 3
    # Check permutation property
    for v in all_vertices(m):
        dirs = dfunc[v]
        if sorted(dirs) != [0, 1, 2]:
            return False, f"Not a permutation at {v}: {dirs}"

    # Check each cycle
    cycle_lengths = []
    for c in range(3):
        visited, ham = trace_cycle(m, dfunc, c)
        if not ham:
            cycle_lengths.append(len(visited))
        else:
            cycle_lengths.append(n)

    if all(l == n for l in cycle_lengths):
        return True, f"All 3 cycles Hamiltonian (length {n})"
    else:
        return False, f"Cycle lengths: {cycle_lengths} (need {n})"


def construction_serpentine_shifted(m):
    """
    Serpentine construction with shifted diagonals for each cycle.

    Cycle c uses direction c as primary (off-diagonal).
    On the diagonal s = (x+y+z) mod m == m-1, cycles deviate.
    The deviation depends on which coordinate triggers the turn.
    """
    dfunc = {}
    for v in all_vertices(m):
        x, y, z = v
        s = (x + y + z) % m
        if s != m - 1:
            dfunc[v] = [0, 1, 2]  # identity permutation
        else:
            # On the special diagonal, use derangement
            # Cycle 0: if x == 0 -> dir 2, else -> dir 1
            # Cycle 1: if y == 0 -> dir 0, else -> dir 2
            # Cycle 2: if z == 0 -> dir 1, else -> dir 0
            d0 = 2 if x == 0 else 1
            d1 = 0 if y == 0 else 2
            d2 = 1 if z == 0 else 0
            dfunc[v] = [d0, d1, d2]
    return dfunc


def construction_multi_diagonal(m):
    """
    Use multiple diagonals - each cycle has its own turning diagonal.

    Cycle 0: turns on diagonal s = 0
    Cycle 1: turns on diagonal s = 1  (or floor(m/3))
    Cycle 2: turns on diagonal s = 2  (or 2*floor(m/3))

    On non-turning diagonals for a cycle, use primary direction.
    On turning diagonal, swap to secondary directions.
    """
    # This approach: each cycle c has diagonal d_c where it deviates
    # Choose diagonals to be different
    diags = [0, m // 3, 2 * (m // 3)]
    if m % 3 != 0:
        diags = [0, 1, 2]

    dfunc = {}
    for v in all_vertices(m):
        x, y, z = v
        s = (x + y + z) % m
        dirs = [None, None, None]

        for c in range(3):
            if s != diags[c]:
                dirs[c] = c  # primary direction

        # Fill in the deviations ensuring permutation
        # This is tricky - the primary directions at non-turning vertices
        # might conflict with needed deviations
        # Actually if all 3 diags are different, at most one cycle deviates per vertex

        if s not in diags:
            # No cycle deviates here
            dfunc[v] = [0, 1, 2]
        elif s == diags[0] and s != diags[1] and s != diags[2]:
            # Only cycle 0 deviates
            # Cycles 1, 2 use dirs 1, 2
            # Cycle 0 must use... but 1 and 2 are taken!
            # This doesn't work - cycle 0 can't use dir 0 (it deviates)
            # and dirs 1, 2 are used by cycles 1, 2
            # So cycle 0 has no direction available. FAIL.
            dfunc[v] = [0, 1, 2]  # placeholder
        else:
            dfunc[v] = [0, 1, 2]  # placeholder

    return dfunc


def construction_gray_code(m):
    """
    Build 3 Hamiltonian cycles directly using generalized Gray code approach.

    Cycle 0: sweep x within y-rows within z-slices (x-primary serpentine)
    Cycle 1: sweep y within z-rows within x-slices (y-primary serpentine)
    Cycle 2: sweep z within x-rows within y-slices (z-primary serpentine)

    Each cycle is built independently, then we check arc-disjointness.
    """
    cycles = []

    for primary in range(3):  # primary sweep direction
        sec = (primary + 1) % 3   # secondary (row change)
        ter = (primary + 2) % 3   # tertiary (slice change)

        # Build path through all vertices
        path = []
        # Start at origin
        pos = [0, 0, 0]

        for slice_idx in range(m):
            for row_idx in range(m):
                for step in range(m):
                    path.append(tuple(pos))
                    if step < m - 1:
                        # Step in primary direction
                        pos[primary] = (pos[primary] + 1) % m
                    elif row_idx < m - 1:
                        # Step in secondary direction
                        pos[sec] = (pos[sec] + 1) % m
                    elif slice_idx < m - 1:
                        # Step in tertiary direction
                        pos[ter] = (pos[ter] + 1) % m
                    # else: last vertex, will close cycle

        cycles.append(path)

    return cycles


def construction_interleaved(m):
    """
    Interleaved construction: at vertex (x,y,z), the direction for cycle c
    is determined by a formula involving the coordinates modulo m.

    Key idea: use (x+y+z) mod m and one coordinate to determine the permutation.
    """
    dfunc = {}
    for v in all_vertices(m):
        x, y, z = v
        s = (x + y + z) % m

        # Try: cycle c uses direction (c + s) mod 3 when s is not special
        # This ensures that as s varies, each cycle rotates through directions
        # But 3 and m may not be coprime...

        if m % 3 == 0:
            # Partition s values into 3 groups
            group = s % 3
            d0 = (0 + group) % 3
            d1 = (1 + group) % 3
            d2 = (2 + group) % 3
        else:
            # s mod 3 cycles through all values as s goes 0..m-1
            group = s % 3
            d0 = (0 + group) % 3
            d1 = (1 + group) % 3
            d2 = (2 + group) % 3

        dfunc[v] = [d0, d1, d2]
    return dfunc


def construction_rotation(m):
    """
    Rotation construction: direction for cycle c at (x,y,z) = (c + f(x,y,z)) mod 3.

    Choose f such that each cycle forms a Hamiltonian cycle.
    Try f(x,y,z) = (x + y + z) mod 3 (when gcd(m,3) = 1).
    """
    dfunc = {}
    for v in all_vertices(m):
        x, y, z = v
        f = (x + y + z) % 3
        dfunc[v] = [(0 + f) % 3, (1 + f) % 3, (2 + f) % 3]
    return dfunc


def construction_two_level(m):
    """
    Two-level construction for odd m.

    Level 1: Within each z-slice, create a Hamiltonian path using dirs 0,1.
    Level 2: Connect slices using dir 2.

    The path within slice z starts at vertex (0, (-z) mod m, z) and ends at
    (0, (-z-1) mod m, z), using the serpentine pattern.

    At the end-of-slice vertex, step dir 2 to next slice.
    At end-of-row vertices within a slice, step dir 1.
    Everywhere else, step dir 0.

    This gives Cycle 0. Then construct Cycles 1, 2 by cyclic coordinate permutation,
    but with carefully chosen derangements at conflict vertices.
    """
    n = m ** 3

    # Build Cycle 0: x-primary serpentine through z-slices
    path0 = []
    for z in range(m):
        y_start = (-z) % m
        x_start = 0
        for row in range(m):
            y = (y_start + row) % m
            x = (x_start - row) % m
            for step in range(m - 1):
                path0.append((x, y, z))
                x = (x + 1) % m
            path0.append((x, y, z))
            # After m-1 steps in dir 0, we're at (x_start - row - 1, y, z)
            # Next: dir 1 (row change) or dir 2 (slice change)

    # Verify path0 length
    if len(path0) != n:
        return None

    # Build Cycle 1: y-primary serpentine through x-slices (cyclic permutation)
    path1 = []
    for x in range(m):
        z_start = (-x) % m
        y_start = 0
        for row in range(m):
            z = (z_start + row) % m
            y = (y_start - row) % m
            for step in range(m - 1):
                path1.append((x, y, z))
                y = (y + 1) % m
            path1.append((x, y, z))

    # Build Cycle 2: z-primary serpentine through y-slices
    path2 = []
    for y in range(m):
        x_start = (-y) % m
        z_start = 0
        for row in range(m):
            x = (x_start + row) % m
            z = (z_start - row) % m
            for step in range(m - 1):
                path2.append((x, y, z))
                z = (z + 1) % m
            path2.append((x, y, z))

    return [path0, path1, path2]


def test_construction(name, m, result):
    """Test a construction result (either dfunc dict or cycles list)."""
    if result is None:
        print(f"  {name}: construction returned None")
        return False

    if isinstance(result, dict):
        ok, info = check_construction(m, result)
        print(f"  {name}: {info}")
        if ok:
            cycles = direction_function_to_cycles(m, result)
            ok2, msg2 = verify_decomposition(m, cycles)
            print(f"    Verification: {msg2}")
            return ok2
        return False
    elif isinstance(result, list) and len(result) == 3:
        # Direct cycle construction - check if arcs are valid first
        for c, path in enumerate(result):
            if len(path) != m**3:
                print(f"  {name}: Cycle {c} wrong length {len(path)}")
                return False
            if len(set(path)) != m**3:
                print(f"  {name}: Cycle {c} has duplicates ({len(set(path))} unique)")
                return False

        # Check arcs valid
        for c, path in enumerate(result):
            for i in range(len(path)):
                v = path[i]
                w = path[(i+1) % len(path)]
                valid = any(next_vertex(m, v, d) == w for d in range(3))
                if not valid:
                    print(f"  {name}: Cycle {c} invalid arc {v}->{w} at step {i}")
                    return False

        # Check arc-disjoint
        ok, msg = verify_decomposition(m, result)
        print(f"  {name}: {msg}")
        return ok

    print(f"  {name}: unexpected result type")
    return False


def run_all_constructions(m_values):
    """Test all construction methods for given m values."""
    constructors = [
        ("serpentine_shifted", construction_serpentine_shifted),
        ("interleaved", construction_interleaved),
        ("rotation", construction_rotation),
        ("two_level", construction_two_level),
    ]

    results = {}
    for m in m_values:
        print(f"\n{'='*50}")
        print(f"m = {m} (n = {m**3})")
        print(f"{'='*50}")

        for name, constructor in constructors:
            try:
                result = constructor(m)
                success = test_construction(name, m, result)
                results[(m, name)] = success
            except Exception as e:
                print(f"  {name}: ERROR - {e}")
                results[(m, name)] = False

    # Summary
    print(f"\n{'='*50}")
    print("Summary")
    print(f"{'='*50}")
    for name, _ in constructors:
        successes = [m for m in m_values if results.get((m, name), False)]
        print(f"  {name}: works for m = {successes}")


if __name__ == "__main__":
    m_values = list(range(3, 12))
    if len(sys.argv) > 1:
        m_values = [int(x) for x in sys.argv[1:]]
    run_all_constructions(m_values)
