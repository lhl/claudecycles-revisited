# Odd-`m` Construction: Formal Partial Proof

## Scope

This document proves correctness of the construction implemented in
`claudescycles.constructions.construct_decomposition_odd_m` for all odd
`m >= 5`.

For even `m`, this document does **not** provide a general construction;
see `proofs/failure_modes.md` and `docs/FINAL_SUMMARY.md`.

## Setup

Work in `G_m` with vertices `(i,j,k) in Z_m^3` and directed generators:

- `X`: `(i,j,k) -> (i+1,j,k)`
- `Y`: `(i,j,k) -> (i,j+1,k)`
- `Z`: `(i,j,k) -> (i,j,k+1)`

Let

- `u = i`
- `v = i + j`
- `w = i + j + k`

all mod `m`. Then:

- `X`: `(u,v,w) -> (u+1, v+1, w+1)`
- `Y`: `(u,v,w) -> (u,   v+1, w+1)`
- `Z`: `(u,v,w) -> (u,   v,   w+1)`

The implemented family uses a parameter `A` and row set
`R = {2,3,...,A+1} subset Z_m` (as integers in `[0,m-1]`).

## Lemma 1 (Existence of `A`)

For every odd `m >= 5`, there exists `A in {0,...,m-2}` such that

- `gcd(m, 2A+1) = 1`
- `gcd(m, 2A+3) = 1`.

### Proof

Define valid residues
`S = {t in Z_m : gcd(m,t)=1 and gcd(m,t+2)=1}`.

For each odd prime power `p^e || m`, the number of residues mod `p^e`
with `p !| t(t+2)` is `p^e - 2p^{e-1} = p^{e-1}(p-2)` (exclude `t=0,-2 mod p`).
By CRT:

`|S| = prod_{p^e || m} p^{e-1}(p-2)`.

For odd `m > 3`, this product is at least `3`:

- if some `p >= 5` divides `m`, then factor `p^{e-1}(p-2) >= 3`;
- if `m = 3^e` with `e >= 2`, then `|S| = 3^{e-1} >= 3`.

So there exists `t in S` with `t != -1 mod m` (only one class is `-1`).
Since `m` is odd, `2` is invertible mod `m`, so there is unique
`A mod m` with `t = 2A+1`. Because `t != -1`, we have `A != m-1`, hence
`A in {0,...,m-2}` after canonical reduction. QED.

## Lemma 2 (Arc Partition at Each Vertex)

At every vertex, the three cycles assign one each of `X,Y,Z`.

### Proof

Direct case split on `w` in the construction:

- `w=0`: cycle 0 uses `Z`; cycles 1 and 2 use opposite choices of `X/Y`.
- `w=1`: cycle 1 uses `Z`; cycles 0 and 2 use opposite choices of `X/Y`.
- `w>=2`: cycle 2 uses `Z`; cycles 0 and 1 use opposite choices of `X/Y`
  (with branch on `w in R` and `v=0`).

Thus at each vertex the multiset is exactly `{X,Y,Z}`. So arcs are
pairwise disjoint across cycles and their union is the full arc set. QED.

## Lemma 3 (Projected Dynamics on `(v,w)`)

Project each cycle to `(v,w)` (forget `u`). Let projected maps be `T_c`.
For all cycles, `w` increments by `+1` every step.

Projected transitions:

- Cycle 0: `w=0 -> (v,w+1)`, else `(v+1,w+1)`.
- Cycle 1: `w=1 -> (v,w+1)`, else `(v+1,w+1)`.
- Cycle 2: `w>=2 -> (v,w+1)`, else `(v+1,w+1)`.

In one full `m`-step sweep of `w`, net `v` shifts are:

- cycle 0: `-1` (one non-diagonal step),
- cycle 1: `-1` (one non-diagonal step),
- cycle 2: `+2` (two diagonal steps).

Hence projected period lengths are:

- cycle 0: `m^2`,
- cycle 1: `m^2`,
- cycle 2: `m^2 / gcd(m,2)`.

For odd `m`, all three have projected period `m^2`. QED.

## Lemma 4 (Lift Criterion from `(v,w)` to `(u,v,w)`)

Suppose a cycle has projected period `m^2`.
Let `X_c` be the number of `X`-steps in one projected period.
Then after `m^2` steps, `(v,w)` returns and `u` shifts by `X_c (mod m)`.

Therefore full period is
`m^2 * (m / gcd(m, X_c))`.
So full period is `m^3` iff `gcd(m, X_c)=1`. QED.

## Lemma 5 (Closed Forms for `X_c`)

For the implemented odd-`m` construction:

- `X_0 = (a+1)(m-1) + (m-a-2) = m(a+2) - (2a+3)`
- `X_1 = (m-1) + a + (m-a-2)(m-1) = m(m-a-2) + (2a+1)`
- `X_2 = 2`.

So:

- `gcd(m, X_0) = gcd(m, 2a+3)`,
- `gcd(m, X_1) = gcd(m, 2a+1)`,
- `gcd(m, X_2) = gcd(m, 2) = 1` (odd `m`).

Given Lemma 1 choices of `a`, all are coprime to `m`. QED.

## Theorem (Odd `m >= 5`)

For every odd `m >= 5`, `construct_decomposition_odd_m(m)` returns three
directed Hamiltonian cycles of length `m^3` that are arc-disjoint and whose
union is exactly all arcs of `G_m`.

### Proof

By Lemma 1, parameter `a` exists.
By Lemma 2, arcs are partitioned exactly.
By Lemma 3, projected dynamics for each cycle has period `m^2` (odd `m`).
By Lemma 5, each `X_c` is coprime to `m`; by Lemma 4 each lifted cycle has
period `m^3`. Since each cycle is a deterministic functional digraph on
`m^3` vertices with one orbit of size `m^3`, each is Hamiltonian.
Thus all requirements hold. QED.

## Boundary Cases

- `m=3`: this family has no admissible `A` in `0..m-2`; solved here only by
  search artifact (`artifacts/solutions/cpsat_m3.json`).
- even `m`: unresolved for a general closed-form construction in this repo.

