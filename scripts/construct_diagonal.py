#!/usr/bin/env python3
"""
Diagonal-based construction solver.

Key insight: at each vertex (x,y,z), the 3 cycles use a permutation of {0,1,2}.
Off the diagonal s=(x+y+z)%m != m-1, cycles use the identity (cycle c -> dir c).
On the diagonal s=m-1, we choose one of two derangements:
  A = (1,2,0): cycle 0->dir1, cycle 1->dir2, cycle 2->dir0
  B = (2,0,1): cycle 0->dir2, cycle 1->dir0, cycle 2->dir1

We solve for the binary A/B assignment on the m^2 diagonal vertices
such that all 3 functional graphs are Hamiltonian cycles.
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


DERANGEMENT_A = (1, 2, 0)  # cycle c -> dir (c+1)%3
DERANGEMENT_B = (2, 0, 1)  # cycle c -> dir (c+2)%3


def get_direction(cycle, is_diagonal, is_A):
    """Get direction for a cycle at a vertex given its diagonal/derangement status."""
    if not is_diagonal:
        return cycle  # identity permutation
    if is_A:
        return DERANGEMENT_A[cycle]
    else:
        return DERANGEMENT_B[cycle]


def solve_diagonal(m, time_limit=300, log=False):
    """
    Solve for A/B assignment on diagonal vertices.

    Returns: (dfunc, stats) or (None, stats)
    """
    n = m ** 3
    vertices = all_vertices(m)
    v2i = {v: vertex_index(m, *v) for v in vertices}

    # Diagonal vertices: s = (x+y+z) % m == m-1
    diag_verts = [v for v in vertices if (v[0]+v[1]+v[2]) % m == m - 1]
    non_diag_verts = [v for v in vertices if (v[0]+v[1]+v[2]) % m != m - 1]

    print(f"m={m}: {len(diag_verts)} diagonal vertices, {len(non_diag_verts)} non-diagonal")

    model = cp_model.CpModel()

    # Binary variable for each diagonal vertex: True = A, False = B
    sigma = {}
    for v in diag_verts:
        sigma[v] = model.new_bool_var(f"sigma_{v}")

    # For each cycle c, build the circuit constraint
    for c in range(3):
        arcs = []
        for v in vertices:
            vi = v2i[v]
            if v in sigma:
                # Diagonal vertex: direction depends on sigma
                # If sigma=True (A): direction = DERANGEMENT_A[c]
                # If sigma=False (B): direction = DERANGEMENT_B[c]
                d_a = DERANGEMENT_A[c]
                d_b = DERANGEMENT_B[c]

                if d_a == d_b:
                    # Same direction regardless of choice (shouldn't happen for derangements)
                    w = next_vertex(m, v, d_a)
                    wi = v2i[w]
                    arcs.append((vi, wi, model.new_constant(1)))
                else:
                    w_a = next_vertex(m, v, d_a)
                    w_b = next_vertex(m, v, d_b)
                    wi_a = v2i[w_a]
                    wi_b = v2i[w_b]
                    arcs.append((vi, wi_a, sigma[v]))
                    arcs.append((vi, wi_b, ~sigma[v]))
            else:
                # Non-diagonal vertex: direction = c (fixed)
                w = next_vertex(m, v, c)
                wi = v2i[w]
                arcs.append((vi, wi, model.new_constant(1)))

        model.add_circuit(arcs)

    # Count constraints: need enough A and B choices for balance
    # For Hamiltonian cycle, each direction must be used a multiple of m times
    # A count + B count = m^2
    # Cycle 0: uses dir 1 at A-verts, dir 2 at B-verts
    # Net y-displacement from diagonal: #A * 1 ≡ 0 mod m -> #A ≡ 0 mod m
    # Net z-displacement from diagonal: #B * 1 ≡ 0 mod m -> #B ≡ 0 mod m
    # Since #A + #B = m^2, and m | #A, m | #B -> both multiples of m ✓ automatic
    # But we can add: #B >= m (at least m slice changes for cycle 0)
    num_A = sum(sigma[v] for v in diag_verts)
    # Don't over-constrain; let the solver find valid assignments

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = 8
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
        # Extract direction function
        dfunc = {}
        for v in vertices:
            if v in sigma:
                is_A = solver.boolean_value(sigma[v])
                dfunc[v] = [get_direction(c, True, is_A) for c in range(3)]
            else:
                dfunc[v] = [0, 1, 2]

        # Convert to cycles
        cycles = []
        for c in range(3):
            path = []
            v = (0, 0, 0)
            for _ in range(n):
                path.append(v)
                d = dfunc[v][c]
                v = next_vertex(m, v, d)
            cycles.append(path)

        # Count A/B
        num_a = sum(1 for v in diag_verts if solver.boolean_value(sigma[v]))
        num_b = len(diag_verts) - num_a
        stats["num_A"] = num_a
        stats["num_B"] = num_b

        return dfunc, cycles, stats
    else:
        return None, None, stats


def analyze_assignment(m, dfunc, diag_verts):
    """Analyze the A/B pattern on diagonal vertices."""
    print(f"\nA/B assignment pattern (m={m}):")

    # Group by coordinates
    a_verts = [v for v in diag_verts if dfunc[v] == list(DERANGEMENT_A)]
    b_verts = [v for v in diag_verts if dfunc[v] == list(DERANGEMENT_B)]

    print(f"  A vertices ({len(a_verts)}): x values = {sorted(set(v[0] for v in a_verts))}")
    print(f"  B vertices ({len(b_verts)}): x values = {sorted(set(v[0] for v in b_verts))}")

    # Check if B vertices have a pattern
    print(f"  B vertices: {sorted(b_verts)}")

    # Check by x value
    for x in range(m):
        bv = [v for v in b_verts if v[0] == x]
        av = [v for v in a_verts if v[0] == x]
        print(f"    x={x}: {len(av)} A, {len(bv)} B")

    # Check by y value
    for y in range(m):
        bv = [v for v in b_verts if v[1] == y]
        av = [v for v in a_verts if v[1] == y]
        print(f"    y={y}: {len(av)} A, {len(bv)} B")

    # Check by z value
    for z in range(m):
        bv = [v for v in b_verts if v[2] == z]
        av = [v for v in a_verts if v[2] == z]
        print(f"    z={z}: {len(av)} A, {len(bv)} B")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("m", type=int, nargs="*", default=[3, 4, 5, 6, 7])
    parser.add_argument("--time-limit", type=int, default=60)
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()

    for m in args.m:
        print(f"\n{'='*60}")
        print(f"Diagonal construction for m={m}")
        print(f"{'='*60}")

        dfunc, cycles, stats = solve_diagonal(m, time_limit=args.time_limit)

        print(f"Status: {stats['status']}, Time: {stats['time_seconds']}s")

        if cycles is not None:
            ok, msg = verify_decomposition(m, cycles)
            print(f"Verification: {msg}")

            if ok:
                print_decomposition_stats(m, cycles)
                diag_verts = [v for v in all_vertices(m)
                              if (v[0]+v[1]+v[2]) % m == m-1]
                analyze_assignment(m, dfunc, diag_verts)

                if args.save:
                    save_decomposition(f"artifacts/diagonal_m{m}.json", m, cycles)
                    print(f"Saved to artifacts/diagonal_m{m}.json")

                    # Save the A/B assignment
                    assignment = {}
                    for v in diag_verts:
                        assignment[str(v)] = "A" if dfunc[v] == list(DERANGEMENT_A) else "B"
                    with open(f"artifacts/diagonal_assignment_m{m}.json", "w") as f:
                        json.dump({"m": m, "assignment": assignment}, f, indent=2)
        else:
            print("No solution found!")


if __name__ == "__main__":
    main()
