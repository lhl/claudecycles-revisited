# IMPLEMENTATION - claudescycles

## Objective

Solve the directed graph decomposition problem in `PROBLEM.md`: decompose the arcs of `G_m` into three directed Hamiltonian cycles for general `m`.

## Baseline

- Problem definition: `PROBLEM.md`
- Current status: verifier/search/construction/proof pipeline implemented; odd `m>=5` theorem proved, even case still open.
- Evidence policy: every completed item must cite exact command(s) and outcomes

## Pre-Analysis (Update Before Each Major Item)

- Scope: P3 proof pass for discovered odd-`m` construction family, with explicit theorem/lemmas and a bounded partial result statement for unresolved even-`m` general construction.
- Risks: Hidden gap in lift argument (pair-cycle to full Hamilton cycle), incorrect modular arithmetic in `X_c` shift counts, and overclaiming beyond validated range.
- Validation plan: tie every proof claim to executable evidence (`search_cp_sat.py`, `gen_construction_odd.py`, `validate_construction_odd.py`, `verify_decomp.py`) and include unresolved lemmas/conjectures explicitly where a full proof is not available.
- Expected artifacts: `proofs/*.md` theorem write-up, failure-mode catalog for incomplete scopes, and updated summary in project memory files.

## Active Punchlist

- [x] P0-01: Bootstrap workflow files (`AGENTS.md`, `docs/IMPLEMENTATION.md`, `WORKLOG.md`, `state/CONTEXT.md`)
- [x] P0-01a: Add `PROBLEM.md` (problem statement)
- [x] P0-02: Add deterministic verifier script for decomposition validity
- [x] P1-01: Build search/solver tooling to find decompositions for small `m` (start with `m=3`)
- [x] P1-02: Discover valid decompositions and identify candidate construction patterns
- [x] P1-03: Test candidate patterns on larger `m` values
- [x] P1-04: Save discovery outputs under `artifacts/` with command provenance
- [x] P2-01: Generalize candidate patterns and validate over broad `m` ranges (odd `m>=5` construction validated up to `m=101`)
- [x] P2-02: Investigate both odd and even `m` cases separately
- [x] P3-01: Attempt a formal proof (or clearly scoped partial proof) in `proofs/`
- [x] P3-02: Catalog failed constructions and failure modes
- [x] P4-01: Write final summary of proven facts, open conjectures, and next experiments

## Deferrals

| ID | Item | Rationale | Risk | Target |
|---|---|---|---|---|

## Validation Log (Commands + Outcomes)

- Bootstrap: workflow files created
- Verifier smoke (negative cases):
  - `python - <<'PY' ... verify_decomposition(...) ... save_decomposition(...) ... PY`
  - Outcome: verifier rejected both crafted invalid decompositions with explicit errors:
    - arc partition violation (`27/27`)
    - non-Hamiltonian cycle (revisit at step 3)
- CLI smoke:
  - `python scripts/verify_decomp.py artifacts/smoke/invalid_m3_axes.json --json`
  - Outcome: exit code `2`; JSON includes `ok=false`, `arc_partition_ok=true`, and per-cycle Hamiltonicity failure diagnostics.
- CP-SAT small-`m` discovery:
  - `python scripts/search_cp_sat.py 3 --time-limit-s 60 --seed 0 --out artifacts/solutions/cpsat_m3.json`
  - Outcome: found valid decomposition (`wall_time_s=0.011858279`), verified `ok=true`.
- Additional even-case CP-SAT runs:
  - `python scripts/search_cp_sat.py 4 --time-limit-s 120 --seed 0 --out artifacts/solutions/cpsat_m4.json`
  - `python scripts/search_cp_sat.py 6 --time-limit-s 180 --seed 0 --out artifacts/solutions/cpsat_m6.json`
  - `python scripts/search_cp_sat.py 8 --time-limit-s 300 --seed 0 --out artifacts/solutions/cpsat_m8.json`
  - `python scripts/search_cp_sat.py 10 --time-limit-s 600 --seed 0 --out artifacts/solutions/cpsat_m10.json`
  - `python scripts/search_cp_sat.py 12 --time-limit-s 900 --seed 0 --out artifacts/solutions/cpsat_m12.json`
  - Outcome: all solved and verified; summary written to `artifacts/validation/cpsat_small_m_summary.json`.
- Odd construction generation + validation:
  - `python scripts/gen_construction_odd.py 5 --out artifacts/constructions/odd_m5.json`
  - `python scripts/gen_construction_odd.py 7 --out artifacts/constructions/odd_m7.json`
  - `python scripts/gen_construction_odd.py 9 --out artifacts/constructions/odd_m9.json`
  - `python scripts/gen_construction_odd.py 11 --out artifacts/constructions/odd_m11.json`
  - `python scripts/validate_construction_odd.py --m-max 101 --out artifacts/validation/odd_construction_validation_m101.json`
  - Outcome: all generated/validated decompositions pass verifier; odd-range batch reports `all_ok=true` for 49 odd values (`m=5..101`).
- Proof + documentation artifacts:
  - Added `proofs/odd_m_construction.md` (theorem + lemmas for odd `m>=5`).
  - Added `proofs/failure_modes.md` (explicit failed constructions + unresolved even lemmas).
  - Added `docs/FINAL_SUMMARY.md` (proven facts, open conjectures, next experiments).
- Final sanity checks:
  - `python -m compileall claudescycles scripts proofs`
  - `python scripts/verify_decomp.py artifacts/solutions/cpsat_m3.json`
  - `python scripts/verify_decomp.py artifacts/solutions/cpsat_m12.json`
  - `python scripts/verify_decomp.py artifacts/constructions/odd_m11.json`
  - `python scripts/validate_construction_odd.py --m-values 5 7 9 11 --out artifacts/validation/odd_construction_validation_sample.json`
  - Outcome: all checks pass.
