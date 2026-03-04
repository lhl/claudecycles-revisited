# IMPLEMENTATION - claudescycles

## Objective

Replicate and extend the decomposition results from `claude-cycles.pdf` with reproducible code, explicit evidence, and restart-safe workflow.

## Baseline

- Primary source: `claude-cycles.pdf`
- Current status: initial workflow setup
- Evidence policy: every completed item must cite exact command(s) and outcomes
- Problem control files: `PROBLEM.md` (replication), `PROBLEM2.md` (extension)

## Pre-Analysis (Update Before Each Major Item)

- Scope: Implement a deterministic verifier for proposed decompositions of `G_m` into 3 directed Hamiltonian cycles.
- Risks: Off-by-one / vertex indexing bugs; verifier that is too permissive (false positives) or too slow for broad `m` ranges.
- Validation plan: Run verifier on (a) deliberately-invalid toy inputs (must fail with clear reason) and (b) any discovered constructions for small `m` (must pass); record commands+outcomes in `WORKLOG.md`.
- Expected artifacts: `artifacts/verify_smoke.json` (machine-readable verifier run results once a candidate construction exists).

## Active Punchlist

- [x] P0-01: Bootstrap workflow files (`AGENTS.md`, `docs/IMPLEMENTATION.md`, `WORKLOG.md`, `state/CONTEXT.md`)
- [x] P0-01a: Add `PROBLEM.md` (original problem statement for replication-only runs)
- [x] P0-01b: Add `PROBLEM2.md` (extension brief for post-replication work)
- [x] P0-02: Add deterministic verifier script for decomposition validity
- [x] P0-03: Add small-`m` search tooling (CSP/backtracking baseline)
- [x] P1-01: Reproduce odd-`m` validity in a documented range
- [x] P1-02: Reproduce even-`m` failure behavior for current rule set
- [x] P1-03: Save reproduction outputs under `artifacts/` with command provenance
- [x] P1-04: Write odd-`m` proof document (`proofs/`)
- [ ] P2-01: Reproduce `m=3` Hamiltonian cycle count claims from the paper
- [ ] P2-02: Reproduce generalizable subset counts and decomposition counts
- [ ] P2-03: Cross-check counting results with an independent implementation path
- [ ] P3-01: Build even-`m` hypothesis backlog and prioritization
- [ ] P3-02: Run iterative even-`m` exploration loop (correctness + benchmark)
- [ ] P3-03: Maintain failure catalog with reasons and rejected families
- [ ] P4-01: Produce final replication-and-extension report (what holds, what is open, next bets)

## Deferrals

| ID | Item | Rationale | Risk | Target |
|---|---|---|---|---|

## Validation Log (Commands + Outcomes)

- `apply_patch` to create `AGENTS.md` -> success
- `mkdir -p docs state artifacts` -> success
- `cat > docs/IMPLEMENTATION.md` -> success
- `cat > WORKLOG.md` -> success
- `cat > state/CONTEXT.md` -> success
- `apply_patch` to create `PROBLEM.md` -> success
- `apply_patch` to create `PROBLEM2.md` -> success
- `python -m claudescycles.verify --input artifacts/invalid_all0_m3.json` -> FAIL as expected (invalid input rejected)
- `python -m claudescycles.search --m 3 --family csp --out artifacts/csp_m3.json` -> HIT (found valid decomposition)
- `python -m claudescycles.verify --input artifacts/csp_m3.json` -> OK
- `python -m claudescycles.generate --m 5 --family claude --out artifacts/claude_m5.json --verify` -> OK
- `python -m claudescycles.scan --family claude --m-min 3 --m-max 101 --step 2 --out artifacts/claude_scan_odd_3_101.json` -> OK (all odd m in range)
- `python -m claudescycles.scan --family claude --m-min 4 --m-max 100 --step 2 --out artifacts/claude_scan_even_4_100.json` -> FAIL (construction not Hamiltonian for even m in range)
- `apply_patch` to add `proofs/claude_odd_m.md` -> success
