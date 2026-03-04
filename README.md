# REVIEW: Comparison against Knuth's "Claude's Cycles" (claude-cycles.pdf)

This document reviews the current state of this repository (`claudescycles`) against the reference note
**"Claude's Cycles"** by **Donald E. Knuth** (dated 28 Feb 2026; revised 02 Mar 2026), stored locally as
`claude-cycles.pdf` (5 pages). For grep/LLM-friendly access we also store `pdftotext` extractions in:

- `references/claude-cycles.txt` (`pdftotext -layout`)
- `references/claude-cycles.md` (`pdftotext -layout`, page-by-page, with known extraction errors corrected)
- `references/claude-cycles.raw.txt` (`pdftotext -raw`)

**Note on reference extractions:** `pdftotext` garbles some mathematical notation (subscripts and superscripts
are flattened, minus signs occasionally rendered as plus signs, special characters like π rendered as `?`, and
the s̄-mapping overline notation is lost). The `references/claude-cycles.md` file has inline corrections for
the most impactful errors; see its errata header for details.

Scope: compare **process**, **technical approach**, and **conclusions**; identify what we have replicated,
what we have not yet replicated, and where our writeups may still need tightening.

## Executive Summary

- **We replicated the odd-`m` construction exactly.** Our generator `claudescycles/claude.py` implements
  the same per-vertex permutation rule shown in Knuth's C-form simplification (Knuth 2026, p.2). At each
  vertex `(i,j,k)`, the construction assigns a permutation of `{0,1,2}` based on `s = (i+j+k) mod m` and
  boundary conditions on `i` and `j`; cycle `c` then bumps coordinate `d_c` at that vertex. We verified
  that our implementation produces the same `m=3` cycle-0 trace as Knuth's example on p.3 (the same cycle,
  starting at a different vertex — Knuth starts at `022` per his convention of beginning where `i` has just
  changed to `0`, rather than at `000`). See `claudescycles/claude.py:8`.
- **We built an independent, deterministic verifier first.** `claudescycles/verify.py` checks (i) each of the
  three cycles is Hamiltonian of length `m^3`, (ii) the cycles are arc-disjoint, and (iii) their union covers
  all arcs of `G_m`. This matches the problem statement's validity criteria and is stronger "repro scaffolding"
  than the narrative verification in the note. See `claudescycles/verify.py:61`.
- **Empirical validation matches the note's reported odd-`m` range.** The note reports Filip Stappers tested
  odd `m` from 3 through 101 (Knuth 2026, p.2). We archived machine-readable scan output verifying exactly
  that range: `artifacts/claude_scan_odd_3_101.json` (all `OK`).
- **We also confirm the construction fails on even `m`.** Our verifier reports non-Hamiltonicity (early repeats)
  for the same Claude/Knuth rule on every even `m` scanned in `[4,100]`:
  `artifacts/claude_scan_even_4_100.json`. This is consistent with the note, which states the *general* even-`m`
  decomposition problem remains open for `m ≥ 4` (Knuth 2026, p.5); it does **not** claim this odd-`m` rule
  should work for even `m`. The case `m=2` was proven impossible by Aubert and Schneider (1982)
  (Knuth 2026, p.5, ref [1]).
- **We translated the proof sketch into a theorem/lemmas writeup.**
  `proofs/claude_odd_m.md` follows Knuth's structure: arc-partition is automatic from "per-vertex permutation",
  and Hamiltonicity is proved cycle-by-cycle using the invariant that `s` increases by 1 each step
  (Knuth 2026, pp.3,5). For cycles 1 and 2 we made the Appendix orbit descriptions more explicit via an
  `m`-step map on the `s=0` layer (compare Knuth 2026, p.5). The cycle 1 proof uses a clean parametric
  bijection `v(r,t) = (-2t, r+t, t-r)` to establish a single orbit of size `m²`; the cycle 2 proof is
  correct but uses a more descriptive orbit argument and could benefit from a similarly explicit bijection.
  The cycle 0 argument is faithful but still somewhat narrative; further tightening is possible for both
  cycle 0 and cycle 2.
