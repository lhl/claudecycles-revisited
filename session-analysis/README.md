# Session Analysis

Tools for analyzing AI coding assistant sessions used in the claudescycles project.

## Overview

This project used two AI coding tools:

- **Codex CLI (GPT-5.2/5.3)**: Setup sessions + main autonomous work session
- **Claude Code (Opus 4.6)**: Interactive review and REVIEW.md revision

The main Codex session had three key autonomous phases:
1. **Clean room implementation** (~6h): Built verifier, CSP search, independently found m=3,
   then consulted PDF and implemented/validated the odd-m construction with proof
2. **Review writing** (~11m): Cross-checked against Knuth paper and wrote REVIEW.md
3. **FOLLOWUP gap filling** (~31m): Extended implementation to feature parity with the paper

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
