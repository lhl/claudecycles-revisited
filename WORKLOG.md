# WORKLOG - claudescycles

## 2026-03-04

### Task: Workflow bootstrap
- Plan: Create shared-memory and execution-control docs for autonomous replicate/extend work.
- Commands: `apply_patch` for `AGENTS.md`; `mkdir -p docs state artifacts`; `cat > docs/IMPLEMENTATION.md`; `cat > WORKLOG.md`; `cat > state/CONTEXT.md`
- Result: Workflow files created with punchlist and restart templates.
- Decision: Continue with P0-02 (deterministic verifier script).

### Task: Problem file split for phased runs
- Plan: Add one file for blind replication (`PROBLEM.md`) and one for extension mode (`PROBLEM2.md`).
- Commands: `apply_patch` to add `PROBLEM.md`; `apply_patch` to add `PROBLEM2.md`; `apply_patch` to update `docs/IMPLEMENTATION.md`; `apply_patch` to update `WORKLOG.md`; `apply_patch` to update `state/CONTEXT.md`
- Result: Phase split is now explicit and can support "move PDF + PROBLEM2 out, run replication, then restore extension mode".
- Decision: Proceed to P0-02 with replication run driven by `PROBLEM.md` only.

### Task: Deterministic decomposition verifier (P0-02)
- Plan: Implement a verifier that checks (1) each of 3 cycles is Hamiltonian of length `m^3`, (2) cycles are arc-disjoint, and (3) union covers all arcs.
- Commands: `python - <<'PY' ... PY` (writes `artifacts/invalid_all0_m3.json`); `python -m claudescycles.verify --input artifacts/invalid_all0_m3.json`
- Result: Verifier correctly rejects an intentionally invalid decomposition for `m=3` with explicit failure reasons.
- Decision: Mark P0-02 complete; next build search tooling to discover a passing decomposition and add a positive artifact.

### Task: CSP-based small-m search + first positive instance
- Plan: Implement a deterministic CSP/backtracking solver for small `m` that enforces indegree=1 constraints for all 3 cycles (with per-vertex permutation coupling), then filter solutions by Hamiltonicity using the verifier.
- Commands: `python -m claudescycles.search --m 3 --family csp --out artifacts/csp_m3.json`; `python -m claudescycles.verify --input artifacts/csp_m3.json --json-out artifacts/verify_csp_m3.json`
- Result: Found a valid decomposition for `m=3` (`artifacts/csp_m3.json`), and verifier reports `OK`.
- Decision: Use the `m=3` solution to infer structural patterns; next attempt to solve additional small `m` (especially `m=4,5,6,7`) and look for a general family.

### Task: CSP scaling experiments (m=4,5) + propagation optimization
- Plan: Try CSP solver on `m=4` and `m=5`; if too slow, optimize constraint propagation to start from affected constraints only.
- Commands: `time python -m claudescycles.search --m 4 --family csp --max-nodes 50000`; `time python -m claudescycles.search --m 5 --family csp --max-nodes 30000`; `time python -m claudescycles.search --m 5 --family csp --max-nodes 200000`
- Result: `m=4` returned `NO_HIT` within 50k nodes (~10s). `m=5` returned `NO_HIT` within 30k nodes (~10s) and still `NO_HIT` within 200k nodes (~59s). (Node budgets are not completeness proofs.)
- Decision: Stop relying on blind CSP scaling; look for a parametric construction and then validate it.

### Task: Recover construction + proof sketch from `claude-cycles.pdf`
- Plan: Extract the PDF text locally and locate the explicit odd-`m` construction and its proof outline.
- Commands: `pdftotext -layout ../claude-cycles.pdf - | sed -n '1,120p'`; `pdftotext -layout ../claude-cycles.pdf - | sed -n '120,260p'`
- Result: Found a concrete piecewise-per-vertex permutation rule (in C-like pseudocode) that yields a valid decomposition for odd `m` (reported tested up to `m=101`), plus a proof strategy for Hamiltonicity of each cycle (cycle 0 in main text; cycles 1–2 in Appendix).
- Decision: Implement the PDF construction as a first-class generator in code, validate over a broad odd-`m` range with our verifier, and write a formal proof document following the lemma structure in the note.

