# Partial Theorem for `G_m`

## Scope

This document proves an explicit 3-cycle decomposition for every odd `m >= 5`.
It does **not** prove a general theorem for even `m`.
The case `m = 3` is covered only by the exact solver artifact in `artifacts/solutions/cpsat_m3.json`.

## Notation

Write vertices of `G_m` as `(i,j,k) in Z_m^3`.
Let:

- `X(i,j,k) = (i+1,j,k)`
- `Y(i,j,k) = (i,j+1,k)`
- `Z(i,j,k) = (i,j,k+1)`

All coordinates are taken modulo `m`.

Introduce the linear change of variables

`(u,v,w) = (i, i+j, i+j+k)`.

Its inverse is

`(i,j,k) = (u, v-u, w-v)`,

so this is a bijection on `Z_m^3`.
In `(u,v,w)` coordinates the three arc directions become

- `X : (u,v,w) -> (u+1,v+1,w+1)`
- `Y : (u,v,w) -> (u,v+1,w+1)`
- `Z : (u,v,w) -> (u,v,w+1)`

The key simplification is that **every** step increases `w` by `1`.

## Construction

Fix an odd `m >= 5`.
Choose `A in {0,1,...,m-2}` such that

- `gcd(m, 2A+1) = 1`
- `gcd(m, 2A+3) = 1`

Define three cycles `C_0, C_1, C_2` by their outgoing direction at each `(u,v,w)`:

### Cycle `C_0`

- if `w = 0`, use `Z`
- if `1 <= w <= A+1`, use `X` when `v != 0`, and `Y` when `v = 0`
- if `A+2 <= w <= m-1`, use `Y` when `v != 0`, and `X` when `v = 0`

### Cycle `C_1`

- if `w = 1`, use `Z`
- if `w = 0` or `A+2 <= w <= m-1`, use `X` when `v != 0`, and `Y` when `v = 0`
- if `2 <= w <= A+1`, use `Y` when `v != 0`, and `X` when `v = 0`

### Cycle `C_2`

- if `w >= 2`, use `Z`
- if `w = 0` or `w = 1`, use `Y` when `v != 0`, and `X` when `v = 0`

This is exactly the rule implemented in [claudescycles/constructions.py](/home/lhl/github/lhl/claudescycles-revisited/claudescycles/constructions.py).

## Lemma 1

For every odd `m >= 5`, a valid parameter `A` exists.

### Proof

Let `m = prod p_t^{e_t}` be the prime-power factorization.
For a fixed odd prime `p | m`, the bad congruence classes are

- `2A+1 == 0 (mod p)`
- `2A+3 == 0 (mod p)`

Because `p` is odd, `2` is invertible modulo `p`, so these are at most two residue classes modulo `p`.
Therefore the number of admissible residues modulo `p^e` is exactly `p^{e-1}(p-2)`.
By the Chinese remainder theorem, the number of admissible residues modulo `m` is

`N(m) = prod p_t^{e_t-1}(p_t-2)`.

If `m >= 5` is odd, then every factor is at least `1`, and at least one factor is at least `3`.
Hence `N(m) >= 3`.
So there is at least one admissible residue class with representative in `{0,1,...,m-2}`.

## Lemma 2

At every vertex, the three cycles use the three outgoing arcs exactly once.

### Proof

There are three cases.

If `w = 0`, then `C_0` uses `Z`, while `C_1` and `C_2` use `X` and `Y` in some order depending on whether `v = 0`.

If `w = 1`, then `C_1` uses `Z`, while `C_0` and `C_2` use `X` and `Y` in some order.

If `w >= 2`, then `C_2` uses `Z`, while `C_0` and `C_1` use `X` and `Y` in some order.

So at every vertex the directions assigned to `(C_0,C_1,C_2)` are a permutation of `(X,Y,Z)`.
Thus the cycles are arc-disjoint and their union is the full arc set.

## Lemma 3

Let `H = {(u,v,0) : u,v in Z_m}`.
For each cycle `C_r`, its orbit length in `Z_m^3` is `m` times the orbit length of its `m`-step return map on `H`.

### Proof

Every move increases `w` by `1`.
So an orbit starting in `H` returns to `H` exactly every `m` steps and never sooner.
Therefore the original orbit is obtained by lifting the return-map orbit through the `m` successive `w`-levels.

## Lemma 4

The return map `T_2` of `C_2` on `H` is

`T_2(u,v) = (u + eps_2(v), v+2)`,

where `eps_2(v) = 1` for `v in {0,m-1}` and `eps_2(v) = 0` otherwise.

### Proof

Starting from `(u,v,0)`, the cycle uses non-`Z` steps only on rows `w = 0` and `w = 1`.
On row `w = 0`, an `X` step occurs exactly when `v = 0`.
After that first step, the current `v` equals `v+1`.
On row `w = 1`, an `X` step occurs exactly when `v+1 = 0`, namely `v = m-1`.
So the total `u`-increment is `1` exactly for `v in {0,m-1}`, and the total `v`-increment is always `2`.

## Lemma 5

The return map `T_0` of `C_0` on `H` is

`T_0(u,v) = (u + delta_0(v), v-1)`,

where

- `delta_0(v) = A+1` if `v = 1`
- `delta_0(v) = A` if `v in {0,m-A,...,m-1}`
- `delta_0(v) = A+2` otherwise

### Proof

For `C_0`, row `w = 0` is the unique `Z` row.
Hence on row `w` with `1 <= w <= m-1`, the current `v` before the step is `v+w-1`.
Therefore the total `v`-increment over one revolution is `m-1`, which is `-1 mod m`.

