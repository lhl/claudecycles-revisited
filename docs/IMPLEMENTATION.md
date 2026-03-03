# IMPLEMENTATION - claudescycles

## Objective

Replicate and extend the decomposition results from `claude-cycles.pdf` with reproducible code, explicit evidence, and restart-safe workflow.

## Baseline

- Primary source: `claude-cycles.pdf`
- Current status: initial workflow setup
- Evidence policy: every completed item must cite exact command(s) and outcomes
- Problem control files: `PROBLEM.md` (replication), `PROBLEM2.md` (extension)

## Pre-Analysis (Update Before Each Major Item)

- Scope:
- Risks:
- Validation plan:
- Expected artifacts:

## Active Punchlist

- [x] P0-01: Bootstrap workflow files (`AGENTS.md`, `docs/IMPLEMENTATION.md`, `WORKLOG.md`, `state/CONTEXT.md`)
- [x] P0-01a: Add `PROBLEM.md` (original problem statement for replication-only runs)
- [x] P0-01b: Add `PROBLEM2.md` (extension brief for post-replication work)
- [ ] P0-02: Add deterministic verifier script for decomposition validity
- [ ] P1-01: Reproduce odd-`m` validity in a documented range
- [ ] P1-02: Reproduce even-`m` failure behavior for current rule set
- [ ] P1-03: Save reproduction outputs under `artifacts/` with command provenance
- [ ] P2-01: Reproduce `m=3` Hamiltonian cycle count claims from the paper
- [ ] P2-02: Reproduce generalizable subset counts and decomposition counts
- [ ] P2-03: Cross-check counting results with an independent implementation path
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
- `apply_patch` to create `PROBLEM2.md` -> success
