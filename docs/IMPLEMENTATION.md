# IMPLEMENTATION - claudescycles

## Objective

Solve the directed graph decomposition problem in `PROBLEM.md`: decompose the arcs of `G_m` into three directed Hamiltonian cycles for general `m`.

## Baseline

- Problem definition: `PROBLEM.md`
- Current status: initial workflow setup
- Evidence policy: every completed item must cite exact command(s) and outcomes

## Pre-Analysis (Update Before Each Major Item)

- Scope: Completed for the current turn. Remaining work is research on even-`m` generalization rather than baseline implementation.
- Risks: The odd family is proved, but no general even construction is proved; future work needs to avoid overstating what the solver artifacts imply.
- Validation plan: Keep using the deterministic verifier and return-map checks as the acceptance gate for any new family or conjectured even pattern.
- Expected artifacts: Additional even-case analyses or proofs, if discovered.

## Active Punchlist

- [x] P0-01: Bootstrap workflow files (`AGENTS.md`, `docs/IMPLEMENTATION.md`, `WORKLOG.md`, `state/CONTEXT.md`)
- [x] P0-01a: Add `PROBLEM.md` (problem statement)
- [x] P0-02: Add deterministic verifier script for decomposition validity
- [x] P1-01: Build search/solver tooling to find decompositions for small `m` (start with `m=3`)
- [x] P1-02: Discover valid decompositions and identify candidate construction patterns
- [x] P1-03: Test candidate patterns on larger `m` values
- [x] P1-04: Save discovery outputs under `artifacts/` with command provenance
- [x] P2-01: Generalize candidate patterns and validate over broad `m` ranges
- [x] P2-02: Investigate both odd and even `m` cases separately
- [x] P3-01: Attempt a formal proof (or clearly scoped partial proof) in `proofs/`
- [x] P3-02: Catalog failed constructions and failure modes
- [x] P4-01: Write final summary of proven facts, open conjectures, and next experiments

## Deferrals

| ID | Item | Rationale | Risk | Target |
|---|---|---|---|---|

## Validation Log (Commands + Outcomes)

- Bootstrap: workflow files created
- `uv run pytest -q` -> `9 passed in 0.13s` after adding `tests/conftest.py`
- `python scripts/gen_construction_odd.py 5 --out artifacts/solutions/odd_m/m5.json` -> generated verified `m=5` artifact
- `python scripts/verify_decomp.py --json artifacts/solutions/odd_m/m5.json` -> `ok=true`, all cycle checks passed, arc partition violations `0`
- `python scripts/search_cp_sat.py 3 --time-limit 60 --out artifacts/solutions/cpsat_m3.json` -> PASS, verified artifact, solver wall time `0.013s`
- `python scripts/search_cp_sat.py 4 --time-limit 60 --out artifacts/solutions/cpsat_m4.json` -> PASS, verified artifact, solver wall time `0.073s`
- `python scripts/search_cp_sat.py 6 --time-limit 120 --out artifacts/solutions/cpsat_m6.json` -> PASS, verified artifact, solver wall time `1.154s`
- `python scripts/search_cp_sat.py 8 --time-limit 180 --out artifacts/solutions/cpsat_m8.json` -> PASS, verified artifact, solver wall time `2.896s`
- `python scripts/search_cp_sat.py 10 --time-limit 300 --out artifacts/solutions/cpsat_m10.json` -> PASS, verified artifact, solver wall time `9.252s`
- `python scripts/search_cp_sat.py 12 --time-limit 300 --out artifacts/solutions/cpsat_m12.json` -> PASS, verified artifact, solver wall time `2.525s`
- `python scripts/search_cp_sat.py 14 --time-limit 900 --out artifacts/solutions/cpsat_m14.json` -> PASS, verified artifact, solver wall time `8.963s`
- `python scripts/validate_construction_odd.py --m-min 5 --m-max 31 --out artifacts/validation/odd_m_validation.json` -> PASS for all `14` odd values
- `python scripts/check_return_maps_odd.py --m-min 5 --m-max 31 --out artifacts/validation/odd_return_map_checks.json` -> PASS for all `14` odd values
- `uv run pytest -q` -> `9 passed in 0.15s` on the final tree
- `python scripts/verify_decomp.py --json artifacts/solutions/cpsat_m14.json > artifacts/validation/cpsat_m14.verify.json` -> archived verifier JSON for `m=14`
