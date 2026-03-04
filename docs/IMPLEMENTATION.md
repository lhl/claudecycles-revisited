# IMPLEMENTATION - claudescycles

## Objective

Solve the directed graph decomposition problem in `PROBLEM.md`: decompose the arcs of `G_m` into three directed Hamiltonian cycles for general `m`.

## Baseline

- Problem definition: `PROBLEM.md`
- Current status: odd `m>=5` solved with a proved explicit construction; even-`m` construction still open (CP-SAT evidence archived up to `m=16`)
- Evidence policy: every completed item must cite exact command(s) and outcomes

## Pre-Analysis (Update Before Each Major Item)

- Scope: Even-m investigation (search for a general even-m construction; catalog failures if no clean pattern emerges).
- Risks: CP-SAT scale blowup for larger m; overfitting to small-m patterns; hidden symmetry assumptions; proof gaps for even m.
- Validation plan: extend `scripts/search_cp_sat.py` to more even m; verify all candidates with `scripts/verify_decomp.py`; attempt to synthesize an explicit rule and validate over ranges; record failures in a dedicated doc under `docs/`.
- Expected artifacts: additional `artifacts/solutions/cpsat_m*.json` and `*.verify.json`; a machine-readable pattern fit / rule description (if found); `docs/FAILED_ATTEMPTS.md`.

## Active Punchlist

- [x] P0-01: Bootstrap workflow files (`AGENTS.md`, `docs/IMPLEMENTATION.md`, `WORKLOG.md`, `state/CONTEXT.md`)
- [x] P0-01a: Add `PROBLEM.md` (problem statement)
- [x] P0-02a: Implement deterministic verifier script for decomposition validity
- [x] P0-02b: Validate verifier on at least one PASS decomposition instance (from solver output)
- [x] P1-01: Build search/solver tooling to find decompositions for small `m` (start with `m=3`)
- [x] P1-02: Discover valid decompositions and identify candidate construction patterns
- [x] P1-03: Test candidate patterns on larger `m` values (odd m validated up to 101)
- [x] P1-04: Save discovery outputs under `artifacts/` with command provenance
- [x] P2-01a: Generalize odd-m pattern: implement + validate + proof (odd m>=5)
- [ ] P2-01b: Generalize even-m pattern (open)
- [x] P2-02a: Investigate odd m (solved for odd m>=5; m=3 via explicit solution)
- [ ] P2-02b: Investigate even m (open)
- [x] P3-01a: Formal proof for odd m>=5 in `proofs/`
- [ ] P3-01b: Even-m proof or strongest partial theorem (open)
- [x] P3-02: Catalog failed constructions and failure modes (`docs/FAILED_ATTEMPTS.md`)
- [x] P4-01: Write final summary of proven facts, open conjectures, and next experiments (`README.md`)

## Deferrals

| ID | Item | Rationale | Risk | Target |
|---|---|---|---|---|

## Validation Log (Commands + Outcomes)

- Bootstrap: workflow files created
- Verifier syntax: `python -m py_compile claudescycles/*.py scripts/verify_decomp.py` (OK)
- Verifier negative fixture: `python scripts/verify_decomp.py artifacts/examples/trivial_m3_nonham.json` (FAIL as expected; non-Hamilton)
- CP-SAT solve m=3: `python scripts/search_cp_sat.py 3 --time-limit-s 60 --seed 0 --overwrite` (FOUND; wrote `artifacts/solutions/cpsat_m3.json`)
- Verifier PASS: `python scripts/verify_decomp.py artifacts/solutions/cpsat_m3.json` (PASS)
- CP-SAT batch m=4..8: ran `scripts/search_cp_sat.py` for m=4,5,6,7,8 and saved PASS solutions + `*.verify.json` reports under `artifacts/solutions/`.
- Odd-m construction validation: `time -p python scripts/validate_construction_odd.py --m-max 101` (PASS; wrote `artifacts/validation/odd_construction_validation.json`)
- CP-SAT even-m evidence: solved and verified m=10,12,14,16; PASS reports under `artifacts/solutions/` (m=16 required `--seed 1`).
