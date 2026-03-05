#!/usr/bin/env python3
"""
Reduced 2D solver for the diagonal assignment problem.

The 3D Hamiltonian cycle problem reduces to: find sigma: Z_m^2 -> {A, B}
such that 3 different functional graphs on Z_m^2 are each a single
Hamiltonian cycle.

Diagonal vertices of Z_m^3 are parameterized by (y,z) in Z_m^2
(with x = (m-1-y-z) mod m).

The functional graphs on Z_m^2 for each cycle:
  Cycle 0: A -> (y+1, z),     B -> (y, z+1)      [standard 2D torus generators]
  Cycle 1: A -> (y-1, z+1),   B -> (y-1, z)
  Cycle 2: A -> (y, z-1),     B -> (y+1, z-1)

All three must simultaneously be Hamiltonian cycles of length m^2.

Matrix M = [[-1,-1],[1,0]] has M^3 = I and maps Cycle k's generators
to Cycle (k+1)'s generators.
"""

import json
import sys
import time
from itertools import product
from ortools.sat.python import cp_model


# Step vectors for each cycle
STEPS = {
    0: {"A": (1, 0), "B": (0, 1)},      # +y, +z
    1: {"A": (-1, 1), "B": (-1, 0)},     # -y+z, -y
    2: {"A": (0, -1), "B": (1, -1)},     # -z, +y-z
}


def apply_step(m, pos, step):
    return ((pos[0] + step[0]) % m, (pos[1] + step[1]) % m)


def trace_cycle_2d(m, sigma, cycle_idx):
    """Trace a functional graph on Z_m^2. Returns (visited_order, is_hamiltonian)."""
    n = m * m
    steps = STEPS[cycle_idx]
    visited = []
    pos = (0, 0)
    seen = set()
    for _ in range(n):
        if pos in seen:
            return visited, False
        seen.add(pos)
        visited.append(pos)
        step = steps["A"] if sigma[pos] else steps["B"]
        pos = apply_step(m, pos, step)
    return visited, (pos == (0, 0) and len(seen) == n)


def solve_2d(m, time_limit=60, log=False, enumerate_all=False):
    """Find sigma: Z_m^2 -> {A,B} making all 3 cycles Hamiltonian."""
    n = m * m
    verts = list(product(range(m), repeat=2))
    v2i = {v: v[0] * m + v[1] for v in verts}

    model = cp_model.CpModel()

    # sigma[v] = True means A, False means B
    sigma = {v: model.new_bool_var(f"s_{v[0]}_{v[1]}") for v in verts}

    # For each cycle, add circuit constraint
    for c in range(3):
        arcs = []
        steps = STEPS[c]
        for v in verts:
            vi = v2i[v]
            wa = apply_step(m, v, steps["A"])
            wb = apply_step(m, v, steps["B"])
            wai = v2i[wa]
            wbi = v2i[wb]
            if wa == wb:
                arcs.append((vi, wai, model.new_constant(1)))
            else:
                arcs.append((vi, wai, sigma[v]))
                arcs.append((vi, wbi, ~sigma[v]))
        model.add_circuit(arcs)

    # Symmetry breaking: fix sigma at origin
    model.add(sigma[(0, 0)] == 1)  # A at origin

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = 8
    if log:
        solver.parameters.log_search_progress = True

    if enumerate_all:
        solutions = []
        class SolCallback(cp_model.CpSolverSolutionCallback):
            def __init__(self):
                super().__init__()
                self.count = 0
            def on_solution_callback(self):
                self.count += 1
                sol = {v: self.boolean_value(sigma[v]) for v in verts}
                solutions.append(sol)
                if self.count >= 1000:
                    self.stop_search()

        callback = SolCallback()
        solver.parameters.enumerate_all_solutions = True
        status = solver.solve(model, callback)
        return solutions, {"status": solver.status_name(status), "count": len(solutions)}

    t0 = time.time()
    status = solver.solve(model)
    elapsed = time.time() - t0

    stats = {"m": m, "status": solver.status_name(status), "time": round(elapsed, 3)}

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        sol = {v: solver.boolean_value(sigma[v]) for v in verts}
        stats["num_A"] = sum(sol.values())
        stats["num_B"] = n - stats["num_A"]
        return sol, stats
    return None, stats


def sigma_to_dfunc_3d(m, sigma):
    """Convert 2D sigma to full 3D direction function."""
    DERANGEMENT_A = [1, 2, 0]
    DERANGEMENT_B = [2, 0, 1]

    dfunc = {}
    for x in range(m):
        for y in range(m):
            for z in range(m):
                v = (x, y, z)
                s = (x + y + z) % m
                if s != m - 1:
                    dfunc[v] = [0, 1, 2]
                else:
                    if sigma[(y, z)]:
                        dfunc[v] = list(DERANGEMENT_A)
                    else:
                        dfunc[v] = list(DERANGEMENT_B)
    return dfunc


