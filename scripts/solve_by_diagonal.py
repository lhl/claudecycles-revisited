#!/usr/bin/env python3
"""
Solve for direction functions that depend only on s = (x+y+z) mod m.

At each vertex (x,y,z), the permutation of {0,1,2} for the 3 cycles
is determined solely by s = (x+y+z) mod m.

This gives 6^m possibilities (6 permutations of {0,1,2} for each of m diagonal classes).
We search for assignments where all 3 cycles are Hamiltonian.
"""

import sys
import time
from itertools import permutations, product

from verify import (
    all_vertices,
    next_vertex,
    verify_decomposition,
    save_decomposition,
    print_decomposition_stats,
)


ALL_PERMS = list(permutations([0, 1, 2]))  # 6 permutations


def make_dfunc(m, perm_assignment):
    """
    Build direction function from perm_assignment: list of m permutations,
    one per diagonal class s=0,...,m-1.
    """
    dfunc = {}
    for v in all_vertices(m):
        s = (v[0] + v[1] + v[2]) % m
        dfunc[v] = list(perm_assignment[s])
    return dfunc


def trace_cycle_fast(m, dfunc, cycle_idx):
    """Trace cycle and return length of orbit from (0,0,0)."""
    n = m ** 3
    v = (0, 0, 0)
    for i in range(n):
        d = dfunc[v][cycle_idx]
        v = next_vertex(m, v, d)
        if v == (0, 0, 0):
            return i + 1
    return n  # shouldn't reach here if cycle returns


def check_all_hamiltonian(m, perm_assignment):
    """Quick check: do all 3 cycles have length m^3?"""
    dfunc = make_dfunc(m, perm_assignment)
    n = m ** 3
    for c in range(3):
        length = trace_cycle_fast(m, dfunc, c)
        if length != n:
            return False
    return True


def brute_force_search(m, time_limit=300):
    """Enumerate all 6^m assignments and check each."""
    print(f"Brute force search for m={m}: {6**m} candidates")
    t0 = time.time()
    count = 0
    solutions = []

    for combo in product(ALL_PERMS, repeat=m):
        count += 1
        if count % 100000 == 0:
            elapsed = time.time() - t0
            if elapsed > time_limit:
                print(f"  Time limit reached after {count} candidates")
                break
            print(f"  Checked {count} candidates in {elapsed:.1f}s...")

        if check_all_hamiltonian(m, combo):
            solutions.append(combo)
            print(f"  FOUND solution #{len(solutions)} at candidate {count}")
            # Print the permutation assignment
            for s in range(m):
                print(f"    s={s}: perm={combo[s]}")

    elapsed = time.time() - t0
    print(f"Search complete: {count} candidates in {elapsed:.1f}s, {len(solutions)} solutions")
    return solutions


def smart_search(m, time_limit=300):
    """
    Search with pruning: check each cycle incrementally.
    If cycle 0 isn't Hamiltonian, skip.
    """
    print(f"Smart search for m={m}: {6**m} candidates")
    t0 = time.time()
    count = 0
    solutions = []

    for combo in product(ALL_PERMS, repeat=m):
        count += 1
        if count % 100000 == 0:
            elapsed = time.time() - t0
            if elapsed > time_limit:
                print(f"  Time limit after {count}")
                break

        dfunc = make_dfunc(m, combo)
        n = m ** 3

        # Check cycle 0 first
        ok = True
        for c in range(3):
            length = trace_cycle_fast(m, dfunc, c)
            if length != n:
                ok = False
                break

        if ok:
            solutions.append(combo)
            print(f"  FOUND solution #{len(solutions)}")
            for s in range(m):
                print(f"    s={s}: perm={combo[s]}")

    elapsed = time.time() - t0
    print(f"Done: {count} in {elapsed:.1f}s, {len(solutions)} solutions")
    return solutions


def verify_and_save(m, perm_assignment, label="bydiag"):
    """Verify and save a solution."""
    dfunc = make_dfunc(m, perm_assignment)
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
    if ok:
        print_decomposition_stats(m, cycles)
        save_decomposition(f"artifacts/{label}_m{m}.json", m, cycles)
    return ok


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("m", type=int, nargs="*", default=[3])
    parser.add_argument("--time-limit", type=int, default=300)
    args = parser.parse_args()

    for m in args.m:
        print(f"\n{'='*60}")
        print(f"Diagonal-class search for m={m}")
        print(f"{'='*60}")

        solutions = brute_force_search(m, time_limit=args.time_limit)

        if solutions:
            print(f"\nVerifying first solution for m={m}:")
            verify_and_save(m, solutions[0])

            # Analyze common patterns
            if len(solutions) >= 2:
                print(f"\nAll {len(solutions)} solutions:")
                for i, sol in enumerate(solutions):
                    perms_str = " | ".join(str(sol[s]) for s in range(m))
                    print(f"  #{i+1}: {perms_str}")
        else:
            print(f"No s-dependent solution exists for m={m}")


if __name__ == "__main__":
    main()