Rows `1..A+1` are `X`-dominant: they use `X` unless the current `v` is `0`.
Rows `A+2..m-1` are `Y`-dominant: they use `X` only when the current `v` is `0`.

There is at most one non-`Z` row with current `v = 0`, namely the row satisfying `w == 1-v (mod m)`.

- If `v = 1`, that row is `w = 0`, which is excluded, so no non-`Z` row sees `v = 0`, and the `X` count is the baseline `A+1`.
- If `v = 0` or `v in {m-A,...,m-1}`, the zero row lies inside `1..A+1`, so one `X` is removed from the baseline, giving `A`.
- Otherwise the zero row lies inside `A+2..m-1`, so one extra `X` is added, giving `A+2`.

## Lemma 6

The return map `T_1` of `C_1` on `H` is

`T_1(u,v) = (u + delta_1(v), v-1)`,

where

- `delta_1(v) = m-A-1` if `v = 1`
- `delta_1(v) = m-A` if `v in {m-A,...,m-1}`
- `delta_1(v) = m-A-2` otherwise

### Proof

For `C_1`, row `w = 1` is the unique `Z` row.
So the non-`Z` rows are `w = 0` and `2..m-1`, giving again a total `v`-increment of `m-1`, hence `v -> v-1`.

The `X`-dominant rows are `w = 0` and `A+2..m-1`.
The rows `2..A+1` are `Y`-dominant and switch to `X` only when the current `v` is `0`.

- If `v = 1`, no non-`Z` row sees current `v = 0`, so the `X` count is the baseline `m-A-1`.
- If `v in {m-A,...,m-1}`, the unique zero row lies in `2..A+1`, so the `X` count is increased to `m-A`.
- Otherwise, including `v = 0`, the zero row lies in an `X`-dominant row, so the `X` count drops to `m-A-2`.

## Lemma 7

Each return map `T_r` is a single cycle on `H`.

### Proof

For `T_2`, the second coordinate changes by `+2`.
Because `m` is odd, `2` is invertible modulo `m`, so `v` returns to its starting value only after exactly `m` applications.
Over those `m` applications, the exceptional set `{0,m-1}` is hit exactly once each, so the total `u`-increment is `2`.
Again `2` is invertible modulo `m`, so after `t` full `v`-cycles the first coordinate is `u+2t`, which returns only when `t = m`.
Hence `T_2` has orbit length `m^2`, equal to `|H|`.

For `T_0`, the second coordinate changes by `-1`, so it returns after exactly `m` applications.
Using the piecewise formula above, start from the baseline value `A+2` and subtract `1` once at `v = 1` and subtract `2` at the `A+1` values `v in {0,m-A,...,m-1}`.
Therefore

`sum_v delta_0(v) = m(A+2) - 1 - 2(A+1) == -(2A+3) (mod m)`.

Since `gcd(m,2A+3)=1`, this total `u`-increment is a unit modulo `m`.
So after each full `v`-cycle the first coordinate advances by a unit, and only after `m` such blocks does it return.
Hence `T_0` also has orbit length `m^2`.

For `T_1`, start from the baseline value `m-A-2`, add `1` once at `v = 1`, and add `2` at the `A` values `v in {m-A,...,m-1}`.
Thus

`sum_v delta_1(v) = m(m-A-2) + 1 + 2A == 2A+1 (mod m)`.

Since `gcd(m,2A+1)=1`, the same argument shows that `T_1` has orbit length `m^2`.

So all three return maps are single cycles on `H`.

## Theorem

For every odd `m >= 5`, the construction above decomposes all arcs of `G_m` into three directed Hamiltonian cycles.

### Proof

By Lemma 2, the three direction assignments partition the outgoing arcs at every vertex, hence they are arc-disjoint and cover all arcs.

By Lemma 7, each `m`-step return map is a single cycle on `H`, so by Lemma 3 each lifted orbit in `Z_m^3` has length `m * m^2 = m^3`.
Thus each `C_r` is Hamiltonian.

Therefore the three cycles are Hamiltonian, arc-disjoint, and their union is the whole arc set.

## Computational Corollary

Together with the exact artifact [artifacts/solutions/cpsat_m3.json](/home/lhl/github/lhl/claudescycles-revisited/artifacts/solutions/cpsat_m3.json), decompositions now exist for every odd `m > 2`.

This corollary is **not** a uniform proof for `m = 3`; it combines the theorem above with a checked solver witness.

## Failure Modes and Unresolved Extensions

### Failure Mode F1: the odd proof does not extend directly to even `m`

The `C_2` return map always changes `v` by `+2` and, after one full `v`-cycle, changes `u` by `2`.
When `m` is even, `2` is not invertible in `Z_m`.
So the proof of Lemma 7 breaks immediately: the return map splits into at least two residue classes in the `u` direction.

### Failure Mode F2: the parameter argument degenerates at `m = 3`

Modulo `3`, the admissibility conditions force `A == 2 (mod 3)`.
That leaves no representative in `{0,1,...,m-2} = {0,1}`.
So the row partition used above has no legal parameter and the proof does not cover `m = 3`.

### Unresolved Lemma U1

Find a constructive family for all even `m >= 4` whose return maps on `H` are single cycles.
The current proof gives no such family.

### Unresolved Lemma U2

Either incorporate `m = 3` into a uniform symbolic construction, or prove that any uniform extension of the present row-based family must fail there.
