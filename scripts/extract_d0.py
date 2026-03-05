#!/usr/bin/env python3
"""
Extract and analyze the d_0 function from cyclically-symmetric solutions.

With cyclic symmetry, the full direction function is determined by d_0 alone.
d_0 maps Z_m^3 -> {0,1,2} and the full permutation at (x,y,z) is:
  cycle 0: d_0(x,y,z)
  cycle 1: (d_0(y,z,x) + 1) mod 3
  cycle 2: (d_0(z,x,y) + 2) mod 3

We analyze d_0 in the projected (u,v) = (x-z, y-z) coordinates
and check for patterns.
"""

import sys
from collections import Counter, defaultdict
from itertools import product

from deep_analyze import find_solution_with_structure
from verify import all_vertices, next_vertex, verify_decomposition, save_decomposition


def extract_d0(m, dfunc):
    """Extract d_0(x,y,z) for all vertices."""
    d0 = {}
    for v in all_vertices(m):
        d0[v] = dfunc[v][0]
    return d0


def d0_in_uv(m, d0):
    """
    Analyze d_0 in (u,v) = (x-z, y-z) mod m coordinates.
    Since d_0 may not depend only on (u,v), report the full picture.
    """
    by_uv = defaultdict(list)
    for (x, y, z), d in d0.items():
        u = (x - z) % m
        v = (y - z) % m
        by_uv[(u, v)].append((z, d))

    print(f"\nd_0 by (u, v) = (x-z, y-z) mod {m}:")
    depends_on_uv = True
    grid = {}
    for u in range(m):
        for v in range(m):
            entries = by_uv[(u, v)]
            dirs = set(d for _, d in entries)
            if len(dirs) == 1:
                d = list(dirs)[0]
                grid[(u, v)] = d
            else:
                depends_on_uv = False
                grid[(u, v)] = entries

    if depends_on_uv:
        print("d_0 DOES depend only on (u,v)!")
        print("Grid (rows=v, cols=u):")
        for v in range(m):
            row = "  "
            for u in range(m):
                row += str(grid[(u, v)]) + " "
            print(row)

        # Analyze the grid
        analyze_grid(m, {k: v for k, v in grid.items()})
    else:
        print("d_0 does NOT depend only on (u,v)")
        # Show z-dependence
        for u in range(m):
            for v in range(m):
                entries = by_uv[(u, v)]
                z_to_d = {z: d for z, d in entries}
                if len(set(z_to_d.values())) > 1:
                    print(f"  (u={u},v={v}): z->d = {z_to_d}")

    return depends_on_uv, grid


def analyze_grid(m, grid):
    """Analyze an m x m grid of {0,1,2} values."""
    print(f"\nGrid analysis:")

    # Count each direction
    counts = Counter(grid.values())
    print(f"  Direction counts: {dict(sorted(counts.items()))}")

    # Check if value depends on u+v mod m
    by_sum = defaultdict(set)
    for (u, v), d in grid.items():
        by_sum[(u + v) % m].add(d)
    sum_dep = all(len(s) == 1 for s in by_sum.values())
    print(f"  Depends on u+v mod {m}: {sum_dep}")

    # Check if value depends on u-v mod m
    by_diff = defaultdict(set)
    for (u, v), d in grid.items():
        by_diff[(u - v) % m].add(d)
    diff_dep = all(len(s) == 1 for s in by_diff.values())
    print(f"  Depends on u-v mod {m}: {diff_dep}")

    # Check all linear combinations au+bv mod m
    for a in range(m):
        for b in range(m):
            if a == 0 and b == 0:
                continue
            by_lin = defaultdict(set)
            for (u, v), d in grid.items():
                by_lin[(a * u + b * v) % m].add(d)
            if all(len(s) == 1 for s in by_lin.values()):
                print(f"  Depends on {a}u+{b}v mod {m}: " +
                      str({k: list(v)[0] for k, v in sorted(by_lin.items())}))

    # Check φ-invariance: φ(u,v) = (v-u, -u) mod m
    phi = lambda u, v: ((v - u) % m, (-u) % m)
    phi_inv = all(grid[(u, v)] == grid[phi(u, v)] for u in range(m) for v in range(m))
    print(f"  φ-invariant (φ(u,v)=(v-u,-u)): {phi_inv}")

    # Check which (u,v) have d=2 (the "z-step" direction)
    d2_positions = [(u, v) for (u, v), d in grid.items() if d == 2]
    print(f"  d=2 positions: {d2_positions}")
    print(f"  d=2 count: {len(d2_positions)} (need coprime to {m})")

    # Check the step sequence trace
    print(f"\n  Tracing the (u,v) functional graph:")
    step_map = {0: (1, 0), 1: (0, 1), 2: (-1, -1)}
    pos = (0, 0)
    visited = []
    for i in range(m * m + 1):
        if pos in [p for p in visited]:
            cycle_start = visited.index(pos)
            print(f"  Cycle length: {i - cycle_start} (starts at step {cycle_start})")
            break
        visited.append(pos)
        d = grid[pos]
        s = step_map[d]
        pos = ((pos[0] + s[0]) % m, (pos[1] + s[1]) % m)
    else:
        print(f"  Full Hamiltonian cycle of length {m*m}")


def solve_and_extract(m):
    """Find structured solution and extract d_0."""
    print(f"\n{'='*60}")
    print(f"m = {m}")
    print(f"{'='*60}")

    dfunc = find_solution_with_structure(m)
    if dfunc is None:
        print("No structured solution found!")
        return None

    # Verify
    n = m ** 3
    cycles = []
    for c in range(3):
        path = []
        v = (0, 0, 0)
        for _ in range(n):
            path.append(v)
            d = dfunc[v][c]
            v = next_vertex(m, v, d)
        cycles.append(path)
    ok, msg = verify_decomposition(m, cycles)
    print(f"Verification: {msg}")

    if not ok:
        return None

    # Direction counts
    for c in range(3):
        dirs = [dfunc[v][c] for v in all_vertices(m)]
        counts = Counter(dirs)
        print(f"Cycle {c}: {dict(sorted(counts.items()))}")

    d0 = extract_d0(m, dfunc)
    depends, grid = d0_in_uv(m, d0)

    save_decomposition(f"artifacts/structured_m{m}.json", m, cycles)
    return grid


if __name__ == "__main__":
    m_values = [3, 5, 7, 9, 4, 6, 8]
    if len(sys.argv) > 1:
        m_values = [int(x) for x in sys.argv[1:]]

    for m in m_values:
        solve_and_extract(m)
