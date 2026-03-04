# REVIEW: Comparison against Knuth’s “Claude’s Cycles” (claude-cycles.pdf)

This document reviews the current state of this repository (`claudescycles`) against the reference note
**“Claude’s Cycles”** by **Donald E. Knuth** (dated 28 Feb 2026; revised 02 Mar 2026), stored locally as
`claude-cycles.pdf` (5 pages). For grep/LLM-friendly access we also store `pdftotext` extractions in:

- `references/claude-cycles.txt` (`pdftotext -layout`)
- `references/claude-cycles.md` (`pdftotext -layout`, page-by-page)
- `references/claude-cycles.raw.txt` (`pdftotext -raw`)

Scope: compare **process**, **technical approach**, and **conclusions**; identify what we have replicated,
what we have not yet replicated, and where our writeups may still need tightening.

## Executive Summary

- **We replicated the odd-`m` construction exactly.** Our generator `claudescycles/claude.py` implements
  the same per-vertex permutation rule (the `"012"/"210"/"120"/"201"/"102"` choice based on `s=i+j+k (mod m)`
  and boundary conditions on `i,j`) shown in Knuth’s C-form simplification (Knuth 2026, p.1). See
  `claudescycles/claude.py:8`.
- **We built an independent, deterministic verifier first.** `claudescycles/verify.py` checks (i) each of the
  three cycles is Hamiltonian of length `m^3`, (ii) the cycles are arc-disjoint, and (iii) their union covers
  all arcs of `G_m`. This matches the problem statement’s validity criteria and is stronger “repro scaffolding”
  than the narrative verification in the note. See `claudescycles/verify.py:61`.
- **Empirical validation matches the note’s reported odd-`m` range.** The note reports Filip Stappers tested
  odd `m` from 3 through 101 (Knuth 2026, p.1). We archived machine-readable scan output verifying exactly that range:
  `artifacts/claude_scan_odd_3_101.json` (all `OK`).
- **We also confirm the construction fails on even `m`.** Our verifier reports non-Hamiltonicity (early repeats)
  for the same Claude/Knuth rule on every even `m` scanned in `[4,100]`:
  `artifacts/claude_scan_even_4_100.json`. This is consistent with the note, which states the *general* even-`m`
  decomposition problem remains open (Knuth 2026, p.5); it does **not** claim this odd-`m` rule should work for even `m`.
- **We translated the proof sketch into a theorem/lemmas writeup, but cycle 0 can still be polished.**
  `proofs/claude_odd_m.md` follows Knuth’s structure: arc-partition is automatic from “per-vertex permutation”,
  and Hamiltonicity is proved cycle-by-cycle using the invariant that `s` increases by 1 each step (Knuth 2026, pp.3–5).
  For cycles 1 and 2 we made the Appendix orbit descriptions more explicit via an `m`-step map on the `s=0` layer
  (compare Knuth 2026, Appendix on p.5). The cycle-0 argument is faithful but still somewhat narrative; further tightening is possible.
- **We have not yet replicated Knuth’s counting results.** The note gives exact counts for `m=3` Hamiltonian
  cycles (e.g., `11502`) and exact-cover counts for decompositions (e.g., `4554`, with a `760` “generalizable”
  subclass) (Knuth 2026, p.4). Those are still on our punchlist (P2).
- **We also have not yet reproduced the note’s small even-`m` existence claims.** Knuth reports that Filip
  Stappers found decompositions empirically for `4 <= m <= 16` (which includes even `m`) (Knuth 2026, p.1), and
  the note reports Claude claimed solutions for `m=4,6,8` without a general pattern (Knuth 2026, p.5). Our current
  repo only establishes that the *odd-`m` Claude/Knuth rule* fails for even `m`, and that a limited-budget CSP run did not find `m=4`.

## What Knuth’s note does (technical content recap)

Knuth’s note:

1. **Defines the graph `G_m`** on `m^3` vertices `ijk` with three outgoing arcs from each vertex: bump `i`, bump
   `j`, or bump `k` (all modulo `m`) (Knuth 2026, p.1).
2. **Reformulates decomposition as a per-vertex permutation assignment.** At each vertex one assigns a
   permutation of directions `{0,1,2}`; following direction `c` at every vertex yields a functional digraph that
   must be a *single* directed Hamiltonian cycle for each `c` (Knuth 2026, p.1).
