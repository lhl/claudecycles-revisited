#!/usr/bin/env python3
"""
Layer-lifting construction for G_m decomposition.

Strategy:
1. Build C_2 as a z-primary Hamiltonian cycle:
   - Choose a Hamiltonian cycle H on Z_m^2 (using dirs 0,1).
   - Visit columns in H-order, taking m-1 dir-2 steps within each column.
   - Take 1 lateral step (from H) between columns.

2. Remaining graph is 2-regular. At each vertex:
   - Normal vertices: remaining arcs are dir 0, dir 1.
   - Lateral vertices: remaining arcs are dir 2 and complementary horizontal.

3. Decompose remaining graph into C_0 and C_1 (two Hamiltonian cycles).
   At lateral vertices, choose which cycle gets dir 2 (binary choice).
   At normal vertices, fix C_0=dir0, C_1=dir1 (default).
   Use CP-SAT or brute force for the binary choices.
"""

import json
import sys
import time
from collections import defaultdict
from itertools import product

from verify import (
    all_vertices,
    next_vertex,
    save_decomposition,
    verify_decomposition,
    print_decomposition_stats,
    vertex_index,
)


def build_serpentine_2d(m):
    """Build the standard row-serpentine Hamiltonian cycle on Z_m^2."""
    path = []
    pos = (0, 0)
    for step_idx in range(m * m):
        path.append(pos)
        x, y = pos
        s = (x + y) % m
        if s == m - 1:
            # Turn: use dir 1
            pos = (x, (y + 1) % m)
        else:
            # Sweep: use dir 0
            pos = ((x + 1) % m, y)
    return path


def build_z_primary_cycle(m, h_cycle):
    """
    Build C_2: z-primary Hamiltonian cycle on Z_m^3.

    h_cycle: list of m^2 vertices of Z_m^2 in Hamiltonian cycle order.
    """
    n2 = m * m
    n3 = m ** 3

    # Determine direction used by H at each position
    h_dirs = []
    for i in range(n2):
        v = h_cycle[i]
        w = h_cycle[(i + 1) % n2]
        if ((v[0] + 1) % m, v[1]) == w:
            h_dirs.append(0)
        elif (v[0], (v[1] + 1) % m) == w:
            h_dirs.append(1)
        else:
            raise ValueError(f"Invalid H arc: {v} -> {w}")

    # Build C_2 path
    path = []
    z = 0
    for k in range(n2):
        xy = h_cycle[k]
        # Visit m vertices in this column
        for step in range(m):
            path.append((xy[0], xy[1], z % m))
            if step < m - 1:
                z += 1  # dir 2 step
            # else: lateral step (handled by the column transition)
        # After m-1 dir-2 steps, z has advanced by m-1
        # Lateral step: direction is h_dirs[k], z stays the same

    return path


def get_lateral_info(m, h_cycle):
    """
    Get lateral vertex info for the z-primary cycle.

    Returns: list of (vertex_3d, h_direction) for each lateral vertex.
    """
    n2 = m * m

    h_dirs = []
    for i in range(n2):
        v = h_cycle[i]
        w = h_cycle[(i + 1) % n2]
        if ((v[0] + 1) % m, v[1]) == w:
            h_dirs.append(0)
        elif (v[0], (v[1] + 1) % m) == w:
            h_dirs.append(1)
        else:
            raise ValueError(f"Invalid H arc: {v} -> {w}")

    laterals = []
    z = 0
    for k in range(n2):
        xy = h_cycle[k]
        z_lateral = (z + m - 1) % m  # z after m-1 dir-2 steps
        laterals.append(((xy[0], xy[1], z_lateral), h_dirs[k]))
        z = (z + m - 1) % m  # update z for next column's start (same as z_lateral)

    return laterals


def solve_remaining(m, laterals, time_limit=60):
    """
    Solve for C_0, C_1 given the lateral vertex info.

    At normal vertices: C_0=dir0, C_1=dir1 (fixed).
    At lateral vertices: binary choice (which cycle gets dir 2).

    Uses brute force for small m, CP-SAT for larger m.
    """
    n3 = m ** 3
    n2 = m * m

    lateral_set = {lat[0] for lat in laterals}
    lateral_dir = {lat[0]: lat[1] for lat in laterals}

    if n2 <= 20:
        return brute_force_remaining(m, laterals, lateral_set, lateral_dir)
    else:
        return cpsat_remaining(m, laterals, lateral_set, lateral_dir, time_limit)


def get_c0_direction(v, choice, lateral_set, lateral_dir):
    """Get C_0's direction at vertex v given binary choices at laterals."""
    if v not in lateral_set:
        return 0  # normal vertex: C_0 uses dir 0
    if choice[v]:
        return 2  # Group A: C_0 gets dir 2
    else:
        # Group B: C_0 gets the complementary horizontal direction
        h_dir = lateral_dir[v]
        return 1 - h_dir  # if H used 0, remaining horizontal is 1; if H used 1, remaining is 0


def get_c1_direction(v, choice, lateral_set, lateral_dir):
    """Get C_1's direction at vertex v given binary choices at laterals."""
    if v not in lateral_set:
        return 1  # normal vertex: C_1 uses dir 1
    if not choice[v]:
        return 2  # Group B: C_1 gets dir 2
    else:
        # Group A: C_1 gets the complementary horizontal direction
        h_dir = lateral_dir[v]
        return 1 - h_dir


