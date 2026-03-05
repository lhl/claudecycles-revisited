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
- CP-SAT even-`m` solver exists: `python -m claudescycles.even_cpsat --m <m> --out-dir <dir>` (uses OR-Tools `AddCircuit`).
- `COMPARISON.md` summarizes the baseline plus four cleanroom branches (`5.2`, `5.3-Codex`, `5.4`, `Opus 4.6`); session metrics were re-audited against session logs and the Opus literature-proof section is explicitly treated as unverified.

## Latest Validated Evidence
- Verifier rejects an intentionally invalid decomposition for `m=3` (`artifacts/invalid_all0_m3.json`).
- CSP search finds a valid decomposition for `m=3` (`artifacts/csp_m3.json`), verified `OK` (`artifacts/verify_csp_m3.json`).
- PDF extraction reveals a piecewise rule that reportedly works for odd `m` (tested through `m=101`) and provides a proof outline.
- Implemented the PDF rule and validated it with our verifier for all odd `m` in `[3,101]` (`artifacts/claude_scan_odd_3_101.json`); it fails for even `m` in `[4,100]` (`artifacts/claude_scan_even_4_100.json`).
- Enumerated all directed Hamiltonian cycles for `m=3`: count `11502` (matches Knuth 2026, p.4).
- Reproduced “generalizable” counts for `m=3` Hamiltonian cycles: `1012` lift to `m=5`; `996` lift to both `m=5` and `m=7` (matches Knuth 2026, p.4).
- Reproduced `m=3` exact-cover decomposition counts: total `4554` decompositions; `760` decompositions using only the `996` “generalizable” cycles (matches Knuth 2026, p.4).
- Archived feature-parity outputs in `artifacts/knuth_m3/` via `python -m claudescycles.knuth_m3 --out-dir artifacts/knuth_m3`.
- Found a verified even-`m` decomposition for `m=4` via CP-SAT (`artifacts/even_m4/cpsat_seed0_t60_w8/solution.json`), verifier `OK` (`artifacts/even_m4/cpsat_seed0_t60_w8/verify.json`), with solver stats + quick structure probe (`solver_stats.json`, `analysis.json`).
- Found verified even-`m` decompositions for `m=6` and `m=8` via CP-SAT, with solution + verifier + stats under `artifacts/even_m6/cpsat_seed0_t120_w8/` and `artifacts/even_m8/cpsat_seed0_t300_w8/`.
- Symmetry counts archived: `artifacts/knuth_m3/symmetry_counts.json` (cycle-level: `136` of `996` generalizable cycles remain generalizable under `ijk→jki`; decomposition-level: `92` of `760` all-generalizable decompositions map to another such decomposition under `ijk→jki`; `0` common to both rotations in either interpretation).
- Audited `cleanroom-5.4` from its checked-in session analysis and branch artifacts: GPT-5.4 (`xhigh`) independently converged on the same `(u,v,w)` odd-`m` skew-product construction as cleanroom-5.2/5.3, with session `019cbf6f` (`24m 43s` wall/active, `81` tool calls, `4.60M` total tokens), solver witnesses through `m=14`, odd-family validation through `m=31`, a `152`-line README, and a `254`-line partial theorem.

## Open Questions
- Tighten the cycle-0 Hamiltonicity argument: can we make the “block” proof fully self-contained and machine-checkable?
- Even `m`: solutions exist for `m=4`; find/verify `m=6` and `m=8`, and extract structural invariants/patterns (or characterize obstructions).
- `m=3` counting claims from the PDF: cross-check the replicated counts with an independent implementation path (and optionally verify symmetry subclaims like the `136` count under `ijk → jki`).

## Next Actions
1. E1 analysis: compare `m=4/6/8` CP-SAT solutions to extract invariants / propose candidate even-`m` family; add a failure/attempt catalog as we iterate.
2. Paper parity: decide how to phrase/resolve the symmetry-count ambiguity (cycle-level vs decomposition-level) in our repo docs.