- **We reproduced Knuth's `m=3` counting + exact-cover results (except the optional symmetry subcount).**
  We reproduce the core paper counts `11502`, `1012`, `996`, `4554`, and `760` (Knuth 2026, p.4) with a
  single deterministic command:
  `python -m claudescycles.knuth_m3 --out-dir artifacts/knuth_m3` (see `artifacts/knuth_m3/counts.json`).
  We have **not** yet independently verified the additional paper subclaim that `136` of those `760` remain
  generalizable under the coordinate mapping `ijk → jki` (nor the “none common to all three mappings” claim).
- **We also have not yet reproduced the note's small even-`m` existence claims.** Knuth reports that Filip
  Stappers found decompositions empirically for `4 ≤ m ≤ 16` (which includes even `m`) (Knuth 2026, p.1), and
  the note reports Claude claimed solutions for `m=4,6,8` without a general pattern (Knuth 2026, p.5). Our
  current repo only establishes that the *odd-`m` Claude/Knuth rule* fails for even `m`, and that a
  limited-budget CSP run did not find `m=4`.

## Methodology (clean-room reimplementation)

This repository began as an experiment in **clean-room reimplementation**: implement a verifier, search
tooling, broad validation, and a proof writeup for the `G_m` decomposition problem starting only from
`PROBLEM.md`, using **Codex + GPT-5.2 (`xhigh`)** and an improved execution harness in `AGENTS.md`.

The initial run (commit `3751296`) was an autonomous, one-shot implementation driven by a single
prompt and the logging/punchlist discipline in `AGENTS.md`. The intent was to start clean-room (only
`PROBLEM.md` + the prompt; the Knuth note was **not checked into this repo**). However, the clean-room
boundary had a significant leak:

> **Path restriction gap:** The interactive setup sessions that preceded the autonomous run created
> `state/CONTEXT.md` and `docs/IMPLEMENTATION.md`, both of which explicitly reference
> `claude-cycles.pdf` as the "primary source." Meanwhile, an out-of-repo copy of the PDF sat one
> directory up at `../claude-cycles.pdf`. The model therefore **knew** the paper existed and had enough
> context to go looking for it from the very first token of the autonomous run — only the repo working
> tree was "clean."

**Timeline from session analysis (UTC, 2026-03-04):**

| Time | Event |
|---|---|
| 19:00:51 | Autonomous phase starts — builds verifier, CSP solver |
| 19:27–19:30 | CSP finds valid `m=3` but fails on `m=5` (200K nodes explored) |
| 19:30:58 | Checks for z3, pysat, ortools, pulp — none installed |
| **19:31:14** | `find .. -maxdepth 2 -name "*claude*cycles*.pdf"` — searches parent directory |
| 19:31:24 | `pdftotext -layout ../claude-cycles.pdf` — reads the full paper |
| 19:33:40 | Already compiling `claude.py` (the Knuth construction) |

The truly independent clean-room window was therefore **~30 minutes** (19:00:51 to 19:31:14), not the
full ~6 hours of Phase 0 wall time. (Phase 0 active time was ~47 minutes per session analysis, consistent
with the ~45 minutes shown in the Codex UI.) The model’s decision to search was rational given its context: the setup
session’s memory files told it `claude-cycles.pdf` existed, the CSP solver had just exhausted its scaling
budget, and no SAT/ILP solvers were available. It searched the parent directory, found the PDF, and
pivoted to implementing the known construction within two minutes.

This is an interesting finding in itself: it demonstrates that **clean-room isolation requires strict
path sandboxing**, not just omitting files from the repo. The model’s ability to `find` files outside
the working tree made the clean-room boundary porous. A future clean-room experiment would need to
either (a) remove the reference paper from reachable paths entirely, or (b) use filesystem-level
sandboxing to prevent traversal above the repo root.

For reproducibility, the PDF and `pdftotext` extracts were later added to the repo (commit `fe26f6a`), at which
point we wrote the review (now `README.md`) and then closed the remaining paper-parity gaps tracked in
[PROBLEM-2-followup.md](PROBLEM-2-followup.md).

### Harness highlights

- Deterministic verification first: `claudescycles/verify.py`
- Durable memory + checkpoints: `WORKLOG.md`, `docs/IMPLEMENTATION.md`, `state/CONTEXT.md`
- Machine-readable evidence: `artifacts/`

