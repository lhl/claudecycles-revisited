# CONTEXT CAPSULE

## Objective
Solve the `G_m` arc decomposition problem (see `PROBLEM.md`) with reproducible scripts and proofs.

## Current Best Known
- Workflow scaffolding created.
- Deterministic verifier implemented (`scripts/verify_decomp.py`) for direction-table decompositions; negative fixture fails as expected.
- CP-SAT search tool implemented (`scripts/search_cp_sat.py`) and verified PASS decompositions found for `m=3..8` under `artifacts/solutions/` with accompanying `*.verify.json` reports.
- Explicit proven construction implemented for odd `m>=5` (`claudescycles/constructions.py`, `scripts/gen_construction_odd.py`) with proof in `proofs/odd_m_construction.md`. Broad validation saved in `artifacts/validation/odd_construction_validation.json`.
- CP-SAT solutions verified for even m up to 16 under `artifacts/solutions/` (m=10,12,14,16 added beyond the earlier m<=8 set).

## Latest Validated Evidence
- `python scripts/verify_decomp.py artifacts/examples/trivial_m3_nonham.json` fails as expected (cycles not Hamiltonian).
- `python scripts/verify_decomp.py artifacts/solutions/cpsat_m{3,4,5,6,7,8}.json` all pass; machine-readable reports saved.

## Open Questions
- Even-m case: can we find a general construction, or at least the strongest partial theorem + clearly stated unresolved lemmas?
- Can we algorithmically infer a structured even-m rule from the archived CP-SAT solutions (e.g. small arithmetic feature sets)?

## Next Actions
1. Attempt to synthesize an even-m construction rule from `artifacts/solutions/` (avoid the known even-m obstruction for rules depending only on (v,w)=(i+j,i+j+k); see `docs/FAILED_ATTEMPTS.md`).
2. Extend CP-SAT evidence to larger even `m` (record seed sensitivity + runtimes in `WORKLOG.md`).
3. Strengthen partial theorems: prove impossibility for additional restricted families and keep cataloging failures.
