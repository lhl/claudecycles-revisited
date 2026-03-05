#!/usr/bin/env python3
"""
Deterministic verifier for decomposition of G_m into 3 directed Hamiltonian cycles.

G_m has vertex set Z_m^3 with arcs:
  (i,j,k) -> ((i+1)%m, j, k)   [direction 0]
  (i,j,k) -> (i, (j+1)%m, k)   [direction 1]
  (i,j,k) -> (i, j, (k+1)%m)   [direction 2]

Input format: a decomposition is specified as 3 "direction sequences" --
for each cycle c, a list of m^3 directions (0/1/2) giving the step taken
at each vertex visited in order. Alternatively, as 3 lists of m^3 vertices
(visit order), or as a direction function mapping each vertex to a
(cycle -> direction) assignment.

This module provides:
  - verify_cycle(m, cycle_vertices): check one cycle is Hamiltonian
  - verify_decomposition(m, cycles): check 3 cycles decompose G_m
  - direction_function_to_cycles(m, dfunc): convert direction assignment to cycles
  - cycles_to_direction_function(m, cycles): convert cycles to direction assignment
"""

import json
import sys
from itertools import product


def vertex_index(m, x, y, z):
    """Map (x,y,z) to integer index."""
    return x * m * m + y * m + z


def index_to_vertex(m, idx):
    """Map integer index to (x,y,z)."""
    z = idx % m
    y = (idx // m) % m
    x = idx // (m * m)
    return (x, y, z)


def next_vertex(m, v, direction):
    """Return vertex reached from v by stepping in given direction."""
    x, y, z = v
    if direction == 0:
        return ((x + 1) % m, y, z)
    elif direction == 1:
        return (x, (y + 1) % m, z)
    elif direction == 2:
        return (x, y, (z + 1) % m)
    else:
        raise ValueError(f"Invalid direction: {direction}")


def all_vertices(m):
    """Generate all m^3 vertices."""
    return list(product(range(m), repeat=3))


def all_arcs(m):
    """Generate all 3m^3 arcs as (tail, head, direction) triples."""
    arcs = []
    for v in all_vertices(m):
        for d in range(3):
            arcs.append((v, next_vertex(m, v, d), d))
    return arcs


def verify_cycle(m, cycle_vertices):
    """
    Verify that a list of vertices forms a directed Hamiltonian cycle in G_m.

    Args:
        m: modulus
        cycle_vertices: list of m^3 (x,y,z) tuples in visit order

    Returns:
        (ok, message) where ok is True/False
    """
    n = m ** 3
    if len(cycle_vertices) != n:
        return False, f"Cycle length {len(cycle_vertices)} != {n}"

    # Check all vertices are valid and distinct
    vset = set()
    for v in cycle_vertices:
        if not (isinstance(v, (tuple, list)) and len(v) == 3):
            return False, f"Invalid vertex format: {v}"
        x, y, z = v
        if not (0 <= x < m and 0 <= y < m and 0 <= z < m):
            return False, f"Vertex out of range: {v}"
        vt = tuple(v)
        if vt in vset:
            return False, f"Duplicate vertex: {v}"
        vset.add(vt)

    if len(vset) != n:
        return False, f"Only {len(vset)} distinct vertices, need {n}"

    # Check each consecutive pair (and wrap-around) is a valid arc
    for i in range(n):
        v = tuple(cycle_vertices[i])
        w = tuple(cycle_vertices[(i + 1) % n])
        # Check w is reachable from v by one step
        valid = False
        for d in range(3):
            if next_vertex(m, v, d) == w:
                valid = True
                break
        if not valid:
            return False, f"No arc from {v} to {w} (step {i})"

    return True, "Valid Hamiltonian cycle"


def cycle_arcs(m, cycle_vertices):
    """Extract the set of arcs (as (tail, head) pairs) from a cycle."""
    n = m ** 3
    arcs = set()
    for i in range(n):
        v = tuple(cycle_vertices[i])
        w = tuple(cycle_vertices[(i + 1) % n])
        arcs.add((v, w))
    return arcs


def cycle_arc_directions(m, cycle_vertices):
    """Extract arcs as (vertex, direction) pairs from a cycle."""
    n = m ** 3
    arc_dirs = []
    for i in range(n):
        v = tuple(cycle_vertices[i])
        w = tuple(cycle_vertices[(i + 1) % n])
        for d in range(3):
            if next_vertex(m, v, d) == w:
                arc_dirs.append((v, d))
                break
    return arc_dirs


def verify_decomposition(m, cycles):
    """
    Verify that 3 cycles form a valid decomposition of G_m.

    Args:
        m: modulus
        cycles: list of 3 lists of vertices (each list is a Hamiltonian cycle)

    Returns:
        (ok, message)
    """
    if len(cycles) != 3:
        return False, f"Expected 3 cycles, got {len(cycles)}"

    n = m ** 3

    # Verify each cycle individually
    for i, cyc in enumerate(cycles):
        ok, msg = verify_cycle(m, cyc)
        if not ok:
            return False, f"Cycle {i}: {msg}"

    # Check arc-disjointness
    all_used = set()
    for i, cyc in enumerate(cycles):
        arcs = cycle_arcs(m, cyc)
        overlap = all_used & arcs
        if overlap:
            sample = list(overlap)[:3]
            return False, f"Cycle {i} shares arcs with earlier cycles: {sample}"
        all_used |= arcs

    # Check coverage
    expected = set()
    for v in all_vertices(m):
        for d in range(3):
            w = next_vertex(m, v, d)
            expected.add((v, w))

    if all_used != expected:
        missing = expected - all_used
        extra = all_used - expected
        parts = []
        if missing:
            parts.append(f"{len(missing)} missing arcs")
        if extra:
            parts.append(f"{len(extra)} extra arcs")
        return False, f"Arc coverage mismatch: {', '.join(parts)}"

    return True, f"Valid decomposition of G_{m} into 3 Hamiltonian cycles"


def direction_function_to_cycles(m, dfunc):
    """
    Convert a direction function to 3 cycles.

    Args:
        m: modulus
        dfunc: dict mapping (x,y,z) -> (d0, d1, d2) where d_c is the direction
               cycle c takes at this vertex. Must be a permutation of (0,1,2).

    Returns:
        list of 3 cycles (each a list of vertices in visit order)
    """
    n = m ** 3
    cycles = []
    for c in range(3):
        # Trace cycle c starting from (0,0,0)
        visited = []
        v = (0, 0, 0)
        for _ in range(n):
            visited.append(v)
            d = dfunc[v][c]
            v = next_vertex(m, v, d)
        if v != (0, 0, 0):
            raise ValueError(f"Cycle {c} does not return to origin after {n} steps (reached {v})")
        cycles.append(visited)
    return cycles


def cycles_to_direction_function(m, cycles):
    """
    Convert 3 cycles to a direction function.

    Returns:
        dict mapping (x,y,z) -> [d0, d1, d2]
    """
    dfunc = {}
    for v in all_vertices(m):
        dfunc[v] = [None, None, None]

    for c, cyc in enumerate(cycles):
        n = m ** 3
        for i in range(n):
            v = tuple(cyc[i])
            w = tuple(cyc[(i + 1) % n])
            for d in range(3):
                if next_vertex(m, v, d) == w:
                    dfunc[v][c] = d
                    break

    return dfunc


def print_decomposition_stats(m, cycles):
    """Print statistics about a decomposition."""
    print(f"\n=== Decomposition Statistics for m={m} ===")
    print(f"Vertices: {m**3}, Arcs: {3*m**3}")

    for c, cyc in enumerate(cycles):
        arc_dirs = cycle_arc_directions(m, cyc)
        dir_counts = [0, 0, 0]
        for _, d in arc_dirs:
            dir_counts[d] += 1
        print(f"Cycle {c}: {dir_counts[0]} dir-0, {dir_counts[1]} dir-1, {dir_counts[2]} dir-2")


def load_decomposition(filepath):
    """Load a decomposition from JSON file."""
    with open(filepath) as f:
        data = json.load(f)
    m = data["m"]
    cycles = [[(v[0], v[1], v[2]) for v in cyc] for cyc in data["cycles"]]
    return m, cycles


def save_decomposition(filepath, m, cycles):
    """Save a decomposition to JSON file."""
    data = {
        "m": m,
        "cycles": [list(map(list, cyc)) for cyc in cycles],
    }
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify.py <decomposition.json>")
        print("  JSON format: {\"m\": N, \"cycles\": [[[x,y,z], ...], ...]}")
        sys.exit(1)

    filepath = sys.argv[1]
    m, cycles = load_decomposition(filepath)
    ok, msg = verify_decomposition(m, cycles)
    if ok:
        print(f"PASS: {msg}")
        print_decomposition_stats(m, cycles)
    else:
        print(f"FAIL: {msg}")
        sys.exit(1)