### PROBLEM-1 prompt (verbatim)

Verbatim copy of `PROBLEM-1-prompt.md`:

```text
Goal:
1) Build code to search/verify decompositions of the directed graph in `PROBLEM.md`.
2) Produce a rigorous proof (or clearly scoped partial proof) of your discovered construction.

Requirements:
- Follow `AGENTS.md` strictly (worklog/memory/checkpoint discipline).
- Start by creating deterministic verification code that checks:
  - each of 3 cycles is Hamiltonian (length m^3),
  - cycles are arc-disjoint,
  - union covers all arcs.
- Then build search tooling for small m to discover candidate patterns.
- Generalize candidate patterns and validate over broad ranges.
- Attempt a formal proof in a `proofs/` document with theorem/lemmas.
- If full proof fails, provide the strongest partial theorem with explicit unresolved lemmas.
- Record exact commands/results in `WORKLOG.md` and punchlist progress in `docs/IMPLEMENTATION.md`.
- Save machine-readable outputs in `artifacts/`.

Success criteria:
- Reproducible code + reproducible evidence + proof document (full or clearly bounded partial).
```

## What Knuth's note does (technical content recap)

Knuth's note:

1. **Defines the graph `G_m`** on `m^3` vertices `ijk` with three outgoing arcs from each vertex: bump `i`, bump
   `j`, or bump `k` (all modulo `m`) (Knuth 2026, p.1).
2. **Reformulates decomposition as a per-vertex permutation assignment.** At each vertex one assigns a
   permutation `σ` of directions `{0,1,2}`; following direction `c` at every vertex yields a functional digraph
   that must be a *single* directed Hamiltonian cycle for each `c` (Knuth 2026, p.1).
3. **Narrates Claude Opus 4.6's search process** (guided by Filip Stappers across 31 explorations spanning
   approximately one hour; Knuth 2026, p.4): attempts at symmetric/linear rules, DFS/brute-force,
   "serpentine/Gray-code" ideas, fiber decomposition, simulated annealing (SA), a near-miss with a
   single-hyperplane patch idea, and finally a successful "piecewise" rule derived from patterns in an
   SA-found solution (Knuth 2026, pp.1–2).
4. **Presents the odd-`m` construction** in a compact program form (C-like), then gives bump-rule descriptions for
   each cycle and proves Hamiltonicity for cycle 0 in the main text (Knuth 2026, pp.2–3).
5. **Provides Appendix sketches for cycles 1 and 2**, describing the order in which `s=0` vertices are visited
   (Knuth 2026, p.5).
6. **Adds a counting digression**: defines "generalizable" `m=3` Hamiltonian cycles via a coordinate-collapsing
   map (the s̄-mapping, described in detail under "Counting results" below) and uses exact cover to count
   `m=3` decompositions and the generalizable subset; concludes there are exactly 760 valid Claude-like
   decompositions for all odd `m > 1` (Knuth 2026, p.4).
7. **States even `m ≥ 4` remains open**, despite empirical evidence of solutions for small even `m` (Stappers
   reports decompositions for `4 ≤ m ≤ 16`), and notes that Claude claimed isolated even solutions (`m=4,6,8`)
   without a general construction (Knuth 2026, pp.1,5). The case `m=2` was proven impossible by Aubert and
   Schneider (1982) (Knuth 2026, p.5, ref [1]).

## What this repository does (and how it aligns)

### Process comparison (how we got here vs. the note's workflow)

#### Discovery vs. replication

Knuth's narrative is explicitly about *an AI-led exploratory search*: Claude Opus 4.6, coached by Filip Stappers
with a "write progress after every run" discipline (via `plan.md`), explored 31 different approaches over
approximately one hour before arriving at a successful odd-`m` construction (Knuth 2026, p.4). The process was
open-ended and creative, with Claude self-directing through strategies (symmetric rules → DFS → serpentine →
fibers → SA → pattern extraction from SA solutions). A human-authored proof followed afterward.

Our repo is a *reproducible replication and extension workflow*, guided by a structured agent harness
(`AGENTS.md`) that intentionally front-loads deterministic verification and systematic punchlist execution:

