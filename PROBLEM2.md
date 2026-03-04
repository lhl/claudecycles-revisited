# PROBLEM2 (Extension Brief)

This file is *not* part of blind replication mode. Use `PROBLEM.md` alone when you want to rediscover the construction from scratch.

## Status (as of 2026-03-04)

- There is an explicit construction that decomposes the arcs of `G_m` into three arc-disjoint Hamiltonian cycles for **odd** `m > 2`.
- The even-`m` general case remains open in the source note; the odd-`m` construction fails on even `m` under our verifier.

## Where the construction lives

- Generator: `claudescycles/claude.py`
- Range-scan evidence:
  - `artifacts/claude_scan_odd_3_101.json` (all odd `m` in `[3,101]` verify `OK`)
  - `artifacts/claude_scan_even_4_100.json` (even `m` in `[4,100]` verify `FAIL`)
- Proof writeup: `proofs/claude_odd_m.md`

## Extension targets

- Even-`m` exploration: characterize which even `m` admit solutions; look for families and invariants.
- Counting claims for `m=3`: reproduce Hamiltonian cycle counts and “generalizable” subset counts.

