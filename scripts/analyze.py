#!/usr/bin/env python3
"""
Analyze decomposition solutions to identify patterns in direction assignments.

For each solved m, loads the decomposition and examines:
- Direction function structure (what determines which direction each cycle uses)
- Diagonal properties (x+y+k mod m)
- Symmetry properties (coordinate permutation, translation)
- Direction count distributions
"""

import json
import sys
from collections import Counter, defaultdict
from itertools import product

from verify import (
    all_vertices,
    cycles_to_direction_function,
    load_decomposition,
    next_vertex,
    vertex_index,
)


def analyze_direction_function(m, dfunc):
    """Analyze patterns in the direction assignment."""
    print(f"\n=== Direction Function Analysis for m={m} ===")

    # Count direction assignments per cycle
    for c in range(3):
        counts = Counter(dfunc[v][c] for v in dfunc)
        print(f"Cycle {c} direction counts: {dict(sorted(counts.items()))}")

    # Analyze by diagonal s = (x+y+k) mod m
    print(f"\nBy diagonal s = (x+y+k) mod m:")
    for s in range(m):
        verts_on_diag = [v for v in dfunc if (v[0] + v[1] + v[2]) % m == s]
        perm_counts = Counter()
        for v in verts_on_diag:
            perm = tuple(dfunc[v])
            perm_counts[perm] += 1
        print(f"  s={s}: {len(verts_on_diag)} vertices, permutations: {dict(perm_counts)}")

    # Check if direction depends on a simple function
    # Try: does cycle c's direction depend on (x+y+k) mod m and one coordinate?
    print(f"\nPermutation patterns by (s, x mod m):")
    for s in range(min(m, 5)):  # Limit output
        for x in range(min(m, 5)):
            verts = [v for v in dfunc if (v[0]+v[1]+v[2]) % m == s and v[0] == x]
            if verts:
                perms = Counter(tuple(dfunc[v]) for v in verts)
                if len(perms) <= 3:
                    print(f"  s={s}, x={x}: {dict(perms)}")

    # Check translation invariance along each axis
    print(f"\nTranslation invariance check:")
    for axis in range(3):
        invariant = True
        for v in all_vertices(m):
            # Compare with v shifted by 1 along axis
            w = list(v)
            w[axis] = (w[axis] + 1) % m
            w = tuple(w)
            if dfunc[v] != dfunc[w]:
                invariant = False
                break
        print(f"  Along axis {axis}: {'invariant' if invariant else 'NOT invariant'}")

    # Check if permutation at v depends only on (x+y+k) mod m
    print(f"\nDoes permutation depend only on s = (x+y+k) mod m?")
    by_diagonal = defaultdict(set)
    for v in dfunc:
        s = (v[0] + v[1] + v[2]) % m
        by_diagonal[s].add(tuple(dfunc[v]))
    all_uniform = True
    for s in sorted(by_diagonal):
        uniform = len(by_diagonal[s]) == 1
        if not uniform:
            all_uniform = False
        print(f"  s={s}: {'uniform' if uniform else 'mixed'} ({by_diagonal[s]})")

    return by_diagonal


def analyze_cycle_structure(m, cycles):
    """Analyze structural properties of each cycle."""
    print(f"\n=== Cycle Structure Analysis for m={m} ===")

    for c, cyc in enumerate(cycles):
        # Direction sequence
        dirs = []
        for i in range(len(cyc)):
            v = cyc[i]
            w = cyc[(i + 1) % len(cyc)]
            for d in range(3):
                if next_vertex(m, v, d) == w:
                    dirs.append(d)
                    break

        # Run-length encoding of direction sequence
        runs = []
        current_dir = dirs[0]
        current_len = 1
        for d in dirs[1:]:
            if d == current_dir:
                current_len += 1
            else:
                runs.append((current_dir, current_len))
                current_dir = d
                current_len = 1
        runs.append((current_dir, current_len))

        # Check if last run merges with first (cycle)
        if runs[0][0] == runs[-1][0]:
            merged_len = runs[0][1] + runs[-1][1]
            runs = [(runs[0][0], merged_len)] + runs[1:-1]

        run_lens = Counter(r[1] for r in runs)
        print(f"\nCycle {c}: {len(runs)} runs")
        print(f"  Run length distribution: {dict(sorted(run_lens.items()))}")

        # Show first few runs
        print(f"  First 20 runs: {runs[:20]}")


def analyze_file(filepath):
    """Load and analyze a decomposition file."""
    m, cycles = load_decomposition(filepath)
    dfunc = cycles_to_direction_function(m, cycles)
    analyze_direction_function(m, dfunc)
    analyze_cycle_structure(m, cycles)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze.py <decomposition.json> [decomposition2.json ...]")
        sys.exit(1)

    for filepath in sys.argv[1:]:
        analyze_file(filepath)