1. We first implemented a **verifier** that encodes the success criteria precisely (`claudescycles/verify.py:61`).
2. We then implemented **search tooling** for small `m` (`claudescycles/csp.py`, `claudescycles/search.py`) to
   rediscover candidates from scratch — we independently found a valid `m=3` decomposition via CSP
   (`artifacts/csp_m3.json`; entrypoint `claudescycles/search.py:21`).
3. We attempted to **scale the CSP solver** to `m=4` and `m=5`, but both returned `NO_HIT` within their node
   budgets (~50k and ~200k nodes respectively). The agent concluded: "Stop relying on blind CSP scaling; look
   for a parametric construction and then validate it."
4. **At that point** (after exhausting the independent search budget), the agent consulted `claude-cycles.pdf` and
   extracted the explicit odd-`m` construction. (See `WORKLOG.md`, task "Recover construction + proof sketch from
   `claude-cycles.pdf`".)
5. We implemented Knuth's **explicit odd-`m` construction** as a generator and validated it over broad ranges
   (`claudescycles/claude.py:8`, `claudescycles/generate.py:1`, `claudescycles/scan.py:29`).
6. We captured reproducible evidence as **machine-readable artifacts** under `artifacts/`.
7. We maintained durable "project memory" (`WORKLOG.md`, `docs/IMPLEMENTATION.md`, `state/CONTEXT.md`), which is
   philosophically aligned with Stappers' "document every run" requirement, but implemented in a restart-safe,
   version-controlled way.

This means our process had two distinct phases: **independent discovery** (steps 1–3, ~30 minutes of
autonomous work where we rediscovered a valid `m=3` instance but could not scale) and **informed
replication** (steps 4–7, the remaining ~5.5 hours of Phase 0, where we implemented and validated the
known construction after consulting the reference). The transition was triggered by the CSP solver's
scaling failure and the absence of stronger solvers, at which point the model searched for — and found —
`claude-cycles.pdf` in the parent directory (see "Methodology" above for exact timestamps).

#### How the AGENTS.md harness shaped the work

The `AGENTS.md` file defines a structured execution protocol: prioritized punchlists, mandatory logging after
every experiment batch, context compression for restart recovery, benchmark-gated optimization, and claim-integrity
rules requiring evidence for every assertion. Several of these features directly address failure modes that
Stappers encountered during the original exploration:

| AGENTS.md feature | Observable outcome in this project | Contrast with Stappers' experience |
|---|---|---|
| **Verifier-first** (P0 in punchlist) | Built `verify.py` before any construction code; CSP solver and Claude generator both verified on output | Stappers validated Claude's results externally; no shared verifier artifact |
| **Restart recovery** (`state/CONTEXT.md`) | No context was lost between sessions; agent could resume from a one-screen capsule | "He had to do some restarts when Claude stopped on random errors; then some of the previous search results were lost" (Knuth 2026, p.4) |
| **Non-negotiable logging** (`WORKLOG.md`) | Every experiment has exact commands and outcomes; this review could be written directly from logs | "After every two or three test programs were run, he had to remind Claude again and again that it was supposed to document its progress carefully" (Knuth 2026, p.4) |
| **Claim integrity** rules | Every assertion in this review cites a specific artifact or code line | The note relies on narrative evidence and Stappers' external confirmation |
| **Machine-readable artifacts** (`artifacts/`) | `*.json` files with command provenance enable exact reproducibility | The note reports testing results narratively |
| **Prioritized punchlist** (`docs/IMPLEMENTATION.md`) | Work proceeds in priority order (P0 → P1 → P2 → ...) with explicit tracking | Claude self-directed through 31 explorations, with some backtracking and dead ends |

The harness directly solved two documented failure modes from the Stappers session: **context loss on restart**
(our `CONTEXT.md` capsule is designed to survive session interruptions) and **inconsistent documentation
discipline** (our `AGENTS.md` makes logging non-negotiable and specifies the exact format).

#### What the AGENTS.md harness did not do

The harness was designed for **rigorous replication**, not **open-ended discovery**. It did not lead to an
independent rediscovery of the odd-`m` construction beyond `m=3`. The CSP solver found a valid `m=3` instance
but could not scale — the search space grows as `6^(m^3)` and the constraint propagation was insufficient to
prune it for `m ≥ 4`. Critically, **the harness did not enforce path-level isolation**: the model could (and
did) traverse above the repo root to find `../claude-cycles.pdf` after only 30 minutes of independent work
(see "Methodology" above). The clean-room intent was undermined by the setup session's memory files referencing
the paper and the absence of filesystem sandboxing.

By contrast, Stappers' lightweight coaching approach (a natural-language problem statement plus a logging
requirement) gave Claude the freedom to explore creative strategies — fiber decompositions, simulated annealing,
pattern extraction — that ultimately led to the breakthrough at exploration 31. A discovery-oriented harness
might supplement the `AGENTS.md` verification infrastructure with prompts for creative reframing, hypothesis
generation, and structured exploration of the strategy space — and, if clean-room isolation is desired, enforce
strict filesystem boundaries to prevent the model from accessing reference materials prematurely.

