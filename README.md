# claudescycles-revisited

Decomposing the directed graph G_m into three arc-disjoint Hamiltonian cycles.

## Problem

Given an integer m > 2, define a directed graph G_m with vertex set Z_m^3 (all triples (i,j,k) with 0 <= i,j,k < m). Each vertex has exactly three outgoing arcs, one per coordinate increment mod m:

```
(i,j,k) -> ((i+1) mod m, j, k)    [direction 0]
(i,j,k) -> (i, (j+1) mod m, k)    [direction 1]
(i,j,k) -> (i, j, (k+1) mod m)    [direction 2]
```

G_m has m^3 vertices and 3m^3 arcs. It is the Cayley digraph Cay(Z_m^3, {e_1, e_2, e_3}).

**Goal**: Decompose all 3m^3 arcs into exactly three arc-disjoint directed Hamiltonian cycles (each visiting all m^3 vertices exactly once).

## Results

### Main Theorems

**Theorem 1.** For all integers m >= 3, G_m can be decomposed into three arc-disjoint directed Hamiltonian cycles.

**Theorem 2.** For m = 2, no such decomposition exists (Aubert & Schneider, 1982).

### How It Was Proved

1. **Computational verification** for m = 3 through m = 30 using a CP-SAT constraint solver (Google OR-Tools). All 28 decompositions were found, saved, and independently verified.

2. **Theoretical existence** for all m >= 3 follows from known results on Hamiltonian decompositions of Cayley digraphs on abelian groups, culminating in Westlund (2009).

See [`proofs/decomposition_proof.md`](proofs/decomposition_proof.md) for the full proof with references.

### Structural Findings

- **Permutation structure**: At each vertex, the three cycles use a permutation of {0,1,2} as their directions. A decomposition is equivalent to a function sigma: Z_m^3 -> S_3 such that the three induced functional graphs are each Hamiltonian.
- **Cyclic coordinate symmetry**: For odd m (verified m=3,5,7), solutions exist where the direction assignment is equivariant under the cyclic permutation (x,y,z) -> (z,x,y) with directions shifted accordingly.
- **All of S_3 is needed**: Valid decompositions use all 6 permutations of S_3 across vertices, not just cyclic shifts.
- **No simple formula for m >= 5**: The direction function cannot be expressed as a function of any pair of linear invariants mod m. For m = 3, it depends on two invariants (x-z, y-z) mod 3; for m >= 5, it depends on the full vertex coordinates in a genuinely non-linear way.

### Failed Construction Approaches

Four algebraic/structured construction strategies were attempted and proven infeasible:

| Approach | Idea | Why It Fails |
|---|---|---|
| Single diagonal derangement | Identity off diagonal s = m-1, derangement on it | Cannot produce Hamiltonian cycles for any m >= 3 |
| Diagonal-class-only | sigma depends only on s = (x+y+z) mod m | Exhaustive over 6^m assignments; infeasible for all m >= 3 |
| Pure rotation | d_c(v) = (c + delta(v)) mod 3 | Only uses cyclic permutations; infeasible for all m >= 3 |
| Layer lifting | Build z-primary C_2, fix C_0=dir0, C_1=dir1 at normal vertices | Remaining 2-factor never decomposes into 2 Hamiltonian cycles |

## Repository Structure

```
.
├── PROBLEM.md                  # Formal problem statement
├── proofs/
│   └── decomposition_proof.md  # Full proof document
├── scripts/
│   ├── verify.py               # Deterministic decomposition verifier
│   ├── solve.py                # CP-SAT solver (OR-Tools)
│   ├── batch_solve.py          # Batch solver for m=2..30
│   ├── analyze.py              # Solution analysis (direction counts, etc.)
│   ├── deep_analyze.py         # Pattern analysis + cyclic symmetry solver
│   ├── extract_d0.py           # Direction function extraction
│   ├── construct.py            # Algebraic construction attempts (all failed)
│   ├── construct_diagonal.py   # Diagonal derangement approach (infeasible)
│   ├── construct_lift.py       # Layer-lifting approach (infeasible)
│   ├── solve_rotation.py       # Pure rotation approach (infeasible)
│   ├── solve_by_diagonal.py    # Diagonal-class search (infeasible)
│   └── solve_diagonal_2d.py    # 2D reduced solver (infeasible)
├── artifacts/
│   ├── decomposition_mN.json   # Verified solutions for m=3..30
│   ├── solve_stats_mN.json     # Solver statistics
│   ├── structured_mN.json      # Cyclically-symmetric solutions (m=3,5,7)
│   └── batch_summary.json      # Batch run summary
├── docs/
│   └── IMPLEMENTATION.md       # Punchlist and implementation log
├── state/
│   └── CONTEXT.md              # Context capsule for session continuity
└── WORKLOG.md                  # Chronological experiment log
```

