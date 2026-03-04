# Session Analysis

Tools for analyzing AI coding assistant sessions used in the claudescycles project.

## Overview

This project used two AI coding tools:

- **Codex CLI (GPT-5.2/5.3)**: Setup sessions + main autonomous work session
- **Claude Code (Opus 4.6)**: Interactive review and REVIEW.md revision

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

## Session Data Locations

### Codex CLI
```
~/.codex/sessions/2026/03/04/rollout-*.jsonl
```

### Claude Code
```
~/.claude/projects/-home-lhl-github-lhl-claudescycles/*.jsonl
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
