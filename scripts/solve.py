#!/usr/bin/env python3
"""
CP-SAT solver for decomposing G_m into 3 directed Hamiltonian cycles.

Uses OR-Tools CP-SAT with AddCircuit constraints.

For each vertex v and cycle c, we decide which direction cycle c takes.
Constraints:
  1. At each vertex, the 3 cycles use a permutation of {0,1,2} (all different directions).
  2. For each cycle c, the functional graph (v -> v + e_{d_c(v)}) is a Hamiltonian cycle
     (modeled via AddCircuit).
"""

import json
import sys
import time
from itertools import product

from ortools.sat.python import cp_model

from verify import (
    all_vertices,
    direction_function_to_cycles,
    next_vertex,
    save_decomposition,
    verify_decomposition,
    print_decomposition_stats,
    vertex_index,
)


def solve_decomposition(m, time_limit=300, num_workers=8, log=True):
    """
    Find a decomposition of G_m into 3 Hamiltonian cycles using CP-SAT.

    Returns:
        (cycles, stats) if found, (None, stats) otherwise
    """
    n = m ** 3
    vertices = all_vertices(m)
    v2i = {v: vertex_index(m, *v) for v in vertices}

    model = cp_model.CpModel()

    # For each vertex v and cycle c: direction[v][c] in {0, 1, 2}
    direction = {}
    for v in vertices:
        direction[v] = {}
        for c in range(3):
            direction[v][c] = model.new_int_var(0, 2, f"d_{v}_{c}")

    # Constraint 1: at each vertex, the 3 directions are all different
    for v in vertices:
        model.add_all_different([direction[v][c] for c in range(3)])

    # Constraint 2: each cycle forms a Hamiltonian circuit
    # For each cycle c, create boolean arc variables
    for c in range(3):
        arcs = []
        for v in vertices:
            vi = v2i[v]
            for d in range(3):
                w = next_vertex(m, v, d)
                wi = v2i[w]
                # Boolean: does cycle c take direction d at vertex v?
                b = model.new_bool_var(f"arc_{c}_{v}_{d}")
                # Link boolean to direction variable
                model.add(direction[v][c] == d).only_enforce_if(b)
                model.add(direction[v][c] != d).only_enforce_if(~b)
                arcs.append((vi, wi, b))
        model.add_circuit(arcs)

    # Optional: symmetry breaking
    # Fix cycle 0's direction at origin to 0
    model.add(direction[(0, 0, 0)][0] == 0)
    # Fix cycle ordering: cycle 1 at origin uses dir 1
    model.add(direction[(0, 0, 0)][1] == 1)

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
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
    }

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        # Extract direction function
        dfunc = {}
        for v in vertices:
            dfunc[v] = tuple(solver.value(direction[v][c]) for c in range(3))

        cycles = direction_function_to_cycles(m, dfunc)
        return cycles, stats
    else:
        return None, stats


def solve_and_save(m, output_dir="artifacts", **kwargs):
    """Solve and save results."""
    print(f"\n{'='*60}")
    print(f"Solving G_{m} decomposition (m={m}, n={m**3} vertices, {3*m**3} arcs)")
    print(f"{'='*60}")

    cycles, stats = solve_decomposition(m, **kwargs)

    print(f"\nSolver status: {stats['status']}")
    print(f"Time: {stats['time_seconds']}s")
    print(f"Branches: {stats['branches']}, Conflicts: {stats['conflicts']}")

    if cycles is not None:
        # Verify
        ok, msg = verify_decomposition(m, cycles)
        print(f"Verification: {'PASS' if ok else 'FAIL'}: {msg}")

        if ok:
            print_decomposition_stats(m, cycles)
            filepath = f"{output_dir}/decomposition_m{m}.json"
            save_decomposition(filepath, m, cycles)
            print(f"Saved to {filepath}")

            # Also save stats
            stats_path = f"{output_dir}/solve_stats_m{m}.json"
            with open(stats_path, "w") as f:
                json.dump(stats, f, indent=2)

        return cycles, stats
    else:
        print("No solution found.")
        return None, stats


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Solve G_m decomposition")
    parser.add_argument("m", type=int, nargs="?", default=3, help="Modulus (default: 3)")
    parser.add_argument("--time-limit", type=int, default=300, help="Time limit in seconds")
    parser.add_argument("--workers", type=int, default=8, help="Number of worker threads")
    parser.add_argument("--output-dir", default="artifacts", help="Output directory")
    parser.add_argument("--quiet", action="store_true", help="Suppress solver log")

    args = parser.parse_args()

    solve_and_save(
        args.m,
        output_dir=args.output_dir,
        time_limit=args.time_limit,
        num_workers=args.workers,
        log=not args.quiet,
    )