### Task: Implement + validate Claude/Knuth odd-m construction
- Plan: Encode the piecewise per-vertex permutation rule from the PDF as a generator; then validate correctness over broad odd `m` and demonstrate failure on even `m`.
- Commands: `python -m claudescycles.generate --m 3 --family claude --out artifacts/claude_m3.json --verify --verify-json-out artifacts/verify_claude_m3.json`; `python -m claudescycles.generate --m 5 --family claude --out artifacts/claude_m5.json --verify --verify-json-out artifacts/verify_claude_m5.json`; `python -m claudescycles.generate --m 7 --family claude --out artifacts/claude_m7.json --verify --verify-json-out artifacts/verify_claude_m7.json`; `python -m claudescycles.generate --m 4 --family claude --out artifacts/claude_m4.json --verify --verify-json-out artifacts/verify_claude_m4.json`
- Result: Construction verifies `OK` for `m=3,5,7` and fails for `m=4` (cycles repeat early; not Hamiltonian).
- Decision: Run range scans and archive machine-readable evidence under `artifacts/`.

### Task: Broad-range validation scans (odd vs even)
- Plan: Scan odd `m` through 101 (as reported in the PDF) and scan even `m` through 100 to characterize failure behavior.
- Commands: `python -m claudescycles.scan --family claude --m-min 3 --m-max 101 --step 2 --out artifacts/claude_scan_odd_3_101.json`; `python -m claudescycles.scan --family claude --m-min 4 --m-max 100 --step 2 --out artifacts/claude_scan_even_4_100.json`
- Result: Odd scan returns `OK` for every odd `m` in `[3,101]`. Even scan returns `FAIL` (construction not Hamiltonian for even `m`).
- Decision: Write proof document for odd `m`; keep even-`m` status explicitly open (construction fails, and PDF notes general even case unresolved).

### Task: Write formal proof document + restore extension brief
- Plan: Create `proofs/` theorem/lemmas writeup for the odd-`m` construction, and add back the missing `PROBLEM2.md` extension brief referenced by repo memory files.
- Commands: `apply_patch` to add `proofs/claude_odd_m.md`; `apply_patch` to add `PROBLEM2.md`
- Result: Proof document written with theorem + lemmas for cycles 0–2 (odd `m`) and an explicit note that the construction fails for even `m`. Extension brief restored and points to code + artifacts.
- Decision: Next: tighten any proof gaps found during review; then consolidate final repo status in `docs/IMPLEMENTATION.md` and `state/CONTEXT.md`.

### Task: Compare repo against Knuth note; write `REVIEW.md`
- Plan: Read `claude-cycles.pdf`, cross-check our code/artifacts/proof against Knuth’s construction + claims, and write an executive-summary review with explicit gaps.
- Commands: `pdftotext -layout claude-cycles.pdf - | sed -n '1,120p'`; `pdftotext -layout claude-cycles.pdf /tmp/claude-cycles.txt`; `rg -n \"Appendix|Cycle 1|Cycle 2|Hamiltonian|Lemma|Theorem|bump\" /tmp/claude-cycles.txt | head -n 80`; `sed -n '145,230p' /tmp/claude-cycles.txt`; `sed -n '220,320p' /tmp/claude-cycles.txt`; `sed -n '1,220p' claudescycles/claude.py`; `sed -n '1,240p' claudescycles/verify.py`; `sed -n '1,260p' proofs/claude_odd_m.md`
- Result: Added `REVIEW.md` summarizing alignment (odd-`m` rule + proof strategy + scan range) and enumerating remaining gaps (even-`m` recovery/certificates; `m=3` counting + exact cover reproduction).
- Decision: Keep. Next: implement P2 counting results and strengthen even-`m` search to recover known small cases with certificates.

### Task: Add paper + extracted text/MD + citation pass in `REVIEW.md`
- Plan: Check in `claude-cycles.pdf`, store deterministic `pdftotext` extractions for fast grep/LLM ingestion, and add page/code-line references throughout `REVIEW.md`.
- Commands: `pdfinfo claude-cycles.pdf`; `pdftotext -layout claude-cycles.pdf references/claude-cycles.txt`; `pdftotext -raw claude-cycles.pdf references/claude-cycles.raw.txt`; `python - <<'PY' ... PY` (writes `references/claude-cycles.md`); `nl -ba claudescycles/claude.py | sed -n '1,120p'`; `nl -ba claudescycles/verify.py | sed -n '1,260p'`; `nl -ba claudescycles/scan.py | sed -n '1,220p'`; `nl -ba claudescycles/search.py | sed -n '1,120p'`
- Result: `references/` now contains stable text/markdown extracts; `REVIEW.md` now cites paper pages and key code entrypoints with line numbers.
- Decision: Keep; commit these sources + review updates as a single logical unit.

