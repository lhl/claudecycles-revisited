# Comparison: Baseline vs. Cleanroom Runs

This document compares four runs of the Claude's Cycles replication/extension experiment across
different models, reasoning levels, and isolation conditions.

## Experiment Overview

**Problem**: Decompose all arcs of the directed graph `G_m` (vertices `Z_m^3`, three outgoing arcs
per vertex bumping each coordinate) into three arc-disjoint directed Hamiltonian cycles.

**Reference**: Knuth, "Claude's Cycles" (2026) — describes how Claude Opus 4.6, coached by Filip
Stappers, discovered a construction for odd `m` over 31 explorations (~1 hour).

| Run | Branch | Model | Reasoning | Isolation | Paper Access |
|-----|--------|-------|-----------|-----------|--------------|
| **Baseline** | [`main`](https://github.com/lhl/claudescycles-revisited/tree/main) | GPT-5.2 (Codex CLI) | xhigh | Porous (paper at `../`) | Yes, after ~30 min |
| **Cleanroom A** | [`cleanroom-5.2`](https://github.com/lhl/claudescycles-revisited/tree/cleanroom-5.2) | GPT-5.2 (Codex CLI) | xhigh | Strict cleanroom | None |
| **Cleanroom B** | [`cleanroom-5.3-codex`](https://github.com/lhl/claudescycles-revisited/tree/cleanroom-5.3-codex) | GPT-5.3-Codex (Codex CLI) | xhigh | Strict cleanroom | None |
| **Cleanroom C** | [`cleanroom-opus-4.6`](https://github.com/lhl/claudescycles-revisited/tree/cleanroom-opus-4.6) | Claude Opus 4.6 (Claude Code) | ultrathink | Strict cleanroom | None |

The **baseline** run had the Knuth paper one directory up and setup-session memory files that
referenced it by name. A prior setup session (GPT-5.3-Codex) had already read the PDF; in the main replication
session the model re-discovered and read the PDF after ~30 minutes of independent work when its
CSP solver failed to scale (see `README.md`, "Methodology" section). The three
**cleanroom** runs had no reference paper accessible and were given only `PROBLEM.md` (the bare
graph definition and goal) plus `AGENTS.md` (the execution harness).

**Tool availability note**: The cleanroom runs had OR-Tools (CP-SAT) pre-installed from the start,
while the baseline's initial autonomous phase had no constraint solvers available (z3, pysat,
ortools, and pulp were all absent). The baseline only gained OR-Tools in a later extension session.
This difference is significant: the baseline model's decision to search for the reference paper was
partly triggered by the absence of solvers capable of scaling beyond its homebrew CSP. The cleanroom
models, with CP-SAT available from the first tool call, could immediately find solutions for small
`m` and use those to drive pattern discovery — a more favorable starting position for independent
construction discovery.

---

## Session Metrics

| Metric | Baseline (5.2) | Cleanroom A (5.2) | Cleanroom B (5.3) | Cleanroom C (Opus 4.6) |
|--------|---------------:|-------------------:|-------------------:|-----------------------:|
| **Session ID** | `019cb512` | `019cb9d0` | `019cbc54` | `f2a37262` |
| **Wall time** | 18h 11m | 1h 27m | 12m 33s | 3h 55m |
| **Active time** | 2h 38m | 1h 08m | 12m 33s | 51m 45s |
| **User msgs** | 18 | 2 | 1 | 86 |
| **Tool calls** | 392 | 170 | 64 | 83 |
| **Total tokens** | 41.22M | 13.55M | 5.45M | 10.22M (API) |
| **Output tokens** | 318.8K | 152.1K | 42.5K | 165.0K |
| **Reasoning tokens** | 238.7K (75% of output) | 109.9K (72%) | 17.7K (42%) | — (not exposed) |
| **Cache hit rate** | 95.5% | 96.7% | 98.6% | 81.8% |

**Key observations**:
- GPT-5.3-Codex was substantially faster than GPT-5.2 on the cleanroom task (12m active vs 68m),
  with ~60% fewer tokens and ~62% fewer tool calls, while reaching the same odd-`m` construction/proof
  (but with a smaller even-`m` CP-SAT sweep and fewer archived artifacts).
- Claude Opus 4.6 had ~52m active time (vs ~68m for Cleanroom A) but much longer wall time (~4h) due
  to idle gaps, and it produced many more exploratory scripts before settling on a solver-heavy approach.
- Codex runs show high cached-input rates (95–99%). Claude Code’s cache rate (81.8%) is computed from
  its cache-read / (cache-read + cache-create + non-cached input) token accounting, and is not directly
  comparable to Codex’s cached-input metric.
- Baseline metrics above are for the main replication session (`019cb512`) only; the baseline branch also
  includes work from separate setup/extension sessions and post-hoc review.

---

## What Each Run Achieved

### Core Results Summary

| Capability | Baseline | Cleanroom A (5.2) | Cleanroom B (5.3) | Cleanroom C (Opus 4.6) |
|------------|:--------:|:------------------:|:------------------:|:----------------------:|
| **Deterministic verifier** | Yes | Yes | Yes | Yes |
| **CP-SAT solver** | Yes (even only) | Yes | Yes | Yes |
| **Odd-m construction** | Knuth's (from paper) | Independent | Independent | None (solver only) |
| **Odd-m proof** | Paraphrase of Knuth | Original (skew-product) | Original (skew-product) | Solver evidence; literature sketch (unverified) |
| **Odd-m validation range** | 3–101 | 5–101 | 5–101 | 3–30 (solver) |
| **Even-m CP-SAT solutions** | m=4,6,8 | m=4,6,8,10,12,14,16 | m=4,6,8,10,12 | m=4,6,8,10,...,30 |
| **Even-m parity obstruction** | Not identified | Proved | Not explicitly | Not identified |
| **m=3 counting/exact-cover** | 11502/1012/996 cycles; 4554/760 decompositions | Not attempted | Not attempted | Not attempted |
| **Symmetry analysis (m=3)** | 136/92/0 verified | Not attempted | Not attempted | Not attempted |
| **Failed constructions catalog** | Not applicable | 5 documented | 4 documented | 4 documented |
| **Structural analysis scripts** | Not applicable | — | — | 10 scripts |

### Detailed Breakdown

**Baseline (`main`)**: Replicated Knuth's odd-`m` construction after reading the paper at minute
30. Extended with CP-SAT even-`m` certificates (m=4,6,8), reproduced all `m=3` counting results
(11502/1012/996/4554/760), and verified the symmetry subclaim (136 of 996 cycles, 92 of 760
decompositions). Proof is a structured paraphrase of Knuth's arguments. The most complete in terms
of paper parity, but not an independent discovery.

**Cleanroom A (GPT-5.2)**: Independently discovered an odd-`m` construction for `m >= 5` based on
a coordinate transformation `(i,j,k) -> (u,v,w) = (i, i+j, i+j+k)` and a skew-product lift
argument. The construction uses a parameter `A` (selected via CRT/gcd constraints) controlling row
assignments. Proved correctness with two structural lemmas (base-cycle period + lift criterion).
Found even-`m` CP-SAT solutions up to `m=16` (widest among the Codex cleanroom runs). Identified and
proved a fundamental parity obstruction: constructions depending only on `(v,w)` cannot work for even
`m` because the three `Delta_c` values must all be odd (coprime to even `m`) but sum to `m^2` (even).

**Cleanroom B (GPT-5.3-Codex)**: Produced essentially the same construction and proof as Cleanroom
A — identical coordinate transformation, identical parameter selection, identical skew-product
lemmas — in a fraction of the active time and with far fewer tokens/tool calls. The implementation is
very similar to Cleanroom A's. This is remarkable convergence: two independent runs of related models
arrived at the same novel mathematical construction and proof framework.

**Cleanroom C (Claude Opus 4.6)**: Took a fundamentally different approach. Rather than discovering
a closed-form construction, Opus built a CP-SAT solver and pushed it to `m=30` (the widest
solver-based range), then spent most of its time on **exploratory structural analysis**: 10
separate scripts probing diagonal patterns, rotation symmetry, cyclic coordinate equivariance, 2D
reductions, and layer-lifting strategies. It attempted several explicit construction strategies and
found them infeasible within the attempted families. It also wrote a literature-based existence
argument, but several citations in its proof/README appear inaccurate (e.g., year/venue mismatches),
and the applicability to this *directed arc-decomposition* problem has not been independently
verified. Treat that portion as **literature leads**, not as a settled proof.

---

## Construction Comparison

### The Independent Discovery (Cleanroom A and B)

Both GPT-5.2 and GPT-5.3 independently discovered the **same novel construction**, which is
*different from Knuth's construction*:

**Knuth/Baseline construction** (from the paper):
- Assigns a permutation based on `s = (i+j+k) mod m` and boundary conditions on `i` and `j`
- Four cases: `s=0`, `s=m-1`, and two middle cases split by `i=m-1`
- Direction assignment uses the raw `(i,j,k)` coordinates
- Proof via `s`-layer invariant (equal-`s` vertices spaced `m` steps apart)

**Cleanroom construction** (independently discovered):
- Coordinate change: `(i,j,k) -> (u,v,w) = (i, i+j, i+j+k)` where every arc increments `w` by 1
- Direction depends only on `(v,w)`, not on `u`
- Three `w`-row cases (`w=0`, `w=1`, `w >= 2`) with a parameter `A` controlling a row subset
- Proof via **skew-product dynamics**: base cycle on `(v,w)` has period `m^2` (Lemma 1),
  lift to `(u,v,w)` has period `m^3` iff `gcd(m, Delta_c) = 1` (Lemma 2)
- Parameter `A` chosen via CRT so that `gcd(m, 2A+1) = gcd(m, 2A+3) = 1`

The cleanroom construction is arguably **more elegant** than Knuth's: the coordinate change reveals
the skew-product structure, the proof factors cleanly into a 2D base lemma and a 1D lift lemma,
and the parameter existence is constructive via CRT. However, Knuth's construction covers `m=3`
(the cleanroom construction cannot find a valid `A` for `m=3`), and Knuth's proof approach works
at a different level of abstraction (orbit arguments on `s`-layers).

Both constructions produce valid decompositions for all odd `m >= 5` but they are **not the same
decomposition** — they assign different permutations at most vertices.

### Opus 4.6's Exploration-Heavy Approach

Opus 4.6 tried four explicit construction strategies and found them infeasible within the attempted families:

| Approach | Idea | Why It Fails |
|----------|------|-------------|
| Single diagonal derangement | Identity off `s=m-1`, derangement on it | Cannot produce Hamiltonian cycles |
| Diagonal-class-only | `sigma` depends only on `s = (x+y+z) mod m` | Exhaustive 6^m search: infeasible for all `m >= 3` |
| Pure rotation | `d_c(v) = (c + delta(v)) mod 3` | Only uses 3 of 6 permutations in S_3 |
| Layer lifting | Build z-primary C_2, fix C_0/C_1 at normal vertices | Remaining 2-factor doesn't decompose |

These are **different construction attempts** than what GPT-5.2/5.3 tried. Opus explored the
diagonal/rotation/lifting design space more broadly but never discovered the `(u,v,w)` coordinate
transformation that unlocks the skew-product structure. Instead, it pivoted to a literature-based
existence argument. This is a valid research direction, but the specific citations/claim in the
cleanroom artifact are not yet verified for this problem.

Opus also produced unique **structural findings** not present in the other runs:
- For `m=3`, the direction function depends on exactly 2 linear invariants: `(x-z, y-z) mod 3`
- For `m >= 5`, no pair of linear invariants suffices (genuinely non-linear)
- Cyclically symmetric solutions exist for odd `m` (verified `m=3,5,7`)
- Valid decompositions must use all 6 elements of S_3 (not just cyclic shifts)

---

## Proof Strategy Comparison

| Aspect | Baseline | Cleanroom A & B | Cleanroom C |
|--------|----------|-----------------|-------------|
| **Proof type** | Paraphrase of Knuth | Original constructive | Computational + literature leads (unverified) |
| **Scope** | Odd `m > 2` | Odd `m >= 5` | `m=3..30` (solver evidence) |
| **Key technique** | `s`-layer orbit argument | Skew-product lift (2 lemmas) | CP-SAT + structural probes; literature leads (unverified) |
| **m=3 coverage** | Included in construction | Solver artifact (excluded from proof) | Solver artifacts |
| **Even-m coverage** | Acknowledged open | Proved obstruction for `(v,w)`-only families | Solver artifacts (`m <= 30`) |
| **Rigor level** | Narrative/explanatory | Algebraic with CRT existence proof | Computational + heuristic analysis |
| **Originality** | Replication | Novel | Exploratory (no construction) |

The cleanroom GPT runs produced the most **technically original** proof work: a novel construction
with an elegant factored proof via skew-product dynamics. Opus produced the **broadest computational
range** (solver evidence through `m=30`) plus exploratory structural analysis, but it did not produce
an explicit construction. The baseline produced the most **complete replication** of Knuth's specific
results including counting and symmetry analysis.

---

## Harness Effects

All four runs used the same `AGENTS.md` harness (verifier-first development, mandatory logging,
restart-safe memory, machine-readable evidence). Comparing outcomes:

### What the harness consistently produced

Every run, regardless of model, followed the same disciplined pipeline:
1. Build a deterministic verifier first (P0 priority)
2. Use search tooling (CSP/backtracking or CP-SAT) to find small-`m` solutions
3. Attempt pattern generalization
4. Document everything in WORKLOG.md with exact commands and results
5. Maintain restart-safe context capsule in `state/CONTEXT.md`
6. Archive machine-readable artifacts

This consistency across three different models demonstrates the harness is **model-agnostic** —
the structured execution protocol transfers across model families and reasoning modes.

### Where the harness helped most

- **Documentation discipline**: All cleanroom runs produced complete worklogs and implementation
  tracking, solving the "repeated reminding" problem Knuth documented from Stappers' session.
- **Reproducibility**: Every *computational* assertion is backed by an artifact with exact provenance.
- **Failed-attempt preservation**: All three cleanroom runs documented failed construction
  approaches, preventing wasted effort in future work.

### Where the harness didn't help

- **Discovery strategy**: The harness prescribes "build verifier → search → generalize → prove"
  but doesn't guide *how* to generalize. The GPT models independently found the `(u,v,w)` coordinate
  change; Opus tried different (ultimately unsuccessful) construction strategies. The harness
  couldn't compensate for this divergence in mathematical insight.
- **Construction discovery for Opus**: Despite more time and more exploration, Opus didn't find a
  closed-form construction. It compensated with a solver-heavy approach plus a literature-based
  existence argument (not yet independently verified) — arguably more "research-like" but one that
  doesn't produce a constructive algorithm.

### Cleanroom isolation

The strict cleanroom (no paper access) produced qualitatively different outcomes than the baseline:
- The baseline replicated Knuth's specific construction; the cleanroom runs invented their own
- The cleanroom construction (`(u,v,w)` skew-product) is genuinely novel relative to Knuth's
- The cleanroom runs could not reproduce the `m=3` counting/exact-cover work (that requires
  specific definitions from the paper, like the s-bar generalizability mapping)

---

## Efficiency Comparison

| Metric | Cleanroom A (5.2) | Cleanroom B (5.3) | Cleanroom C (Opus 4.6) |
|--------|------------------:|------------------:|:----------------------:|
| Active time | 1h 08m | 12m 33s | 51m 45s |
| Tokens per minute (active) | 200K | 435K | 198K |
| Tool calls per minute | 2.5 | 5.1 | 1.6 |
| Output tokens | 152.1K | 42.5K | 165.0K |
| Reasoning % of output | 72% | 42% | — |
| `scripts/*.py` files | 4 | 4 | 12 |
| Tracked `artifacts/*` files | 30 | 14 | 49 |
| Proof length | 284 lines | 151 lines | 180 lines |

**GPT-5.3-Codex** was the most efficient by every metric: fastest wall time, fewest tokens, highest
tool-call throughput, and most concise proof, while achieving the same construction and proof framework.
It also spent proportionally less on reasoning tokens (42% vs 72% of output) than the GPT-5.2 cleanroom run.

**Claude Opus 4.6** was the most exploratory: it produced the most scripts (12 vs 4), pushed the
solver to the widest `m` range (`m <= 30`), and generated the most output tokens (165K). Its
longer thinking blocks (24K + 32K tokens) reflect deeper upfront planning. Despite this investment,
it did not find a closed-form construction — suggesting the mathematical insight required for the
`(u,v,w)` transformation may not emerge from broader exploration alone.

**GPT-5.2** (Cleanroom A) produced a longer proof, more artifacts, and a wider even-`m` CP-SAT sweep than
Cleanroom B, but at a much higher token/tool-call cost.

---

## README Quality Comparison

All three cleanroom models wrote their own READMEs without post-hoc editing.

**Cleanroom A (GPT-5.2)** — 103 lines, 4.1KB:
- Well-structured with Problem/Implementation/Status/Quickstart/Future sections
- Clear three-way status split: Proven / Computational evidence / Open
- Practical: copy-paste CLI commands, seed sensitivity noted
- Professional tone, appropriate mathematical terminology

**Cleanroom B (GPT-5.3)** — 135 lines, 3.6KB:
- Similar structure to A (convergent even in documentation style)
- More detailed "What Is Implemented" breakdown (4 numbered sections)
- Artifact inventory with directory explanations
- Slightly more terse, uses `##` headers inconsistently (some sections lack hierarchy)

**Cleanroom C (Claude Opus 4.6)** — 161 lines, 8.0KB:
- Most comprehensive: includes structural findings, failed constructions table, performance data,
  open problems, 7 academic references
- Mathematical framing (Cayley digraph identification, S_3 saturation evidence)
- The only README that reads like a **research paper abstract** rather than a project README
- Includes a computational performance table with O(m^4) scaling analysis
- Includes 7 academic references (some citations appear inaccurate; treat as pointers to verify)

Opus's README is the most informative standalone document; the GPT READMEs are more practical
as project guides. All three are candid about the lack of a general even-`m` construction; Opus’s
literature-proof section needs independent verification.

---

## Key Findings

### 1. Independent convergence on a novel construction

GPT-5.2 and GPT-5.3 independently discovered the same `(u,v,w)` coordinate transformation and
skew-product proof structure. The construction code is nearly identical between the two runs.
This suggests the approach is a natural "attractor" in the solution space for models with strong
mathematical reasoning — the coordinate change that makes every arc increment `w` by 1 is a
canonical simplification that both models found via CP-SAT pattern analysis.

### 2. Different model families, different strategies

The GPT models (5.2/5.3) converged on **constructive proof via pattern discovery**: find solutions
with CP-SAT, analyze the direction tables, identify the `(v,w)` dependence, derive a parametric
family, and prove it. Claude Opus 4.6 pursued **exploratory analysis + solver evidence**: broader
structural investigation (10 analysis scripts), failed construction attempts, and solver
certificates through `m=30`. It also sketched a literature-based existence argument, but that
portion is not yet independently verified for this directed decomposition problem.

Neither strategy is strictly superior:
- The GPT approach produced a **novel explicit construction** — arguably more valuable for
  mathematical insight and for generating specific decompositions
- The Opus approach produced richer structural analysis plus the widest solver range (`m <= 30`),
  and proposed literature leads for an all-`m` result (unverified) — arguably more valuable as a research survey

### 3. The cleanroom construction is novel relative to Knuth

The independently discovered `(u,v,w)` construction is **distinct from Knuth's `(i,j,k)` / `s`-based
construction**. Both produce valid odd-`m` decompositions but assign different permutations at most
vertices. The cleanroom proof (skew-product lift with CRT parameter selection) is more algebraically
structured than Knuth's orbit-based argument. This demonstrates that LLMs can independently discover
non-trivial mathematical constructions that differ from known solutions to the same problem.

### 4. Speed vs. depth tradeoff

| | Fast + Focused | Slow + Exploratory |
|---|---|---|
| **Model** | GPT-5.3-Codex (12m) | Claude Opus 4.6 (52m) |
| **Construction found?** | Yes (identical to 5.2) | No |
| **Unique insights** | Minimal beyond construction | S_3 saturation, linear invariant analysis, cyclic symmetry |
| **Proof strategy** | Constructive (original) | Computational (solver) + literature sketch (unverified) |

GPT-5.3's efficiency came from a more direct problem-solving path; Opus's exploration produced
richer structural understanding at the cost of not finding the key construction. Whether the
exploration is "wasted" depends on the goal: for a one-shot solve, 5.3 wins; for a research survey,
Opus's structural findings are independently valuable.

### 5. Harness effectiveness is model-agnostic

The `AGENTS.md` harness produced consistent process outcomes across all three models:
- All built verifiers first
- All maintained worklogs with exact commands
- All archived machine-readable artifacts
- All documented failed approaches
- All maintained restart-safe context capsules

This validates the harness design: the structured execution protocol transfers across model
families without modification. The harness shapes *how* models work (disciplined, reproducible,
evidence-based) but not *what* they discover (that depends on the model's mathematical capabilities).

### 6. Even-`m` remains the hard open problem

No run produced a general even-`m` construction. Cleanroom A's parity obstruction proof shows that
the natural `(v,w)`-only approach fundamentally cannot work for even `m`. Opus provides solver
certificates through `m=30` but no general construction; its literature-proof sketch remains
unverified. The even-`m` case likely requires either:
- A construction with essential `u`-dependence (breaking the skew-product structure)
- A fundamentally different approach (e.g., the recursive/group-theoretic methods Opus suggested)

---

## Summary Table

| Dimension | Baseline (5.2) | Cleanroom A (5.2) | Cleanroom B (5.3) | Cleanroom C (Opus 4.6) |
|-----------|:--------------:|:------------------:|:------------------:|:----------------------:|
| **Paper access** | Yes (after 30m) | No | No | No |
| **Active time** | 2h 38m | 1h 08m | 12m 33s | 51m 45s |
| **Construction found** | Replicated Knuth's | Novel (skew-product) | Novel (same as A) | None |
| **Proof originality** | Paraphrase | Original | Original | Computational + literature leads |
| **Proof scope** | Odd m > 2 | Odd m >= 5 | Odd m >= 5 | `m <= 30` (solver); all-`m` claim TBD |
| **Even-m evidence** | m=4,6,8 | m=4,...,16 | m=4,...,12 | m=4,...,30 |
| **m=3 counting** | Full (11502/1012/996; 4554/760) | — | — | — |
| **Structural insights** | From paper | Parity obstruction | (Same as A) | S_3, linear invariants, symmetry |
| **Failed attempts documented** | — | 5 | 4 | 4 |
| **README quality** | N/A (multi-author) | Professional | Professional | Research-paper quality |
| **Efficiency** | Moderate | Good | Excellent | Moderate (exploration-heavy) |