def sigma_to_cycles_3d(m, sigma):
    """Convert 2D sigma to 3 Hamiltonian cycles on Z_m^3."""
    from verify import next_vertex
    dfunc = sigma_to_dfunc_3d(m, sigma)
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
    return cycles


def print_sigma_grid(m, sigma):
    """Print sigma as a grid."""
    print(f"  sigma grid (y=row, z=col, A=1 B=0):")
    for y in range(m):
        row = "  "
        for z in range(m):
            row += "A" if sigma[(y, z)] else "B"
        print(row)


def analyze_sigma_pattern(m, sigma):
    """Check if sigma has algebraic structure."""
    print(f"\nPattern analysis for m={m}:")
    print_sigma_grid(m, sigma)

    # Check row sums (number of A per row)
    row_sums = [sum(sigma[(y, z)] for z in range(m)) for y in range(m)]
    col_sums = [sum(sigma[(y, z)] for y in range(m)) for z in range(m)]
    print(f"  Row A-counts: {row_sums}")
    print(f"  Col A-counts: {col_sums}")

    # Check diagonal sums
    diag_sums = [sum(sigma[((y+d)%m, (d)%m)] for d in range(m)) for y in range(m)]
    print(f"  Diag (y+z const) A-counts: {diag_sums}")

    anti_diag_sums = [sum(sigma[((d)%m, (y-d)%m)] for d in range(m)) for y in range(m)]
    print(f"  Anti-diag (y-z const) A-counts: {anti_diag_sums}")

    # Check M-invariance
    M = lambda y, z: ((-y - z) % m, y % m)
    m_invariant = all(sigma[v] == sigma[M(*v)] for v in sigma)
    print(f"  M-invariant: {m_invariant}")

    # Check if sigma(y,z) depends on y-z mod m
    by_diff = {}
    for (y, z), val in sigma.items():
        d = (y - z) % m
        by_diff.setdefault(d, set()).add(val)
    uniform_by_diff = all(len(v) == 1 for v in by_diff.values())
    print(f"  Depends only on y-z mod m: {uniform_by_diff}")
    if uniform_by_diff:
        pattern = {d: list(v)[0] for d, v in sorted(by_diff.items())}
        print(f"  Pattern: {pattern}")

    # Check if sigma(y,z) depends on y+z mod m
    by_sum = {}
    for (y, z), val in sigma.items():
        s = (y + z) % m
        by_sum.setdefault(s, set()).add(val)
    uniform_by_sum = all(len(v) == 1 for v in by_sum.values())
    print(f"  Depends only on y+z mod m: {uniform_by_sum}")

    # Check if sigma(y,z) depends on some linear combination ay+bz mod m
    for a in range(m):
        for b in range(m):
            if a == 0 and b == 0:
                continue
            by_lin = {}
            for (y, z), val in sigma.items():
                s = (a * y + b * z) % m
                by_lin.setdefault(s, set()).add(val)
            if all(len(v) == 1 for v in by_lin.values()):
                pattern = {s: list(v)[0] for s, v in sorted(by_lin.items())}
                a_vals = [s for s, v in pattern.items() if v]
                print(f"  Linear pattern: sigma depends on ({a}y+{b}z) mod {m}: A at {a_vals}")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("m", type=int, nargs="*", default=[3, 4, 5, 7])
    parser.add_argument("--time-limit", type=int, default=120)
    parser.add_argument("--enumerate", action="store_true")
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()

    for m in args.m:
        print(f"\n{'='*60}")
        print(f"2D diagonal solver for m={m}")
        print(f"{'='*60}")

        if args.enumerate and m <= 5:
            solutions, stats = solve_2d(m, time_limit=args.time_limit, enumerate_all=True)
            print(f"Found {stats['count']} solutions")
            if solutions:
                for i, sol in enumerate(solutions[:5]):
                    print(f"\nSolution {i+1}:")
                    analyze_sigma_pattern(m, sol)
        else:
            sigma, stats = solve_2d(m, time_limit=args.time_limit)
            print(f"Status: {stats['status']}, Time: {stats.get('time', '?')}s")

            if sigma is not None:
                print(f"A count: {stats['num_A']}, B count: {stats['num_B']}")
                analyze_sigma_pattern(m, sigma)

                # Verify 3D decomposition
                from verify import verify_decomposition, print_decomposition_stats
                cycles = sigma_to_cycles_3d(m, sigma)
                ok, msg = verify_decomposition(m, cycles)
                print(f"\n3D Verification: {msg}")

                if ok:
                    print_decomposition_stats(m, cycles)
                    if args.save:
                        from verify import save_decomposition
                        save_decomposition(f"artifacts/diagonal2d_m{m}.json", m, cycles)
            else:
                print("No solution found!")


if __name__ == "__main__":
    main()
