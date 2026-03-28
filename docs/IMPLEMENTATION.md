# IMPLEMENTATION - claudescycles

## Objective

Replicate and extend the decomposition results from `claude-cycles.pdf` with reproducible code, explicit evidence, and restart-safe workflow.

## Baseline

- Primary source: `claude-cycles.pdf`
- Current status: odd-`m` construction + proof replicated; `m=3` counting/exact-cover parity achieved; even-`m` existence certificates found for `m=4,6,8` (general even-`m` construction remains open in our own runs); versioned 2026-03-02 and 2026-03-16 source drafts archived with a dated README/COMPARISON addendum; independent cross-check pending (P2-03)
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
- [x] P2-05: Verify Knuth p.4 symmetry subclaims (see `artifacts/knuth_m3/symmetry_counts.json`)
- [ ] P3-01: Build even-`m` hypothesis backlog and prioritization
- [ ] P3-02: Run iterative even-`m` exploration loop (correctness + benchmark)
- [x] P3-02a: CP-SAT `m=4` HIT (artifacts under `artifacts/even_m4/cpsat_seed0_t60_w8/`)
- [x] P3-02b: CP-SAT `m=6` HIT (artifacts under `artifacts/even_m6/cpsat_seed0_t120_w8/`)
- [x] P3-02c: CP-SAT `m=8` HIT (artifacts under `artifacts/even_m8/cpsat_seed0_t300_w8/`)
- [ ] P3-03: Maintain failure catalog with reasons and rejected families
- [x] P4-00: Add README update section for extensions beyond the note
- [ ] P4-01: Produce final replication-and-extension report (what holds, what is open, next bets)
- [x] P4-02: Audit `COMPARISON.md` against archived session logs and branch artifacts
- [x] P4-03: Archive the 2026-03-16 paper revision and add a dated README/COMPARISON note

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
- `python -m claudescycles.verify --input artifacts/claude_m5.json` -> OK (baseline revalidation)
- `python -m claudescycles.knuth_m3 --out-dir artifacts/knuth_m3` -> OK (baseline revalidation)
- `python -m claudescycles.even_cpsat --m 4 --out-dir artifacts/even_m4/cpsat_seed0_t60_w8 --time-limit-sec 60 --seed 0 --num-workers 8` -> HIT; verifier OK (`artifacts/even_m4/cpsat_seed0_t60_w8/verify.json`)
- `python -m claudescycles.even_cpsat --m 6 --out-dir artifacts/even_m6/cpsat_seed0_t120_w8 --time-limit-sec 120 --seed 0 --num-workers 8` -> HIT; verifier OK (`artifacts/even_m6/cpsat_seed0_t120_w8/verify.json`)
- `python -m claudescycles.even_cpsat --m 8 --out-dir artifacts/even_m8/cpsat_seed0_t300_w8 --time-limit-sec 300 --seed 0 --num-workers 8` -> HIT; verifier OK (`artifacts/even_m8/cpsat_seed0_t300_w8/verify.json`)
- `python -m claudescycles.knuth_m3_symmetry` -> wrote symmetry counts (`artifacts/knuth_m3/symmetry_counts.json`)
- `apply_patch` to update `COMPARISON.md` (session-metric + artifact-count audit) -> success
- `git show cleanroom-5.4:session-analysis/README.md`; `git show cleanroom-5.4:session-analysis/analyze_sessions.py > /tmp/analyze_sessions_54.py`; `git show cleanroom-5.4:session-analysis/codex-sessions/rollout-2026-03-06T04-17-49-019cbf6f-5309-7432-abd8-417875f27e40.jsonl > /tmp/cleanroom54.jsonl`; `python3 /tmp/analyze_sessions_54.py /tmp/cleanroom54.jsonl --json`; `git show cleanroom-5.4:README.md`; `git show cleanroom-5.4:proofs/partial_theorem.md`; `git ls-tree -r --name-only cleanroom-5.4`; `apply_patch` to update `COMPARISON.md` -> success (added cleanroom-5.4 metrics/results and explicit 5.2/5.3/5.4/Opus labeling)
- `curl -L -sS https://www-cs-faculty.stanford.edu/~knuth/papers/claude-cycles.pdf -o /tmp/claude-cycles-2026-03-16.pdf`; `curl -I -L --max-time 20 https://www-cs-faculty.stanford.edu/~knuth/papers/claude-cycles.pdf`; `pdfinfo /tmp/claude-cycles-2026-03-16.pdf`; `diff -u references/claude-cycles.txt /tmp/claude-cycles-2026-03-16.txt` -> confirmed new 6-page `16 Mar 2026` draft and isolated the added postscript material
- `curl -I -L --max-time 20 https://github.com/kim-em/KnuthClaudeLean/`; `curl -L -sS --max-time 20 https://raw.githubusercontent.com/kim-em/KnuthClaudeLean/master/README.md`; `curl -I -L --max-time 20 https://github.com/no-way-labs/residue`; `curl -L -sS --max-time 20 https://raw.githubusercontent.com/no-way-labs/residue/main/README.md`; `curl -L -sS --max-time 20 https://raw.githubusercontent.com/no-way-labs/residue/main/paper/completing_claudes_cycles.tex` -> corroborated live Lean + multi-agent repo links cited by the revised paper
- `curl -I -L --max-time 20 https://cs.stanford.edu/~knuth/even%20solution.py`; `curl -I -L --max-time 20 https://cs.stanford.edu/~knuth/even%20closed%20form.c`; `curl -I -L --max-time 20 https://cs.stanford.edu/~knuth/alternative%20hamiltonian%20decomposition.pdf`; `curl -I -L --max-time 20 https://cs.stanford.edu/~knuth/even%20closed%20form%20proof%20final.pdf` -> all returned `404` on 2026-03-29
- `mkdir -p references/papers`; `cp claude-cycles.pdf references/papers/claude-cycles-2026-03-02.pdf`; `cp references/claude-cycles.txt references/papers/claude-cycles-2026-03-02.txt`; `cp references/claude-cycles.raw.txt references/papers/claude-cycles-2026-03-02.raw.txt`; `cp references/claude-cycles.md references/papers/claude-cycles-2026-03-02.md`; `cp /tmp/claude-cycles-2026-03-16.pdf references/papers/claude-cycles-2026-03-16.pdf`; `pdftotext -layout references/papers/claude-cycles-2026-03-16.pdf references/papers/claude-cycles-2026-03-16.txt`; `pdftotext -raw references/papers/claude-cycles-2026-03-16.pdf references/papers/claude-cycles-2026-03-16.raw.txt`; `shasum -a 256 references/papers/claude-cycles-2026-03-02.pdf references/papers/claude-cycles-2026-03-16.pdf` -> archived both paper versions with checksums
- `python -m claudescycles.knuth_m3 --out-dir /tmp/knuth_m3_20260329` -> reproduced `{11502,1012,996,4554,760}` against the revised paper
- `apply_patch` to update `README.md`, `COMPARISON.md`, `docs/IMPLEMENTATION.md`, `WORKLOG.md`, `state/CONTEXT.md`; `apply_patch` to add `references/papers/README.md` -> success
