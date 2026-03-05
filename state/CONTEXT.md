# CONTEXT CAPSULE

## Objective
Solve the `G_m` arc decomposition problem (see `PROBLEM.md`) with reproducible scripts and proofs.

## Current Best Known
- Workflow scaffolding created.
- Full tooling stack rebuilt and executable:
  - Verifier: `claudescycles/gm.py`, `claudescycles/io.py`, `claudescycles/verify.py`, `scripts/verify_decomp.py`
  - CP-SAT search: `scripts/search_cp_sat.py`
  - Odd construction: `claudescycles/constructions.py`, `scripts/gen_construction_odd.py`
  - Odd batch validator: `scripts/validate_construction_odd.py`
- Proof/docs layer added:
  - `proofs/odd_m_construction.md`
  - `proofs/failure_modes.md`
  - `docs/FINAL_SUMMARY.md`

## Latest Validated Evidence
- CP-SAT verified artifacts:
  - `artifacts/solutions/cpsat_m3.json` (`0.0119s`)
  - `artifacts/solutions/cpsat_m4.json` (`0.0795s`)
  - `artifacts/solutions/cpsat_m6.json` (`1.3411s`)
  - `artifacts/solutions/cpsat_m8.json` (`3.5223s`)
  - `artifacts/solutions/cpsat_m10.json` (`11.1639s`)
  - `artifacts/solutions/cpsat_m12.json` (`3.6371s`)
- Odd construction verified artifacts:
  - `artifacts/constructions/odd_m5.json`, `odd_m7.json`, `odd_m9.json`, `odd_m11.json` all pass.
- Broad odd validation:
  - `artifacts/validation/odd_construction_validation_m101.json`
  - `all_ok=true` for all 49 odd values in `[5, 101]`.

## Open Questions
- Whether an explicit general even-`m` construction can be extracted from CP-SAT artifacts.
- Whether even-case proof can be reduced to a lift criterion analogous to the odd proof.

## Next Actions
1. Mine `artifacts/solutions/cpsat_m*.json` for even-case structural invariants.
2. Propose and test an even-`m` parametric family.
3. Attempt theorem-level proof for the even family if discovered.
