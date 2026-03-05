# Session Analysis

Tools and archived session data for analyzing AI coding assistant sessions used in the claudescycles-revisited project.

## Cleanroom 5.4: GPT-5.4 Extension Session

This branch (`cleanroom-5.4`) contains a single Codex CLI session where GPT-5.4 was given an autonomous prompt to build search/verification code and produce a rigorous proof for the directed graph decomposition problem. The session was nearly one-shot: the model worked autonomously for ~23 minutes, with only a single follow-up instruction to write a README and commit.

### Session Summary

| Metric | Value |
|---|---|
| **Session ID** | `019cbf6f-5309-7432-abd8-417875f27e40` |
| **Model** | GPT-5.4 via Codex CLI 0.110.0 |
| **Type** | Mostly autonomous (1 autonomous phase + 1 interactive follow-up) |
| **Wall time** | 24m 43s |
| **Active time** | 24m 43s (100% -- zero idle gaps) |
| **Turns** | 2 (initial prompt + commit/README instruction) |
| **Tool calls** | 81 |
| **Total tokens** | 4.60M (4.54M input, 63.8K output) |
| **Input cache rate** | 96.0% (4.36M / 4.54M cached) |
| **Reasoning tokens** | 30.9K (49% of output) |
| **Events** | 397 |

### Phase Breakdown

| Phase | Type | Duration | Tool Calls | Output Tokens | Description |
|---|---|---|---|---|---|
| 0 | Autonomous | 22m 35s | 69 | 57.9K | Core implementation: verification, CP-SAT search, odd-m construction, tests, proof |
| 1 | Interactive | 2m 8s | 12 | 5.9K | README + git commit (user-requested) |

### Key Observations

- **Near-oneshot**: One prompt produced the entire implementation (22m 35s autonomous phase). The only follow-up was a request to write a README and commit, which took 2m 8s.
- **High cache efficiency**: 96.0% of input tokens were cache hits, indicating efficient context reuse across 81 tool calls.
- **Balanced reasoning**: 30.9K of 63.8K output tokens (49%) were reasoning tokens -- a lower reasoning ratio than the 5.2 session (67%), suggesting GPT-5.4 spent more of its budget on direct code/text output relative to chain-of-thought.
- **Compact output**: 32.8K non-reasoning output tokens across 81 tool calls (~405 tokens per tool call average), indicating concise, targeted actions.
- **100% active**: Zero idle gaps across the entire 24m 43s session -- continuous work from start to finish.
- **Substantial output**: 36 files changed, +7,911 lines in a single commit covering library code, scripts, tests, artifacts, proofs, and documentation.

### What GPT-5.4 Produced

- Deterministic core library (`claudescycles/`) with graph construction, verification, JSON I/O, and odd-m construction
- CP-SAT search tooling (`scripts/search_cp_sat.py`) finding witnesses for m = 3, 4, 6, 8, 10, 12, 14
- Explicit odd-m construction with validation for m = 5..31
- Return-map verification for all odd m in 5..31
- 9 passing tests covering verifier failure modes and odd-family correctness
- Partial theorem proving odd-m decompositions for every odd m >= 5
- Machine-readable artifacts in `artifacts/`

### Comparison with Cleanroom 5.2 (GPT-5.2)

| Metric | 5.2 (GPT-5.2) | 5.4 (GPT-5.4) |
|---|---|---|
| Wall time | 26m 24s | 24m 43s |
| Turns | 1 (pure oneshot) | 2 (1 autonomous + 1 follow-up) |
| Tool calls | 79 | 81 |
| Total tokens | 8.23M | 4.60M |
| Input tokens | 8.16M | 4.54M |
| Output tokens | 69.3K | 63.8K |
| Reasoning % | 67% | 49% |
| Cache rate | 99.1% | 96.0% |
| Events | 546 | 397 |
| Files changed | N/A | 36 (+7,911 lines) |

Notable: GPT-5.4 used ~44% fewer total tokens than 5.2 for comparable work, with fewer events (397 vs 546) and a lower reasoning ratio, suggesting more efficient processing.

### Hourly Event Distribution

```
2026-03-05 19:00 UTC: ################### (397 events)
```

All events fit within a single clock-hour.

## Scripts

### `analyze_sessions.py`

General-purpose session analyzer for Claude Code and Codex CLI JSONL files. Supports analyzing specific files or discovering sessions from default locations.

```bash
# Analyze a specific session file
python3 analyze_sessions.py codex-sessions/rollout-*.jsonl

# Phase breakdown (splits Codex sessions into autonomous/interactive phases)
python3 analyze_sessions.py --phases codex-sessions/rollout-*.jsonl

# Machine-readable JSON
python3 analyze_sessions.py --json codex-sessions/rollout-*.jsonl

# Discover all sessions for a project (from ~/.codex and ~/.claude)
python3 analyze_sessions.py --project-filter claudescycles

# Custom idle threshold (default: 300s = 5 minutes)
python3 analyze_sessions.py --idle-threshold 600 session.jsonl
```

## Archived Session

| Session ID | File | Duration | Tool Calls | Tokens | Summary |
|---|---|---|---|---|---|
| `019cbf6f` | `rollout-...-019cbf6f-...jsonl` (886K) | 25m | 81 | 4.6M | Full implementation: verification, CP-SAT search (m=3..14), odd-m construction (m=5..31), partial proof, tests |

Raw session JSONL is archived in `codex-sessions/` for posterity and future analysis. The file is a complete event log (metadata, prompts, model responses, tool calls, token counts).

## Session Data Locations

### Codex CLI (live)
```
~/.codex/sessions/2026/03/06/rollout-*.jsonl
```

### Codex CLI (archived)
```
session-analysis/codex-sessions/rollout-*.jsonl
```

## Key Metrics

- **Wall time**: Clock time from first to last event
- **Active time**: Sum of inter-event gaps < idle threshold (default 5m)
- **Tool calls**: Shell commands, file reads/writes executed by the model
- **Token usage**: Cumulative input/output tokens (Codex reports running totals)
- **Reasoning tokens**: Chain-of-thought tokens used by the model (Codex-specific)

## Phase Classification

A phase is classified as **autonomous** if the wall time between user messages exceeds the threshold (default 5 minutes). Otherwise it's **interactive**. This session has two phases: one autonomous (22m 35s of continuous work) and one interactive (2m 8s for the README/commit follow-up).