3. **Narrates Claude Opus 4.6’s search process** (guided by Filip Stappers): attempts at symmetric/linear rules,
   DFS/brute-force, “serpentine/Gray-code” ideas, simulated annealing (SA), a near-miss with a single-hyperplane
   patch idea, and finally a successful “piecewise” rule derived from patterns in an SA-found solution (Knuth 2026, pp.1–2).
4. **Presents the odd-`m` construction** in a compact program form (C-like), then gives bump-rule descriptions for
   each cycle and proves Hamiltonicity for cycle 0 in the main text (Knuth 2026, pp.1,3).
5. **Provides Appendix sketches for cycles 1 and 2**, describing the order in which `s=0` vertices are visited (Knuth 2026, p.5).
6. **Adds a counting digression**: defines “generalizable” `m=3` Hamiltonian cycles and uses exact cover to count
   `m=3` decompositions and the generalizable subset; concludes there are hundreds of odd-`m` solutions (Knuth 2026, p.4).
7. **States even `m` remains open**, despite empirical evidence of solutions for small even `m` (Stappers reports
   decompositions for `4 <= m <= 16`), and notes that Claude claimed isolated even solutions (`m=4,6,8`) without
   a general construction (Knuth 2026, pp.1,5).

## What this repository does (and how it aligns)

### Process comparison (how we got here vs. the note’s workflow)

Knuth’s narrative is explicitly about *an AI-led exploratory search* with strict “write progress after every run”
instructions (Stappers’ `plan.md` discipline), plus a later human-authored proof.

Our repo is a *reproducible engineering/scientific workflow* that intentionally front-loads determinism:

- We first implemented a **verifier** that encodes the success criteria precisely (`claudescycles/verify.py:61`).
- We then implemented **search tooling** for small `m` (`claudescycles/csp.py`, `claudescycles/search.py`) to
  rediscover candidates from scratch (we found a valid `m=3` instance; entrypoint `claudescycles/search.py:21`).
- Only after that did we implement Knuth’s **explicit odd-`m` construction** as a generator and validate it over
  ranges (`claudescycles/claude.py:8`, `claudescycles/generate.py:1`, `claudescycles/scan.py:29`).
- We captured reproducible evidence as **machine-readable artifacts** under `artifacts/`.
- We maintained durable “project memory” (`WORKLOG.md`, `docs/IMPLEMENTATION.md`, `state/CONTEXT.md`), which is
  philosophically aligned with Stappers’ “document every run” requirement, but implemented in a restart-safe,
  version-controlled way.

### Construction comparison (does our code match Knuth’s program?)

Yes. The core choice in Knuth’s simplified C program is a per-vertex direction permutation `d`, selected by
`s=(i+j+k) mod m` and a small number of boundary conditions (`j=m-1`, `i>0`, `i=m-1`).

Our `claudescycles/claude.py` implements the same case split and returns the same permutations:

- `s == 0`: `"012"` if `j == m-1` else `"210"`
- `s == m-1`: `"120"` if `i > 0` else `"210"`
- otherwise: `"201"` if `i == m-1` else `"102"`

We then treat `d[c]` as the direction for cycle `c` and “bump” that coordinate, exactly as in the note (Knuth 2026, p.1).

### Verification comparison (what is checked and how)

Knuth’s note:

- reports empirical testing by Stappers for odd `m` in `[3,101]`;
- provides a proof for cycle 0 and sketches for cycles 1 and 2;
- does not provide a standalone “verifier spec” as code.

Our verifier (`claudescycles/verify.py`) makes the success conditions explicit and checkable:

- **Arc partition:** at every vertex, the three cycle directions must be a permutation of `{0,1,2}`. In this
  graph, that condition is equivalent to “arc-disjoint” + “union covers all arcs”, because outgoing arcs are
  uniquely identified by (tail vertex, bumped coordinate).
- **Hamiltonicity:** for each cycle, following successors from vertex `000` for `m^3` steps must visit `m^3`
  distinct vertices and return to `000`.

This is consistent with the formal “sigma assignment” reformulation in the note (Knuth 2026, p.1).

### Proof comparison (what we proved vs. what the note sketches)

Knuth’s main proof for cycle 0 relies on (Knuth 2026, p.3):

- the invariant that `s` increases by 1 each step, so equal-`s` vertices are spaced `m` steps apart; and
- a block argument showing that, for odd `m`, certain “step by 2” behavior forces coverage of all `m^2` vertices
  in each `s`-layer (and therefore all `m^3` vertices).

