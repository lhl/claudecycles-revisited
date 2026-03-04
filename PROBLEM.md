# PROBLEM

Given an integer `m > 2`, define a directed graph `G_m` with vertex set `Z_m^3`:

- Vertices are triples `(i, j, k)` with `0 <= i, j, k < m`.
- Each vertex has exactly three outgoing arcs:
  - `(i, j, k) -> ((i + 1) mod m, j, k)`
  - `(i, j, k) -> (i, (j + 1) mod m, k)`
  - `(i, j, k) -> (i, j, (k + 1) mod m)`

Goal:

Find a general decomposition of all arcs of `G_m` into three directed cycles, each of length `m^3`.

Equivalent requirements:

- Each cycle is Hamiltonian (visits all `m^3` vertices exactly once before returning).
- The three cycles are arc-disjoint.
- Their union is exactly the full arc set of `G_m` (all `3m^3` arcs).

Notes:

- The case `m=2` has been proven impossible (Aubert and Schneider, 1982).
- It is known that decompositions exist for small even `m` (at least `m=4` through `m=16`), but no general construction is known for even `m`.
- The problem is open for both odd and even `m`.
