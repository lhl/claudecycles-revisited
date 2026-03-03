# PROBLEM (Replication Input)

Source context: Donald E. Knuth, "Claude's Cycles" (dated 2026-02-28, revised 2026-03-02).

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

Replication mode guidance:

- Use this file as the primary problem statement for blind replication runs.
- Keep extension hints and prior solution details out of scope during pure replication.