Our proof document (`proofs/claude_odd_m.md`) follows the same invariants (compare Knuth 2026, pp.3–5):

- **Lemma 1:** arc partition is automatic from per-vertex permutations (matches the note’s framing).
- **Lemma 2:** `s` increases by 1 each step (matches the note’s “layers spaced by `m` steps”).
- **Cycle 0:** we present a “fixed `i` block” argument paralleling Knuth’s narrative; this part is faithful but
  still written in a somewhat explanatory style rather than in a fully algebraic “state transition” style.
- **Cycles 1 and 2:** where Knuth’s Appendix describes the order of `s=0` vertices, we instead define an explicit
  `m`-step map `Φ` on the `s=0` layer and show it has a single orbit of size `m^2` when `m` is odd. This is the
  same content, but packaged in a way that is often easier to formalize and to test against code.

**Bottom line:** our proof is a faithful paraphrase/structuring of Knuth’s arguments; it is not an independent
new proof technique, and it can still be tightened (especially cycle 0).

## Conclusions comparison (what is “settled” and what remains open)

### Odd `m`

Knuth’s note concludes (with Stappers’ testing and the provided proofs) that the Claude-derived construction
gives valid decompositions for **odd** `m > 2` (Knuth 2026, pp.1,3–5).

We match that conclusion and provide reproducible evidence:

- `artifacts/claude_scan_odd_3_101.json`: verifier says `OK` for all odd `m` in `[3,101]`.
- `proofs/claude_odd_m.md`: theorem + lemmas establishing validity for all odd `m > 2` (subject to polishing
  noted above).

### Even `m`

Knuth’s note explicitly states the **general even-`m` problem remains open**, while also reporting that Claude
claimed isolated even solutions (`m=4,6,8`) without a general construction, and that Stappers empirically found
solutions for `4 <= m <= 16` (Knuth 2026, pp.1,5).

Our work does **not** resolve even `m`. What we have established is narrower:

- The specific Claude/Knuth **odd-`m` construction fails for even `m`** in `[4,100]` under our verifier
  (`artifacts/claude_scan_even_4_100.json`).
- Our CSP/backtracking search did not find a solution for `m=4` within a limited node budget (recorded in
  `WORKLOG.md`), but that is not a completeness result; in particular, it does not contradict Knuth’s report
  that solutions exist for `m=4` (it only shows our current search is not yet strong enough to reliably recover
  them).

### Counting results (m = 3)

Knuth’s note includes exact counts for:

- the number of Hamiltonian cycles when `m=3` (and a “generalizable” subclass), and
- the number of `3×3×3` decompositions (exact cover), and the number of decompositions comprised only of
  generalizable cycles.

We have **not yet** reproduced these counts. That is the largest “technical gap” relative to the note.

## References

- Knuth, Donald E. **“Claude’s Cycles.”** 28 Feb 2026; revised 02 Mar 2026. In this repo as `claude-cycles.pdf`.
  Key locations: p.1 (problem statement; sigma reformulation; C-form construction; odd-`m` testing range), p.3 (cycle-0 proof),
  p.4 (generalizability + counts + exact-cover theorem), p.5 (even-`m` status; Appendix for cycles 1 and 2).

## Recommendations / Next Steps

1. **Reproduce the `m=3` counting/exact-cover section** (P2): implement enumeration of all `m=3` Hamiltonian
   cycles, define “generalizable” exactly as in the note, and reproduce the exact cover counts. Archive results
   as `artifacts/*.json` with command provenance.
2. **Even-`m` exploration (P3):** attempt to reproduce the claimed `m=4,6,8` solutions with a solver that can
   provide certificates (e.g., exact cover/SAT/ILP), and catalog failures and invariants.
3. **Proof polish:** refactor cycle-0’s argument to remove narrative gaps and make the orbit structure explicit
   (similar to what we did for cycles 1 and 2).

## Conclusion

Relative to Knuth’s “Claude’s Cycles”, this repository currently achieves a strong replication of the **odd-`m`**
construction and its validation:

- The implemented rule matches the note’s program.
- The verifier encodes the exact success criteria.
- The archived scan reproduces the note’s stated odd-`m` empirical range.
- The proof writeup tracks the note’s proof strategy and makes two of the three cycle proofs more explicit.

The two major remaining gaps are (i) reproduction of Knuth’s **`m=3` counting / exact-cover** results and (ii)
substantive progress on the **even-`m`** case, which the note (and our own experiments) leave open.