def trace_cycle_from_dfunc(m, direction_func, start=(0, 0, 0)):
    """Trace a cycle following direction_func."""
    n = m ** 3
    path = []
    v = start
    seen = set()
    for _ in range(n):
        if v in seen:
            return path, False
        seen.add(v)
        path.append(v)
        d = direction_func(v)
        v = next_vertex(m, v, d)
    return path, (v == start and len(seen) == n)


def brute_force_remaining(m, laterals, lateral_set, lateral_dir):
    """Brute force search over binary choices at lateral vertices."""
    n3 = m ** 3
    lat_list = [lat[0] for lat in laterals]

    print(f"  Brute force: {2**len(lat_list)} choices...")

    for bits in range(2 ** len(lat_list)):
        choice = {}
        for i, v in enumerate(lat_list):
            choice[v] = bool((bits >> i) & 1)

        d0_func = lambda v, c=choice: get_c0_direction(v, c, lateral_set, lateral_dir)
        d1_func = lambda v, c=choice: get_c1_direction(v, c, lateral_set, lateral_dir)

        _, ham0 = trace_cycle_from_dfunc(m, d0_func)
        if not ham0:
            continue
        _, ham1 = trace_cycle_from_dfunc(m, d1_func)
        if not ham1:
            continue

        print(f"  Found solution at bits={bits:0{len(lat_list)}b}")
        a_count = sum(choice.values())
        print(f"  Group A: {a_count}, Group B: {len(lat_list) - a_count}")
        return choice

    print("  No solution found!")
    return None


def cpsat_remaining(m, laterals, lateral_set, lateral_dir, time_limit):
    """CP-SAT solver for the binary choices."""
    from ortools.sat.python import cp_model

    n3 = m ** 3
    vertices = all_vertices(m)
    v2i = {v: vertex_index(m, *v) for v in vertices}

    model = cp_model.CpModel()

    # Binary choice for each lateral vertex
    choice = {}
    lat_list = [lat[0] for lat in laterals]
    for v in lat_list:
        choice[v] = model.new_bool_var(f"ch_{v}")

    # Build circuit constraints for C_0 and C_1
    for c in range(2):
        arcs = []
        for v in vertices:
            vi = v2i[v]
            if v not in lateral_set:
                # Normal vertex: fixed direction
                d = 0 if c == 0 else 1
                w = next_vertex(m, v, d)
                wi = v2i[w]
                arcs.append((vi, wi, model.new_constant(1)))
            else:
                h_dir = lateral_dir[v]
                comp_dir = 1 - h_dir

                if c == 0:
                    # C_0: choice=True -> dir 2, choice=False -> comp_dir
                    w_true = next_vertex(m, v, 2)
                    w_false = next_vertex(m, v, comp_dir)
                    arcs.append((vi, v2i[w_true], choice[v]))
                    arcs.append((vi, v2i[w_false], ~choice[v]))
                else:
                    # C_1: choice=True -> comp_dir, choice=False -> dir 2
                    w_true = next_vertex(m, v, comp_dir)
                    w_false = next_vertex(m, v, 2)
                    arcs.append((vi, v2i[w_true], choice[v]))
                    arcs.append((vi, v2i[w_false], ~choice[v]))

        model.add_circuit(arcs)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = 8

    status = solver.solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        result = {v: solver.boolean_value(choice[v]) for v in lat_list}
        a_count = sum(result.values())
        print(f"  CP-SAT solution: Group A={a_count}, Group B={len(lat_list)-a_count}")
        return result
    else:
        print(f"  CP-SAT status: {solver.status_name(status)}")
        return None


def construct_decomposition(m, time_limit=60):
    """Full construction pipeline."""
    print(f"\n{'='*60}")
    print(f"Layer-lifting construction for m={m}")
    print(f"{'='*60}")

    # Step 1: build 2D serpentine
    h_cycle = build_serpentine_2d(m)
    print(f"2D serpentine: {len(h_cycle)} vertices")

    # Step 2: build C_2 (z-primary)
    c2_path = build_z_primary_cycle(m, h_cycle)
    print(f"C_2 path: {len(c2_path)} vertices")

    # Verify C_2
    from verify import verify_cycle
    ok, msg = verify_cycle(m, c2_path)
    print(f"C_2 verification: {msg}")
    if not ok:
        return None

    # Step 3: get lateral info
    laterals = get_lateral_info(m, h_cycle)
    print(f"Lateral vertices: {len(laterals)}")

    # Step 4: solve for C_0, C_1
    lateral_set = {lat[0] for lat in laterals}
    lateral_dir = {lat[0]: lat[1] for lat in laterals}

    choice = solve_remaining(m, laterals, time_limit)
    if choice is None:
        return None

    # Step 5: build C_0 and C_1
    d0_func = lambda v: get_c0_direction(v, choice, lateral_set, lateral_dir)
    d1_func = lambda v: get_c1_direction(v, choice, lateral_set, lateral_dir)

    c0_path, _ = trace_cycle_from_dfunc(m, d0_func)
    c1_path, _ = trace_cycle_from_dfunc(m, d1_func)

    cycles = [c0_path, c1_path, c2_path]

    # Verify full decomposition
    ok, msg = verify_decomposition(m, cycles)
    print(f"\nFull verification: {msg}")
    if ok:
        print_decomposition_stats(m, cycles)
        save_decomposition(f"artifacts/lift_m{m}.json", m, cycles)

    return cycles if ok else None


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("m", type=int, nargs="*", default=[3, 5, 7])
    parser.add_argument("--time-limit", type=int, default=120)
    args = parser.parse_args()

    for m in args.m:
        construct_decomposition(m, time_limit=args.time_limit)
