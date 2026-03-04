# Failed / Rejected Construction Attempts

This file records construction ideas that were tested and rejected, with the main reason they fail.
This is meant to prevent repeated work and to document failure modes for the even-m case.

## Simple (mod 3) direction rules

Attempt: for cycle `c`, set direction as `(i+j+k+c) mod 3` (cyclic shift so that directions per vertex are a permutation).

Result: fails Hamiltonicity quickly (short cycles / repeats) for all tested `m` (3..10).

Evidence: ad-hoc generator + `claudescycles.verify.verify_decomposition` (see exploration in the session logs around 2026-03-05).

## Strong symmetry between cycles (coordinate-cycle automorphism)

Attempt: enforce that cycles are images of one cycle under the coordinate permutation `(i,j,k)->(j,k,i)` (and the induced direction permutation).

Result: infeasible for `m=3,4,5` in CP-SAT (no solution exists under this symmetry restriction).

Evidence: CP-SAT snippet with constraints linking cycle 1/2 to cycle 0 via coordinate permutation; solver returned INFEASIBLE.

## Too-simple piecewise-permutation rules using only {i+j==0, i+j+k==0}

Attempt: choose one of a small fixed set of permutations depending only on whether:
- `i+j+k == 0`, else whether `i+j == 0`, else default.

Result: no solutions for `m=3,4,5` under this restriction (brute force over 6^3 choices of permutations on the three regions).

## "Rotate the carry rule" across cycles (naive cyclic symmetry)

Attempt: define cycle 0 as a hierarchical carry-like rule:
- if `i+j+k==0` use `k`,
- else if `i+j==0` use `j`,
- else use `i`,
and define cycles 1 and 2 by cycling the roles of coordinates and planes.

Result: violates arc partition at many vertices (multiple cycles choose the same direction at the same vertex).

## Even-m obstruction for constructions that depend only on (v,w)=(i+j, i+j+k)

This is a key failure mode: if directions for each cycle depend only on `(v,w)` (not on `u=i`), then:
- on the `(v,w)` base cycle, each cycle's `u`-increment over one base period is
  `Delta_c = #{(v,w) where cycle c uses direction 0}`.
- arc partition implies `Delta_0 + Delta_1 + Delta_2 = m^2` (exactly one `dir 0` per `(v,w)` cell).
- for even `m`, Hamiltonicity of each lifted cycle requires `gcd(m,Delta_c)=1`, forcing each `Delta_c` to be odd,
  hence their sum is odd, contradiction since `m^2` is even.

Conclusion: any even-m construction must have essential dependence on the extra coordinate (`u=i`) beyond `(v,w)`.

