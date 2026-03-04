# Session Analysis

Tools for analyzing AI coding assistant sessions used in the claudescycles project.

## Overview

This project used two AI coding tools:

- **Codex CLI (GPT-5.2/5.3)**: Setup sessions + main autonomous work session
- **Claude Code (Opus 4.6)**: Interactive review, REVIEW.md→README.md revision, session analysis, docs finalization

The main Codex session had three key autonomous phases:
1. **"Clean room" implementation → informed replication** (~6h wall, ~47m active): Built verifier, CSP search,
   independently found m=3. However, the clean-room boundary was porous: setup session
   memory files (`state/CONTEXT.md`, `docs/IMPLEMENTATION.md`) already referenced
   `claude-cycles.pdf`, and the PDF was accessible at `../claude-cycles.pdf`. After only
   **~30 minutes** (19:00:51–19:31:14 UTC) the model searched for and read the paper when
   its CSP solver failed to scale and no SAT/ILP solvers were available. The remaining
   ~5.5 hours were spent implementing and validating the Knuth construction with proof.
2. **Review writing** (~11m): Cross-checked against Knuth paper and wrote REVIEW.md
3. **FOLLOWUP gap filling** (~31m): Extended implementation to feature parity with the paper

### PDF access timeline (Phase 0)

The transition from independent to informed work is precisely located in the session data:

| UTC Time | Event |
|---|---|
| 19:00:51 | Phase 0 starts — verifier + CSP solver built |
| 19:27–19:30 | CSP finds m=3 but fails on m=5 (200K nodes) |
| 19:30:58 | Checks for z3, pysat, ortools, pulp — none found |
| **19:31:14** | `find .. -maxdepth 2 -name "*claude*cycles*.pdf"` |
| 19:31:24 | `pdftotext -layout ../claude-cycles.pdf` — reads paper |
| 19:33:40 | Already writing `claude.py` (Knuth construction) |

This demonstrates that **clean-room isolation requires path-level sandboxing**, not just
omitting files from the repo. The model knew the PDF existed (from setup session context)
and rationally searched for it when its independent approach hit a wall. The "active" metric
(~47 minutes for Phase 0) better matches the perceived duration in the UI than raw wall time.

## Scripts

### `analyze_claudescycles.py`

Project-specific analyzer with phase detection. Splits Codex sessions into autonomous
and interactive phases bounded by user messages.

```bash
# Full analysis (setup sessions + main session phases + Claude Code + summary)
python3 analyze_claudescycles.py

# Just the main session's phase breakdown
python3 analyze_claudescycles.py --phases-only

# Machine-readable JSON
python3 analyze_claudescycles.py --json

# Custom autonomous threshold (default: 300s = 5 minutes)
python3 analyze_claudescycles.py --autonomous-threshold 600
```

### `analyze_sessions.py`

General-purpose base analyzer (from [fsr4-rdna3](https://github.com/lhl/fsr4-rdna3)).
Handles Claude Code and Codex CLI session discovery and parsing.

```bash
# All sessions for this project
python3 analyze_sessions.py --project-filter claudescycles

# JSON output piped to jq
python3 analyze_sessions.py --project-filter claudescycles --json | \
  jq '.[] | {tool, session_id: .session_id[:12], wall: .wall_seconds}'
```

## Archived Codex Sessions

Raw session JSONLs are archived in `codex-sessions/` for posterity and future analysis.
Each file is a complete event log (metadata, prompts, model responses, tool calls, token counts).

| Session ID | File | Duration | Summary |
|---|---|---|---|
| `019cb4f4` | `rollout-...-019cb4f4-...jsonl` (436K) | 30m | **Setup**: Read Knuth's PDF, surveyed AGENTS.md patterns from other repos, built project scaffolding (`AGENTS.md`, `PROBLEM.md`, `state/CONTEXT.md`, `docs/IMPLEMENTATION.md`) |
| `019cb512` | `rollout-...-019cb512-...jsonl` (4.6M) | 18h 11m | **Replication**: One-shot autonomous implementation (verifier, CSP, odd-`m` construction, proofs), review writing, followup gap filling, README accuracy pass. 18 phases, 392 tool calls, 41.2M tokens |
| `019cb877` | `rollout-...-019cb877-...jsonl` (906K) | 26m | **Extension**: CP-SAT even-`m` solver (found m=4,6,8), symmetry verification (136/0 counts). 79 tool calls, 8.2M tokens |

Two short-lived sessions (019cb4f1, 019cb510) were aborted false starts and are not archived.

## Archived Claude Code Sessions

Raw session JSONLs are archived in `claude-sessions/` for posterity and future analysis.
Each file is a complete event log (timestamps, user/assistant messages, tool calls, token usage with cache breakdowns).

| Session ID | File | Wall / Active | Turns | Tokens | Summary |
|---|---|---|---|---|---|
| `4ee5a7fb` | `4ee5a7fb-...jsonl` (2.4M) | 11h 40m / 57m | 188 user, 315 assistant | 33.5M API tokens | **Review + Analysis**: Interactive REVIEW.md editing (citation corrections, formula fixes), session analysis tooling setup, Codex session scanning (PDF access timeline discovery), extension review, README framing |
| `dc550b0c` | `dc550b0c-...jsonl` (552K) | 1h 3m / 11m | 43 user, 65 assistant | 4.0M API tokens | **Docs finalization**: Extension review (CP-SAT even-m, symmetry), Future Directions section, final docs commit |

One additional session (`0b08c8f6`, 567 bytes) was a false start with only a SessionStart hook event and no conversation.

## Session Data Locations

### Codex CLI (live)
```
~/.codex/sessions/2026/03/04/rollout-*.jsonl
```

### Codex CLI (archived)
```
session-analysis/codex-sessions/rollout-*.jsonl
```

### Claude Code (live)
```
~/.claude/projects/-home-lhl-github-lhl-claudescycles/*.jsonl
```

### Claude Code (archived)
```
session-analysis/claude-sessions/*.jsonl
```

## Phase Classification

A phase is classified as **autonomous** if the wall time between user messages exceeds
the threshold (default 5 minutes). Otherwise it's **interactive**.

Note: Wall time includes human idle time between prompts, so an "autonomous" phase's
wall time may be much longer than its active compute time. The `active` metric
(derived from event timestamp gaps) is a better measure of actual AI work time.

## Key Metrics

- **Wall time**: Clock time from first to last event
- **Active time**: Sum of inter-event gaps < idle threshold (default 5m)
- **Tool calls**: Shell commands, file reads/writes executed by the model
- **Token usage**: Cumulative input/output tokens (Codex reports running totals;
  per-phase values are computed as deltas)
- **Reasoning tokens**: Chain-of-thought tokens used by the model (Codex-specific)

## Combined Project Session Summary

| Tool | Sessions | Total Wall | Total Active | Total Tokens | Role |
|---|---|---|---|---|---|
| Codex CLI (GPT-5.2/5.3) | 3 useful + 2 aborted | ~19h wall | ~2h 57m | 50.8M | Autonomous implementation: scaffolding, replication, extension |
| Claude Code (Opus 4.6) | 2 useful + 1 false start | ~12h 43m wall | ~1h 9m | 37.5M | Interactive review: citations, analysis tooling, docs finalization |
| **Total** | **5 useful sessions** | **~31h 43m wall** | **~4h 6m active** | **88.3M tokens** | |

All session JSONLs are archived in `codex-sessions/` and `claude-sessions/` respectively.
