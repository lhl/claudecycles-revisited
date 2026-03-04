# PROBLEM-2 FOLLOWUP: Feature-parity tracker vs Knuth’s “Claude’s Cycles”

This file tracks what we have replicated from Knuth’s **“Claude’s Cycles”** note (2026-02-28; rev 2026-03-02)
and what remains.

Canonical source: `claude-cycles.pdf` (see also `references/claude-cycles.md` and `references/claude-cycles.txt`).

## Executive Summary (current status)

- Odd-`m` construction from the note is implemented (`claudescycles/claude.py`) and validated for odd `m` in `[3,101]`.
- The construction fails on even `m` (as expected; even case remains open in the note).
- Proof writeup exists for the odd-`m` construction: `proofs/claude_odd_m.md`.
- Paper-count “feature parity” for `m=3` is now implemented and reproduced with artifacts under `artifacts/knuth_m3/`.
- Review/crosswalk exists: `README.md` (paper pages + code line references).

## Repro Commands (one-liners)

- Verify a decomposition JSON: `python -m claudescycles.verify --input artifacts/claude_m5.json`
- Scan the Knuth/Claude construction:
  - odd: `python -m claudescycles.scan --family claude --m-min 3 --m-max 101 --step 2 --out artifacts/claude_scan_odd_3_101.json`
  - even: `python -m claudescycles.scan --family claude --m-min 4 --m-max 100 --step 2 --out artifacts/claude_scan_even_4_100.json`
- Reproduce Knuth’s `m=3` counting + exact-cover results:
  - `python -m claudescycles.knuth_m3 --out-dir artifacts/knuth_m3`

## Paper parity checklist

### Construction + odd-`m` validity

- [x] Implement Knuth’s case-split rule (the `"012"/"210"/"120"/"201"/"102"` table): `claudescycles/claude.py`
- [x] Deterministic verifier: `claudescycles/verify.py`
- [x] Empirical scan matches the note’s reported odd-`m` test range `[3,101]`: `artifacts/claude_scan_odd_3_101.json`
- [x] Empirical even-`m` failure scan recorded: `artifacts/claude_scan_even_4_100.json`

### Proof results (writeups)

- [x] Odd-`m` decomposition theorem (cycles 0–2): `proofs/claude_odd_m.md`
- [x] “Claude-like iff generalizable” theorem note: `proofs/claude_like_generalizable.md`

### Counting / exact cover (m = 3) — Knuth 2026, p.4

Reproduced via `claudescycles/m3_cycles.py`, `claudescycles/generalize.py`, `claudescycles/m3_decompositions.py`,
and the CLI `claudescycles/knuth_m3.py`.

- [x] # Hamiltonian cycles in `G_3`: `11502`
- [x] # that lift to `m=5`: `1012`
- [x] # that lift to both `m=5` and `m=7`: `996`
- [x] # decompositions of `3×3×3` arcs into 3 Hamiltonian cycles: `4554`
- [x] # decompositions using only the `996` “generalizable” cycles: `760`

Artifacts:

- `artifacts/knuth_m3/counts.json`
- `artifacts/knuth_m3/generalizable_cycle_masks.json`
- `artifacts/knuth_m3/decompositions.json`

## What remains open / not yet replicated

- Independent cross-check path for the `m=3` counts (currently a single implementation pipeline).
- Even-`m` general case: the note reports existence for small even `m` but no general construction; we have not yet
  reproduced explicit even-`m` solutions with certificates.
- Optional parity items from the note’s discussion (symmetry behaviors, “nicest” decompositions, etc.).

## Where to look next

- Punchlist: `docs/IMPLEMENTATION.md`
- Chronological work/evidence: `WORKLOG.md`
- Restart capsule: `state/CONTEXT.md`