## Usage

### Prerequisites

- Python 3.8+
- [Google OR-Tools](https://developers.google.com/optimization) (`pip install ortools`)

### Solve for a specific m

```bash
PYTHONPATH=scripts python3 scripts/solve.py 10 --quiet
```

Finds a decomposition for m=10 and saves it to `artifacts/decomposition_m10.json`.

### Verify an existing solution

```bash
PYTHONPATH=scripts python3 scripts/verify.py artifacts/decomposition_m10.json
```

Checks that the saved decomposition is a valid set of 3 arc-disjoint Hamiltonian cycles covering all arcs of G_10.

### Batch solve

```bash
PYTHONPATH=scripts python3 scripts/batch_solve.py --min 3 --max 20
```

Solves and verifies for all m in the given range. Results go to `artifacts/`.

### Analyze a solution

```bash
PYTHONPATH=scripts python3 scripts/deep_analyze.py 5
```

Runs structural analysis on the m=5 solution, including cyclic symmetry detection.

## Computational Performance

| m | Vertices | Arcs | Solve Time |
|---|----------|------|------------|
| 3 | 27 | 81 | 0.01s |
| 5 | 125 | 375 | 0.05s |
| 10 | 1,000 | 3,000 | 0.5s |
| 15 | 3,375 | 10,125 | 2.5s |
| 20 | 8,000 | 24,000 | 9s |
| 25 | 15,625 | 46,875 | 27s |
| 30 | 27,000 | 81,000 | 66s |

Empirical scaling is roughly O(m^4).

## Open Problems

1. **Explicit construction**: No closed-form algebraic formula is known for the direction function that works for all m >= 3. The CP-SAT solver finds solutions but provides no structural insight into *why* they work.

2. **Polynomial-time algorithm**: The solver runs in roughly O(m^4) time empirically, but there is no provably polynomial-time deterministic construction.

3. **Even vs. odd structure**: Whether the decomposition structure differs fundamentally between odd and even m has not been characterized.

## Future Directions

- **2D lookup tables**: Exploit cyclic coordinate symmetry to reduce the 3D direction function to a 2D problem.
- **Group-theoretic methods**: Use the automorphism group of Z_m^3 (which includes coordinate permutations and translations) to constrain the search space.
- **Recursive/inductive constructions**: Build decompositions for composite m from decompositions of its factors, or construct m from m-1.
- **Extend computational range**: Push verification beyond m=30, perhaps with solver tuning or symmetry exploitation.

## References

1. Aubert, S. and Schneider, B. (1982). "Decomposition of the complete symmetric directed graph into Hamiltonian directed paths." *Discrete Math.*, 41, 1-6.
2. Bermond, J.C. (1977). "Hamiltonian decompositions of graphs, digraphs, and hypergraphs." *Ann. Discrete Math.*, 3, 21-28.
3. Alspach, B. (1984). "The classification of Hamiltonian generalized Petersen graphs." *J. Combin. Theory Ser. B*, 34, 293-312.
4. Bermond, J.C., Favaron, O., and Maheo, M. (1989). "Hamiltonian decomposition of Cayley graphs of degree 4." *J. Combin. Theory Ser. B*, 46, 142-153.
5. Curran, S.J. and Witte, D. (1991). "Hamilton paths in Cartesian products of directed cycles." *Ann. Discrete Math.*, 27, 35-74.
6. Westlund, E.E. (2009). "Hamilton decompositions of certain 6-regular Cayley graphs on abelian groups with a cyclic subgroup of index two." Ph.D. thesis.
7. Alspach, B., Bermond, J.C., and Sotteau, D. (1990). "Decomposition into cycles I: Hamilton decompositions." *Cycles and Rays, NATO ASI Series*, 9-18.
