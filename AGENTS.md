# claudescycles - Agent Execution Guide

This file defines working rules for autonomous coding/research agents in this repo.
If this file conflicts with higher-priority platform instructions, follow the higher-priority instructions.

## Mission

Solve the directed graph decomposition problem defined in `PROBLEM.md` with reproducible code, verifiable outputs, and durable project memory.

## Working Style

We do not require heavyweight spec-driven waterfall for every task.
We do require:
- clear punchlists
- persistent worklog memory
- measurable validation
- tight iterate-validate-document loops

## Available Tools and Libraries

The following solver/constraint libraries are installed and available for use:

- **z3** (Z3 theorem prover / SMT solver)
- **pysat** (SAT solver toolkit)
- **ortools** (Google OR-Tools, including CP-SAT constraint solver with `AddCircuit`)
- **pulp** (LP/MIP solver interface)

Standard scientific Python is also available (numpy, scipy, networkx, etc.).

## Shared Repo Safety (Must Follow)

- Run `git status -sb` before starting; treat it as baseline state.
- If unrelated changes exist, leave them untouched and stage only your task files.
- Never discard work you did not create (`git restore`, `git checkout --`, `git reset --hard`, destructive rewrites).
- If a file is actively contested by another agent, stop and coordinate before editing it.

## Source of Truth Files (Project Memory)

These files are mandatory and act as durable memory across restarts:

- `docs/IMPLEMENTATION.md`: authoritative punchlist, active plan, deferrals, validation status.
- `WORKLOG.md`: chronological log of major actions, commands, outcomes, and decisions.
- `state/CONTEXT.md`: short restart capsule (current objective, latest evidence, next actions).

If missing, create them before substantial implementation.

## Non-Negotiable Logging Discipline

After each meaningful experiment/test batch, update memory files before continuing:

1. Update `WORKLOG.md` with:
   - exact command(s) run
   - key result/metric
   - interpretation (pass/fail/improved/regressed)
2. Update `docs/IMPLEMENTATION.md` punchlist status.
3. Refresh `state/CONTEXT.md` if direction changed.

Do not run long sequences of experiments without writing results down.

## Context Management and Restart Recovery

- Every 20-30 minutes (or when context gets noisy), compress state into `state/CONTEXT.md`.
- Keep `state/CONTEXT.md` to one screen:
  - objective
  - best current candidate
  - latest validated metrics
  - open questions
  - next 1-3 actions
- After any restart, read `state/CONTEXT.md`, then `docs/IMPLEMENTATION.md`, then `WORKLOG.md` before taking new actions.

## Default Execution Loop

Use this loop for each punchlist item:

1. Pick one unchecked item from `docs/IMPLEMENTATION.md`.
2. Write a brief pre-analysis note (scope, risk, validation plan).
3. Implement minimal change (code, script, or experiment setup).
4. Run correctness checks first.
5. Run performance/search benchmark when optimization or exploration quality matters.
6. Compare against baseline and decide: keep or revert.
7. Record evidence in `WORKLOG.md` and update punchlist status.
8. Commit if the change is correct and useful.

## Optimization Loop (Benchmark-Gated)

For optimization work, always follow:

1. Implement optimization candidate.
2. Run correctness tests/smoke tests.
3. Run benchmark and compare against baseline.
4. Update `docs/IMPLEMENTATION.md` and `WORKLOG.md` with numbers.
5. If improved and correct: keep + commit.
6. If regressed or unclear: revert code change, keep documentation update, continue to next candidate.
7. Repeat until optimization backlog is exhausted or explicitly paused.

## Claim Integrity (Done Means Proven)

Any claim of "done", "solved", or "improved" must include all three:

- test/verification evidence (exact command + outcome)
- runtime/algorithm evidence (what path/rule was exercised)
- docs parity evidence (punchlist + worklog updated)

Avoid overclaiming; scope statements to tested ranges and conditions.

## Commit Discipline

- Commit on logical task completion (not every edit, not long after done).
- Stage explicitly; do not use `git add .` or `git add -A`.
- Review staged files and staged diff before commit:
  - `git diff --staged --name-only`
  - `git diff --staged`
- Use conventional commit style when possible (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`).

## Initial Punchlist Template (Discover + Prove)

Seed `docs/IMPLEMENTATION.md` with this checklist and track progress there:

- [ ] P0: Repository bootstrap
- [ ] P0: Create/verify `docs/IMPLEMENTATION.md`, `WORKLOG.md`, `state/CONTEXT.md`
- [ ] P0: Add deterministic verifier script for cycle decomposition validity
- [ ] P1: Build search/solver tooling to find decompositions for small `m`
- [ ] P1: Discover valid decompositions and candidate construction patterns
- [ ] P1: Archive outputs under `artifacts/` with command provenance
- [ ] P2: Generalize candidate patterns and validate over broad `m` ranges
- [ ] P2: Investigate both odd and even `m` cases
- [ ] P3: Attempt a formal proof (or clearly scoped partial proof) in `proofs/`
- [ ] P3: Catalog failed constructions and failure modes (not just successes)
- [ ] P4: Write final summary of proven facts, open conjectures, and next experiments

## Worklog Entry Format

Use concise entries with evidence:

```md
## YYYY-MM-DD
### Task: <short label>
- Plan: <what was attempted>
- Commands: `<exact command>`
- Result: <key outputs/metrics>
- Decision: <keep/revert/next>
```

## Blockers

If blocked by missing requirements, conflicting edits, or failing infrastructure:

- record blocker in `WORKLOG.md`
- mark related item as blocked in `docs/IMPLEMENTATION.md`
- propose the smallest unblocking action
- continue with other unblocked punchlist items when possible

## Keep This File Updated

When you discover a better workflow for memory durability, restart safety, or optimization throughput, update this file in the same change that proves the improvement.
