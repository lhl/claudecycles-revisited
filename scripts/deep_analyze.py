#!/usr/bin/env python3
"""
Deep analysis of solver-found decompositions.
Try to find ANY pattern in the direction function.
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
)


def analyze_all_linear_deps(m, dfunc):
    """
    Check if the permutation at (x,y,z) depends on any pair of linear
    functions of coordinates.
    """
    print(f"\n=== Linear dependency search for m={m} ===")

    # Encode permutation as integer 0-5
    PERMS = list(set(tuple(dfunc[v]) for v in dfunc))
    perm_to_id = {p: i for i, p in enumerate(PERMS)}
    print(f"Distinct permutations used: {len(PERMS)}")
    for p in PERMS:
        count = sum(1 for v in dfunc if tuple(dfunc[v]) == p)
        print(f"  {p}: {count} vertices")

    # Check if permutation depends on a single linear function
    for a in range(m):
        for b in range(m):
            for c in range(m):
                if a == b == c == 0:
                    continue
                by_val = defaultdict(set)
                for v in dfunc:
                    val = (a * v[0] + b * v[1] + c * v[2]) % m
                    by_val[val].add(tuple(dfunc[v]))
                if all(len(s) == 1 for s in by_val.values()):
                    print(f"  Depends on ({a}x+{b}y+{c}z) mod {m}")
                    for val in sorted(by_val):
                        print(f"    val={val}: {list(by_val[val])[0]}")
                    return True

    # Check pairs of linear functions
    print("  No single linear dependency found.")
    print("  Checking pairs of linear functions...")

    found = False
    for a1, b1, c1 in product(range(m), repeat=3):
        if a1 == b1 == c1 == 0:
            continue
        for a2, b2, c2 in product(range(m), repeat=3):
            if a2 == b2 == c2 == 0:
                continue
            if (a2, b2, c2) <= (a1, b1, c1):
                continue  # avoid duplicates

            by_pair = defaultdict(set)
            for v in dfunc:
                v1 = (a1 * v[0] + b1 * v[1] + c1 * v[2]) % m
                v2 = (a2 * v[0] + b2 * v[1] + c2 * v[2]) % m
                by_pair[(v1, v2)].add(tuple(dfunc[v]))
            if all(len(s) == 1 for s in by_pair.values()):
                print(f"  Depends on ({a1}x+{b1}y+{c1}z, {a2}x+{b2}y+{c2}z) mod {m}")
                found = True
                break
        if found:
            break

    if not found:
        print("  No pair of linear functions determines the permutation.")

    return found


def find_cycle_direction_pattern(m, cycles):
    """Analyze direction sequence patterns for each cycle."""
    print(f"\n=== Direction sequence pattern analysis for m={m} ===")

    for c, cyc in enumerate(cycles):
        n = len(cyc)
        # Extract direction sequence
        dirs = []
        for i in range(n):
            v = cyc[i]
            w = cyc[(i + 1) % n]
            for d in range(3):
                if next_vertex(m, v, d) == w:
                    dirs.append(d)
                    break

        # Check for periodic patterns
        for period in range(1, n // 2 + 1):
            if n % period != 0:
                continue
            is_periodic = all(dirs[i] == dirs[i % period] for i in range(n))
            if is_periodic and period < n:
                print(f"Cycle {c}: periodic with period {period}")
                print(f"  Base pattern: {dirs[:period]}")
                break


def analyze_coordinate_projections(m, dfunc):
    """Check how the permutation relates to individual and paired coordinates."""
    print(f"\n=== Coordinate projection analysis for m={m} ===")

    # For each cycle c, check if its direction depends on a single coordinate
    for c in range(3):
        for coord in range(3):
            by_val = defaultdict(set)
            for v in dfunc:
                by_val[v[coord]].add(dfunc[v][c])
            if all(len(s) == 1 for s in by_val.values()):
                coord_name = "xyz"[coord]
                print(f"  Cycle {c} direction depends only on {coord_name}")

    # Check if direction depends on any pair of coordinates
    for c in range(3):
        for c1 in range(3):
            for c2 in range(c1 + 1, 3):
                by_pair = defaultdict(set)
                for v in dfunc:
                    by_pair[(v[c1], v[c2])].add(dfunc[v][c])
                if all(len(s) == 1 for s in by_pair.values()):
                    names = "xyz"
                    print(f"  Cycle {c} direction depends on ({names[c1]},{names[c2]})")

    # Check if direction for cycle c at vertex v depends on (v[c], s)
    for c in range(3):
        by_pair = defaultdict(set)
        for v in dfunc:
            s = (v[0] + v[1] + v[2]) % m
            by_pair[(v[c], s)].add(dfunc[v][c])
        if all(len(s) == 1 for s in by_pair.values()):
            print(f"  Cycle {c} direction depends on (coord_{c}, s)")


def analyze_orbit_structure(m, dfunc):
    """Analyze the orbit structure when we quotient by some group action."""
    print(f"\n=== Orbit structure analysis for m={m} ===")

    # Check if cyclic coordinate permutation maps one cycle's dfunc to another
    # sigma: (x,y,z) -> (z,x,y), which maps dir 0->dir 2, dir 1->dir 0, dir 2->dir 1
    print("Checking cyclic coordinate symmetry:")
    for v in list(dfunc.keys())[:5]:
        x, y, z = v
        w = (z, x, y)
        # sigma maps dir d at v to dir (d-1)%3 at w
        # So cycle c at v uses dir d[c], which becomes dir (d[c]-1)%3 at w for cycle c
        # But we want: cycle c at w should correspond to cycle (c+1) at v?
        d_v = dfunc[v]
        d_w = dfunc[w]
        print(f"  v={v}: {d_v}")
        print(f"  sigma(v)={w}: {d_w}")
        # Check: d_w[c] == (d_v[(c-1)%3] + 1) % 3 ?
        match = all(d_w[c] == (d_v[(c - 1) % 3] + 1) % 3 for c in range(3))
        print(f"  Cyclic symmetry holds: {match}")


def find_solution_with_structure(m):
    """Use CP-SAT to find a solution with specific structural constraints."""
    from ortools.sat.python import cp_model
    from verify import vertex_index

    vertices = all_vertices(m)
    n = m ** 3
    v2i = {v: vertex_index(m, *v) for v in vertices}

    model = cp_model.CpModel()

    # Variables: direction[v][c] in {0,1,2}
    direction = {}
    for v in vertices:
        direction[v] = {}
        for c in range(3):
            direction[v][c] = model.new_int_var(0, 2, f"d_{v}_{c}")

    # All-different at each vertex
    for v in vertices:
        model.add_all_different([direction[v][c] for c in range(3)])

    # Circuit constraints
    for c in range(3):
        arcs = []
        for v in vertices:
            vi = v2i[v]
            for d in range(3):
                w = next_vertex(m, v, d)
                wi = v2i[w]
                b = model.new_bool_var(f"a_{c}_{v}_{d}")
                model.add(direction[v][c] == d).only_enforce_if(b)
                model.add(direction[v][c] != d).only_enforce_if(~b)
                arcs.append((vi, wi, b))
        model.add_circuit(arcs)

    # STRUCTURAL CONSTRAINT: cyclic coordinate symmetry
    # If (x,y,z) -> (z,x,y) maps cycle c to cycle (c+1)%3 with appropriate dir shift
    # Then: direction[(z,x,y)][(c+1)%3] = (direction[(x,y,z)][c] + 1) % 3
    # Equivalently: for each v=(x,y,z), w=(z,x,y):
    #   direction[w][1] = (direction[v][0] + 1) % 3
    #   direction[w][2] = (direction[v][1] + 1) % 3
    #   direction[w][0] = (direction[v][2] + 1) % 3

    for v in vertices:
        x, y, z = v
        w = (z, x, y)
        for c in range(3):
            # direction[w][(c+1)%3] = (direction[v][c] + 1) % 3
            c_new = (c + 1) % 3
            # This is tricky with integer modular arithmetic in CP-SAT
            # direction[v][c] can be 0, 1, or 2
            # (direction[v][c] + 1) % 3: 0->1, 1->2, 2->0
            # Use element constraint or direct cases
            for d in range(3):
                b = model.new_bool_var(f"sym_{v}_{c}_{d}")
                model.add(direction[v][c] == d).only_enforce_if(b)
                model.add(direction[v][c] != d).only_enforce_if(~b)
                model.add(direction[w][c_new] == (d + 1) % 3).only_enforce_if(b)

    # Symmetry breaking
    model.add(direction[(0, 0, 0)][0] == 0)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60
    solver.parameters.num_workers = 8

    status = solver.solve(model)
    print(f"Structured solver status: {solver.status_name(status)}")

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        dfunc = {}
        for v in vertices:
            dfunc[v] = [solver.value(direction[v][c]) for c in range(3)]
        return dfunc
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python deep_analyze.py <file.json> | --solve <m>")
        sys.exit(1)

    if sys.argv[1] == "--solve":
        m = int(sys.argv[2])
        print(f"Finding structured solution for m={m}...")
        dfunc = find_solution_with_structure(m)
        if dfunc:
            print("Found structured solution!")
            m_val = max(v[0] for v in dfunc) + 1
            analyze_all_linear_deps(m_val, dfunc)
            analyze_coordinate_projections(m_val, dfunc)

            # Save
            from verify import direction_function_to_cycles, verify_decomposition, save_decomposition, print_decomposition_stats
            cycles = []
            n = m ** 3
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
                save_decomposition(f"artifacts/structured_m{m}.json", m, cycles)
        else:
            print("No structured solution found.")
    else:
        filepath = sys.argv[1]
        m, cycles = load_decomposition(filepath)
        dfunc = cycles_to_direction_function(m, cycles)
        analyze_all_linear_deps(m, dfunc)
        analyze_coordinate_projections(m, dfunc)
        analyze_orbit_structure(m, dfunc)
        find_cycle_direction_pattern(m, cycles)


if __name__ == "__main__":
    main()
