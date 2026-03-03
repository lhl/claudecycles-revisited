# CONTEXT CAPSULE

## Objective
Replicate and extend `claude-cycles.pdf` results with reproducible scripts.

## Current Best Known
- AGENTS/process scaffolding created.
- Starter punchlist and worklog initialized.
- Problem split created:
  - `PROBLEM.md` for replication-only mode
  - `PROBLEM2.md` for extension mode after baseline replication

## Latest Validated Evidence
- None yet in this capsule (bootstrap only).

## Open Questions
- Best script architecture for verifier/counting/search loops.
- Feasible strategy for reproducing `m=3` count claims efficiently.

## Next Actions
1. Implement deterministic decomposition verifier script.
2. Run baseline replication using `PROBLEM.md` only (with `PROBLEM2.md` and PDF removed from context).
3. Store artifacts and update punchlist statuses.
4. Re-introduce `PROBLEM2.md` for extension loop once baseline is reproduced.