### Task: Enumerate all Hamiltonian cycles for `m=3` (count replication)
- Plan: Implement a rooted DFS enumerator for directed Hamiltonian cycles in `G_3`, returning each cycle as a per-vertex direction function; confirm Knuth’s reported total count.
- Commands: `python - <<'PY'\nfrom claudescycles.m3_cycles import list_hamiltonian_cycles_m3\n\ncycles = list_hamiltonian_cycles_m3()\nprint('count', len(cycles))\nprint('unique_arc_masks', len({c.arc_mask for c in cycles}))\nPY`
- Result: `count 11502`, `unique_arc_masks 11502` (matches Knuth 2026, p.4).
- Decision: Next implement “generalizable” lifting (counts 1012/996) and exact-cover decomposition counting (4554/760), with machine-readable outputs in `artifacts/`.

### Task: Reproduce “generalizable” counts for `m=3` cycles
- Plan: Implement Knuth’s `x^` lifting from `m=3` cycles to odd `m` and reproduce the reported counts for `m=5` and `m=7`.
- Commands: `python - <<'PY'\nfrom time import perf_counter\n\nfrom claudescycles.generalize import generalizes_m3_cycle_to_m\nfrom claudescycles.m3_cycles import iter_hamiltonian_cycles_m3\n\nc5 = 0\nc5c7 = 0\nn = 0\n\nt0 = perf_counter()\nfor cyc in iter_hamiltonian_cycles_m3():\n    n += 1\n    ok5 = generalizes_m3_cycle_to_m(base_dirs=cyc.dirs, m=5)\n    if ok5:\n        c5 += 1\n        ok7 = generalizes_m3_cycle_to_m(base_dirs=cyc.dirs, m=7)\n        if ok7:\n            c5c7 += 1\n\ndt = perf_counter() - t0\nprint('total', n)\nprint('generalize_to_5', c5)\nprint('generalize_to_5_and_7', c5c7)\nprint('elapsed_sec', dt)\nPY`
- Result: `generalize_to_5 1012`, `generalize_to_5_and_7 996` (matches Knuth 2026, p.4). Runtime ~1.7s on this machine.
- Decision: Next: implement exact-cover counting for decompositions (expect 4554 total; 760 using only the 996 “generalizable” cycles).

### Task: Reproduce exact-cover decomposition counts for `m=3` (4554 total; 760 generalizable-only)
- Plan: Use arc-mask exact cover (A,B disjoint implies unique complement C) to count `3×3×3` decompositions from the full Hamiltonian-cycle list; then count decompositions comprised only of the 996 “generalizable” cycles.
- Commands: `python - <<'PY'\nfrom time import perf_counter\n\nfrom claudescycles.generalize import generalizes_m3_cycle_to_m\nfrom claudescycles.m3_cycles import list_hamiltonian_cycles_m3\nfrom claudescycles.m3_decompositions import (\n    count_m3_decompositions_in_subset,\n    list_m3_decompositions_from_arc_masks,\n)\n\ncycles = list_hamiltonian_cycles_m3()\nmasks = [c.arc_mask for c in cycles]\n\nallowed: set[int] = set()\nfor idx, cyc in enumerate(cycles):\n    if generalizes_m3_cycle_to_m(base_dirs=cyc.dirs, m=5) and generalizes_m3_cycle_to_m(\n        base_dirs=cyc.dirs, m=7\n    ):\n        allowed.add(idx)\nprint('allowed_generalizable', len(allowed))\n\nt0 = perf_counter()\ndecomps = list_m3_decompositions_from_arc_masks(masks)\ndt = perf_counter() - t0\nprint('decompositions_total', len(decomps))\nprint('elapsed_sec', dt)\n\nprint('decompositions_all_generalizable', count_m3_decompositions_in_subset(decomps, allowed=allowed))\nPY`
- Result: `allowed_generalizable 996`; `decompositions_total 4554`; `decompositions_all_generalizable 760` (matches Knuth 2026, p.4). Exact-cover enumeration runtime ~1.4s on this machine.
- Decision: Next: add a single CLI to reproduce all of Knuth’s `m=3` counts and write `artifacts/` outputs; then write a proof-note for the “Claude-like iff generalizable” theorem and a `FOLLOWUP.md` tracker.

### Task: Archive feature-parity outputs for Knuth `m=3` counts
- Plan: Provide a single deterministic CLI that reproduces the `m=3` paper counts and writes machine-readable outputs under `artifacts/`.
- Commands: `python -m claudescycles.knuth_m3 --out-dir artifacts/knuth_m3`; `head -n 40 artifacts/knuth_m3/counts.json`; `ls -la artifacts/knuth_m3`
- Result: Wrote `artifacts/knuth_m3/counts.json`, `artifacts/knuth_m3/generalizable_cycle_masks.json`, and `artifacts/knuth_m3/decompositions.json` with counts `{11502,1012,996,4554,760}` matching Knuth 2026 (p.4).
- Decision: Proceed to proof/documentation parity: add a proof-note for the “Claude-like iff generalizable” theorem, then write `FOLLOWUP.md` summarizing current status + next steps.

