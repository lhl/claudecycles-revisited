# Final Summary (Current State)

## Proven Facts

1. Deterministic verifier is implemented and reproducible:
   - Hamiltonicity (`m^3` length),
   - arc-disjointness (local `{0,1,2}` partition at each vertex),
   - full arc coverage (equivalent to local partition in this setting).
2. CP-SAT search tooling is implemented and reproducible:
   - verified solutions generated for `m = 3,4,6,8,10,12`.
3. Closed-form odd-`m` construction is implemented:
   - generator: `claudescycles.constructions.construct_decomposition_odd_m`.
4. Formal theorem proved in this repo:
   - for all odd `m >= 5`, the implemented construction yields a valid
     3-cycle Hamilton decomposition of `G_m`.
   - proof document: `proofs/odd_m_construction.md`.

## Computational Evidence

- Odd range validation:
  - `artifacts/validation/odd_construction_validation_m101.json`
  - result: `49/49` odd values in `[5,101]` pass.
- Even sample validation:
  - `artifacts/validation/cpsat_small_m_summary.json`
  - result: sampled `m in {4,6,8,10,12}` all pass via CP-SAT search.

## Open Conjectures / Gaps

1. General even-`m` constructive formula remains unresolved.
2. No full theorem yet covering all `m > 2`.

## Failure Modes Cataloged

See `proofs/failure_modes.md` for:

- local partition failure examples,
- Hamiltonicity failure examples,
- wrong-parameter failures in odd family,
- even-out-of-scope failures for odd template.

## Recommended Next Experiments

1. Mine CP-SAT solutions for even `m` to infer structural invariants in `(u,v,w)`.
2. Attempt a two-parameter family for even `m` with a lift argument analogous to odd case.
3. Add proof-oriented symbolic checks (e.g., derived `X_c` and projected period formulas) as executable assertions.

