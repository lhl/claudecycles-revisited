# IMPLEMENTATION - claudescycles

## Objective

Replicate and extend the decomposition results from `claude-cycles.pdf` with reproducible code, explicit evidence, and restart-safe workflow.

## Baseline

- Primary source: `claude-cycles.pdf`
- Current status: odd-`m` construction + proof replicated; `m=3` counting/exact-cover parity achieved; even-`m` remains open; independent cross-check pending (P2-03)
- Evidence policy: every completed item must cite exact command(s) and outcomes
- Problem control files: `PROBLEM.md` (replication), `PROBLEM-3-extension.md` (extension)

## Pre-Analysis (Update Before Each Major Item)

- Scope: Implement a deterministic verifier for proposed decompositions of `G_m` into 3 directed Hamiltonian cycles.
- Risks: Off-by-one / vertex indexing bugs; verifier that is too permissive (false positives) or too slow for broad `m` ranges.
- Validation plan: Run verifier on (a) deliberately-invalid toy inputs (must fail with clear reason) and (b) any discovered constructions for small `m` (must pass); record commands+outcomes in `WORKLOG.md`.
- Expected artifacts: `artifacts/verify_smoke.json` (machine-readable verifier run results once a candidate construction exists).

## Active Punchlist

- [x] P0-01: Bootstrap workflow files (`AGENTS.md`, `docs/IMPLEMENTATION.md`, `WORKLOG.md`, `state/CONTEXT.md`)
- [x] P0-01a: Add `PROBLEM.md` (original problem statement for replication-only runs)
- [x] P0-01b: Add `PROBLEM-3-extension.md` (extension brief for post-replication work; formerly `PROBLEM2.md`)
- [x] P0-02: Add deterministic verifier script for decomposition validity
- [x] P0-03: Add small-`m` search tooling (CSP/backtracking baseline)
- [x] P1-01: Reproduce odd-`m` validity in a documented range
- [x] P1-02: Reproduce even-`m` failure behavior for current rule set
- [x] P1-03: Save reproduction outputs under `artifacts/` with command provenance
- [x] P1-04: Write odd-`m` proof document (`proofs/`)
- [x] P1-05: Write `README.md` comparing against `claude-cycles.pdf` (formerly `REVIEW.md`)
- [x] P1-06: Add `claude-cycles.pdf` + `pdftotext` extracts under `references/`
- [x] P2-01: Reproduce `m=3` Hamiltonian cycle count claims from the paper
- [x] P2-02: Reproduce generalizable subset counts and decomposition counts
- [ ] P2-03: Cross-check counting results with an independent implementation path
- [x] P2-04: Add proof-note + followup tracker for Knuth `m=3` results (`PROBLEM-2-followup.md`, formerly `FOLLOWUP.md`)
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
- `apply_patch` to create `PROBLEM2.md` -> success (renamed to `PROBLEM-3-extension.md`)
- `python -m claudescycles.verify --input artifacts/invalid_all0_m3.json` -> FAIL as expected (invalid input rejected)
- `python -m claudescycles.search --m 3 --family csp --out artifacts/csp_m3.json` -> HIT (found valid decomposition)
- `python -m claudescycles.verify --input artifacts/csp_m3.json` -> OK
- `python -m claudescycles.generate --m 5 --family claude --out artifacts/claude_m5.json --verify` -> OK
- `python -m claudescycles.scan --family claude --m-min 3 --m-max 101 --step 2 --out artifacts/claude_scan_odd_3_101.json` -> OK (all odd m in range)
- `python -m claudescycles.scan --family claude --m-min 4 --m-max 100 --step 2 --out artifacts/claude_scan_even_4_100.json` -> FAIL (construction not Hamiltonian for even m in range)
- `apply_patch` to add `proofs/claude_odd_m.md` -> success
- `pdftotext -layout claude-cycles.pdf references/claude-cycles.txt` -> success
- `pdftotext -layout -f 1 -l 1 claude-cycles.pdf -` -> used for review cross-checking
- `python - <<'PY' ... PY` (calls `claudescycles.m3_cycles.list_hamiltonian_cycles_m3`) -> count=11502 (matches paper)
- `python - <<'PY' ... PY` (counts `generalize_to_5=1012`, `generalize_to_5_and_7=996`) -> matches paper
- `python - <<'PY' ... PY` (exact cover) -> `decompositions_total=4554`, `decompositions_all_generalizable=760` (matches paper)
- `python -m claudescycles.knuth_m3 --out-dir artifacts/knuth_m3` -> OK; outputs written under `artifacts/knuth_m3/`
- `apply_patch` to add `proofs/claude_like_generalizable.md` -> success
- `apply_patch` to add `FOLLOWUP.md` -> success (renamed to `PROBLEM-2-followup.md`)