### Construction comparison (does our code match Knuth's program?)

Yes. The core choice in Knuth's simplified C program (Knuth 2026, p.2) is a per-vertex direction permutation `d`,
selected by `s=(i+j+k) mod m` and a small number of boundary conditions (`j=m-1`, `i>0`, `i=m-1`).

Our `claudescycles/claude.py` implements the same case split and returns the same permutations:

- `s == 0`: `"012"` if `j == m-1` else `"210"`
- `s == m-1`: `"120"` if `i > 0` else `"210"`
- otherwise: `"201"` if `i == m-1` else `"102"`

Cycle `c` then uses the unique outgoing arc that "bumps" coordinate `d[c]`:

- `d[c] = 0` means `(i,j,k) → (i+1,j,k)`
- `d[c] = 1` means `(i,j,k) → (i,j+1,k)`
- `d[c] = 2` means `(i,j,k) → (i,j,k+1)`

This is exactly the mechanism described in the note (Knuth 2026, p.2).

### Verification comparison (what is checked and how)

Knuth's note:

- reports empirical testing by Stappers for odd `m` in `[3,101]` (Knuth 2026, p.2);
- provides a proof for cycle 0 and sketches for cycles 1 and 2 (Knuth 2026, pp.3,5);
- does not provide a standalone "verifier spec" as code.

Our verifier (`claudescycles/verify.py`) makes the success conditions explicit and checkable:

- **Arc partition:** at every vertex, the three cycle directions must be a permutation of `{0,1,2}`. In this
  graph, that condition is equivalent to "arc-disjoint" + "union covers all arcs", because outgoing arcs are
  uniquely identified by (tail vertex, bumped coordinate).
- **Hamiltonicity:** for each cycle, following successors from vertex `000` for `m^3` steps must visit `m^3`
  distinct vertices and return to `000`.

This is consistent with the formal sigma-assignment reformulation in the note (Knuth 2026, p.1).

### Proof comparison (what we proved vs. what the note sketches)

Knuth's main proof for cycle 0 relies on (Knuth 2026, p.3):

- the invariant that `s` increases by 1 each step, so equal-`s` vertices are spaced `m` steps apart; and
- a block argument showing that, for odd `m`, certain "step by 2" behavior forces coverage of all `m^2` vertices
  in each `s`-layer (and therefore all `m^3` vertices).

Our proof document (`proofs/claude_odd_m.md`) follows the same invariants (compare Knuth 2026, pp.3,5):

