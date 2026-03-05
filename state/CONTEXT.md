# CONTEXT CAPSULE

## Objective
Solve the `G_m` arc decomposition problem (see `PROBLEM.md`) with reproducible scripts and proofs.

## Current Best Known
- Deterministic verifier, JSON I/O, CP-SAT search script, and explicit odd-`m` construction source have been rebuilt.
- `proofs/partial_theorem.md` proves a decomposition for every odd `m >= 5`.
- Exact CP-SAT artifacts exist for `m=3,4,6,8,10,12,14`; odd construction validation and return-map checks both pass for every odd `m` in `5..31`.
- `README.md` now summarizes the work, current status, reproducibility commands, and future directions.

## Latest Validated Evidence
- `uv run pytest -q` -> `9 passed in 0.13s`
- `python scripts/gen_construction_odd.py 5 --out artifacts/solutions/odd_m/m5.json` -> PASS
- `python scripts/verify_decomp.py --json artifacts/solutions/odd_m/m5.json` -> `ok=true`
- `python scripts/validate_construction_odd.py --m-min 5 --m-max 31 --out artifacts/validation/odd_m_validation.json` -> PASS for `14` odd values
- `python scripts/search_cp_sat.py {3,4,6,8,10,12,14} ...` -> PASS with verified artifacts saved under `artifacts/solutions/`
- `python scripts/check_return_maps_odd.py --m-min 5 --m-max 31 --out artifacts/validation/odd_return_map_checks.json` -> PASS for `14` odd values
- `uv run pytest -q` -> `9 passed in 0.15s`

## Open Questions
- Can the even solver artifacts be normalized into a constructive family?
- Is there a proof that the current row-based odd family cannot extend to even `m`, beyond the immediate `+2` return-map obstruction?
- Can `m=3` be absorbed into a symbolic family instead of handled by a solver witness?

## Next Actions
1. Stage explicit paths and review the staged diff.
2. Commit the full implementation/artifact/proof tree.
3. After this turn, resume even-case pattern extraction from the saved solver witnesses.