### Task: Proof/documentation feature parity (theorem note + followup tracker)
- Plan: Add a proof note formalizing Knuth’s “Claude-like iff generalizable” theorem and create a single followup tracker summarizing parity + remaining gaps.
- Commands: `apply_patch` to add `proofs/claude_like_generalizable.md`; `apply_patch` to add `FOLLOWUP.md`
- Result: Proof-note added and tied to implementation (`claudescycles/generalize.py`, `claudescycles/knuth_m3.py`); followup tracker added with repro commands and parity checklist.
- Decision: Next: stage/commit the new counting code + artifacts + docs as one logical change; then proceed to P3 even-`m` exploration and/or P2-03 independent cross-check.

### Task: Post-rename doc consistency (README methodology + followup links)
- Plan: After renaming `REVIEW.md`→`README.md`, `FOLLOWUP.md`→`PROBLEM-2-followup.md`, and `PROBLEM2.md`→`PROBLEM-3-extension.md`, update docs so the methodology and pointers remain technically correct and restart-safe.
- Commands: `git status -sb`; `rg -n "PROBLEM-1-prompt" README.md`; `sed -n '60,140p' README.md`; `sed -n '340,430p' README.md`; `rg -n "REVIEW\\.md|FOLLOWUP\\.md|PROBLEM2\\.md"`; `apply_patch` to update `PROBLEM-2-followup.md`; `apply_patch` to update `docs/IMPLEMENTATION.md`; `apply_patch` to update `state/CONTEXT.md`
- Result: `README.md` now embeds the verbatim one-shot prompt (`PROBLEM-1-prompt.md`) in a top-level Methodology section and ends with a link/summary to `PROBLEM-2-followup.md`. Repo memory files now reference the renamed documents (`README.md`, `PROBLEM-2-followup.md`, `PROBLEM-3-extension.md`).
- Decision: Keep; stage/commit doc-only changes after a quick staged-diff review.

### Task: Clarify “clean-room” timeline vs when the note was consulted
- Plan: Use git history + `WORKLOG.md` evidence to verify when Knuth’s note was consulted vs when `claude-cycles.pdf` was checked into the repo; then tighten the README conclusion/methodology wording accordingly.
- Commands: `git log --oneline --decorate --graph -n 40`; `git show --name-status --oneline 3751296`; `git show --name-status --oneline fe26f6a`; `git show 3751296:WORKLOG.md | rg -n 'Recover construction|pdftotext|claude-cycles\\.pdf'`; `apply_patch` to update `README.md`
- Result: `claude-cycles.pdf` was checked into the repo in commit `fe26f6a` (after the initial implementation commit `3751296`), but `WORKLOG.md` in `3751296` records consulting an out-of-repo `../claude-cycles.pdf` during the initial session to obtain the explicit odd-`m` construction.
- Decision: Keep; README now defines “clean-room” as “clean-room start” and explicitly attributes the odd-`m` construction/proof to the post-search consult of the note (with commit provenance for reproducibility).

### Task: Validate README session-analysis notes (PDF access + 45m UI)
- Plan: Cross-check the README’s “clean-room boundary leak” narrative against machine-parsed Codex session logs, and reconcile the “~45 minutes” UI observation with active vs wall time.
- Commands: `python3 session-analysis/analyze_claudescycles.py --phases-only | sed -n '1,220p'`; `apply_patch` to refine wording in `README.md`
- Result: Phase 0 wall time is ~6h, but active time is ~47m; the timeline shows `find ..` then `pdftotext -layout ../claude-cycles.pdf` around 19:31 UTC, matching the `WORKLOG.md` narrative. The ~45m UI number aligns with “active time,” not wall time.
- Decision: Keep; leave session-analysis timeline in README, but word it as “knew the PDF existed and could go looking for it,” and explicitly note active vs wall time.

### Task: Update session-analysis docs with active-time note
- Plan: Make `session-analysis/README.md` explicitly record the Phase 0 active time so the “~45m UI” observation is reconciled in the same place as the phase timeline.
- Commands: `apply_patch` to update `session-analysis/README.md`
- Result: `session-analysis/README.md` now calls out Phase 0 as “~6h wall, ~47m active” and notes active-time vs wall-time interpretation.
- Decision: Keep.