- **Lemma 1:** arc partition is automatic from per-vertex permutations (matches the note's framing).
- **Lemma 2:** `s` increases by 1 each step (matches the note's "layers spaced by `m` steps").
- **Cycle 0:** we present a "fixed `i` block" argument paralleling Knuth's narrative (Lemmas 3–6); this part is
  faithful but still written in a somewhat explanatory style rather than in a fully algebraic "state transition"
  style.
- **Cycle 1:** where Knuth's Appendix describes the order of `s=0` vertices, we define an explicit
  `m`-step map `Φ₁` on the `s=0` layer and introduce a parametric bijection `v(r,t) = (-2t, r+t, t-r)` to
  show that the map has a single orbit of size `m²` when `m` is odd. This is the same content as Knuth's
  Appendix, but packaged in a way that is easier to formalize and to test against code.
- **Cycle 2:** we define the `m`-step map `Φ₂` with explicit case analysis (four cases depending on `j` vs.
  `m-1` and `i` vs. `m-2`), but the orbit argument is more descriptive than cycle 1's — it asserts that
  "every `j` value is reached, and for each fixed `j` the orbit visits all `m` values of `i` exactly once"
  without providing an analogous parametric bijection. The argument is correct but at a different level of
  rigor than cycle 1.

**Bottom line:** our proof is a faithful paraphrase/structuring of Knuth's arguments; it is not an independent
new proof technique, and it can still be tightened (especially cycle 0 and the cycle 2 orbit structure).

## Conclusions comparison (what is "settled" and what remains open)

### Odd `m`

Knuth's note concludes (with Stappers' testing and the provided proofs) that the Claude-derived construction
gives valid decompositions for **odd** `m > 2` (Knuth 2026, pp.2–3,5).

We match that conclusion and provide reproducible evidence:

- `artifacts/claude_scan_odd_3_101.json`: verifier says `OK` for all odd `m` in `[3,101]`.
- `proofs/claude_odd_m.md`: theorem + lemmas establishing validity for all odd `m > 2` (subject to polishing
  noted above).

### Even `m`

Knuth's note explicitly states:

- `m=2` is **impossible** (proven by Aubert and Schneider, 1982; Knuth 2026, p.5, ref [1]).
- The general even-`m` problem for `m ≥ 4` **remains open**, while also reporting that Claude claimed isolated
  even solutions (`m=4,6,8`) without a general construction, and that Stappers empirically found decompositions
  for `4 ≤ m ≤ 16` (Knuth 2026, pp.1,5).

Our work does **not** resolve even `m`. What we have established is narrower:

- The specific Claude/Knuth **odd-`m` construction fails for even `m`** in `[4,100]` under our verifier
  (`artifacts/claude_scan_even_4_100.json`).
- Our CSP/backtracking search did not find a solution for `m=4` within a limited node budget (recorded in
  `WORKLOG.md`), but that is not a completeness result; in particular, it does not contradict Knuth's report
  that solutions exist for `m=4` (it only shows our current search is not yet strong enough to reliably recover
  them).

### Counting results (`m = 3`)

Knuth's note includes exact counts (Knuth 2026, p.4):

- **11502** total Hamiltonian cycles for `m=3`.
- **1012** of those generalize to Hamiltonian cycles for `m=5`.
- **996** generalize to Hamiltonian cycles for both `m=5` and `m=7`; these 996 are in fact generalizable to all
  odd `m > 1`.
- **4554** total decompositions of `G_3` into three arc-disjoint Hamiltonian cycles (via exact cover over the
  11502 cycles).
- **760** of those 4554 decompositions use only generalizable cycles and are therefore valid Claude-like
  decompositions for all odd `m > 1`.
- **136** of those 760 remain generalizable under the coordinate mapping `ijk → jki`, but **none** are common
  to all three cyclic mappings `{ijk, jki, kij}`.

The "generalizable" definition uses a coordinate-collapsing map (the "s̄-mapping"; Knuth 2026, p.4): given a
vertex `(I,J,K)` with `0 ≤ I,J,K < m`, compute `S = (I+J+K) mod m`, then collapse each coordinate to a
`{0,1,2}` value via `x̄ = 0` if `x=0`, `x̄ = 2` if `x=m-1`, `x̄ = 1` otherwise; and set
`k = (s̄ - ī - j̄) mod 3`. The successor of `(I,J,K)` is obtained by bumping the same coordinate that the
`m=3` cycle bumps at `(ī, j̄, k)`. A cycle is "generalizable" if this process yields a Hamiltonian cycle for
all odd `m ≥ 3`.

We have reproduced the core counts `11502`, `1012`, `996`, `4554`, and `760` and archived machine-readable
outputs under `artifacts/knuth_m3/` (see `artifacts/knuth_m3/counts.json`). Reproduction entrypoint:

`python -m claudescycles.knuth_m3 --out-dir artifacts/knuth_m3`

The lifting map is implemented in `claudescycles/generalize.py`, enumeration in `claudescycles/m3_cycles.py`,
and exact-cover counting in `claudescycles/m3_decompositions.py`. The remaining paper-specific symmetry
subclaim about `136` under `ijk → jki` is not yet independently checked.

## References

- Knuth, Donald E. **"Claude's Cycles."** 28 Feb 2026; revised 02 Mar 2026. In this repo as `claude-cycles.pdf`.
  Key locations:
  p.1 (problem statement; sigma reformulation; Stappers' empirical claims for `4 ≤ m ≤ 16`),
  p.2 (Claude's exploration narrative; C-form construction; odd-`m` testing range through 101),
  p.3 (cycle-0 proof; generalizability motivation),
  p.4 (generalizability definition; s̄-mapping; counts: 11502/1012/996 cycles, 4554/760 decompositions,
  136 under jki; exact-cover theorem; Stappers' process notes: 31 explorations, ~1 hour),
  p.5 (even-`m` status; `m=2` impossibility ref [1]; Claude's even claims; Appendix for cycles 1 and 2).
- Aubert, Jacques and Bernadette Schneider. "Graphes orientés indécomposables en circuits hamiltoniens."
  *Journal of Combinatorial Theory* B32 (1982), 347–349. (Cited in Knuth 2026, p.5, ref [1]: proves `m=2`
  is impossible.)

## Recommendations / Next Steps

1. **Independent cross-check of the `m=3` counts** (P2-03): implement a second, independent enumeration/counting
   path (and optionally verify the `136` symmetry subclaim under `ijk → jki`).
2. **Even-`m` exploration (P3):** attempt to reproduce the claimed `m=4,6,8` solutions with a solver that can
   provide certificates (e.g., exact cover/SAT/ILP), and catalog failures and invariants. Note that `m=2` is
   provably impossible (Aubert and Schneider, 1982) and should be excluded from search.
3. **Proof polish:** refactor cycle 0's argument to remove narrative gaps and make the orbit structure explicit
   (similar to what we did for cycle 1); add a parametric bijection to the cycle 2 orbit argument to bring it
   to the same level of rigor as cycle 1.

## Conclusion

Relative to Knuth's "Claude's Cycles", this repository currently achieves a strong replication of the **odd-`m`**
construction and its validation:

- The implemented rule matches the note's program.
- The verifier encodes the exact success criteria.
- The archived scan reproduces the note's stated odd-`m` empirical range.
- The proof writeup tracks the note's proof strategy and makes two of the three cycle proofs more explicit
  (with cycle 1 fully algebraic via a parametric bijection and cycle 2 needing a tighter orbit argument).

The major remaining gaps are (i) an **independent cross-check** of the `m=3` counting pipeline (and optionally
the paper's symmetry subclaims like the `136`-count under `ijk → jki`), and (ii) substantive progress on the
**even-`m`** case for `m ≥ 4`, which the note (and our own experiments) leave open.

On the **process and harness** side: our `AGENTS.md` framework successfully addressed documented failure modes
from the original Stappers/Claude session — context loss on restart and inconsistent documentation discipline —
and produced a rigorous, reproducible evidence trail. However, session analysis revealed a significant gap: the
clean-room boundary was porous. The setup session's memory files (`state/CONTEXT.md`, `docs/IMPLEMENTATION.md`)
referenced `claude-cycles.pdf`, and the model could traverse to `../claude-cycles.pdf` outside the repo. It did
so after only **~30 minutes** of independent work (at 19:31:14 UTC), triggered by CSP scaling failure and the
absence of SAT/ILP solvers. The independent search phase found `m=3` but the model rationally pivoted to the
known construction rather than continuing to explore. The PDF was later checked into the repo for
reproducibility (commit `fe26f6a`). A future clean-room experiment would require filesystem-level sandboxing,
and a future discovery-oriented iteration might combine the `AGENTS.md` verification infrastructure with
creative exploration strategies to support both rigorous validation and open-ended search.

## PROBLEM-2 followup (paper gap closure)

See [PROBLEM-2-followup.md](PROBLEM-2-followup.md) for the structured follow-up: we used this README-level
review to identify gaps versus Knuth's note (notably the `m=3` counting/exact-cover results), then implemented
those missing components and archived machine-readable outputs under `artifacts/knuth_m3/`. The followup file
also tracks what remains open (even `m`, independent cross-checks, and proof polishing).
