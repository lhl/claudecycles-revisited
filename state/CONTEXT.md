# CONTEXT CAPSULE

## Objective
Replicate and extend `claude-cycles.pdf` results with reproducible scripts.

## Current Best Known
- AGENTS/process scaffolding created.
- Starter punchlist and worklog initialized.
- Problem split created:
  - `PROBLEM.md` for replication-only mode
  - `PROBLEM-3-extension.md` for extension mode after baseline replication (formerly `PROBLEM2.md`)
- Original autonomous one-shot prompt captured in `PROBLEM-1-prompt.md` (also embedded verbatim in `README.md`).
- Deterministic verifier implemented: `python -m claudescycles.verify --input <json>`
- `claude-cycles.pdf` (repo root) contains an explicit construction for odd `m` plus proof sketches; `pdftotext` extracts live in `references/`.
- Proof writeup exists: `proofs/claude_odd_m.md`.
- Additional theorem note exists: `proofs/claude_like_generalizable.md` (generalizable cycles + Claude-like theorem).
- Review writeup exists: `README.md` (comparison vs Knuth note; formerly `REVIEW.md`).
- Followup tracker exists: `PROBLEM-2-followup.md` (formerly `FOLLOWUP.md`).

## Latest Validated Evidence
- Verifier rejects an intentionally invalid decomposition for `m=3` (`artifacts/invalid_all0_m3.json`).
- CSP search finds a valid decomposition for `m=3` (`artifacts/csp_m3.json`), verified `OK` (`artifacts/verify_csp_m3.json`).
- PDF extraction reveals a piecewise rule that reportedly works for odd `m` (tested through `m=101`) and provides a proof outline.
- Implemented the PDF rule and validated it with our verifier for all odd `m` in `[3,101]` (`artifacts/claude_scan_odd_3_101.json`); it fails for even `m` in `[4,100]` (`artifacts/claude_scan_even_4_100.json`).
- Enumerated all directed Hamiltonian cycles for `m=3`: count `11502` (matches Knuth 2026, p.4).
- Reproduced “generalizable” counts for `m=3` Hamiltonian cycles: `1012` lift to `m=5`; `996` lift to both `m=5` and `m=7` (matches Knuth 2026, p.4).
- Reproduced `m=3` exact-cover decomposition counts: total `4554` decompositions; `760` decompositions using only the `996` “generalizable” cycles (matches Knuth 2026, p.4).
- Archived feature-parity outputs in `artifacts/knuth_m3/` via `python -m claudescycles.knuth_m3 --out-dir artifacts/knuth_m3`.

## Open Questions
- Tighten the cycle-0 Hamiltonicity argument: can we make the “block” proof fully self-contained and machine-checkable?
- Even `m`: do decompositions exist for any even `m`? If yes, characterize the smallest solvable even `m` and search for families/invariants.
- `m=3` counting claims from the PDF: cross-check the replicated counts with an independent implementation path (and optionally verify symmetry subclaims like the `136` count under `ijk → jki`).

## Next Actions
1. P2-03: Implement an independent cross-check for the `m=3` counts (and optionally verify symmetry subclaims).
2. P3: Extend search/solver for even `m` (start with `m=4,6,8`) and record a failure catalog with reasons.
3. Proof polish: refactor `proofs/claude_odd_m.md` (especially cycle 0 and cycle 2) to eliminate any remaining narrative gaps.
