# Session Analysis

Tools and archived session data for analyzing the cleanroom-5.3 Codex session in the claudescycles-revisited project.

Comparison note: `cleanroom-5.2` session data is archived only as a baseline reference. The primary work session here is the `cleanroom-5.3` clean-room implementation run (`019cbc54-445c-7721-a313-f748f91b7dd2`).

## Cleanroom 5.3 Session

| Metric | Value |
|---|---|
| Session ID | `019cbc54-445c-7721-a313-f748f91b7dd2` |
| Model | `gpt-5.3-codex` (Codex CLI `0.110.0`) |
| Wall / Active | `12m 33s` / `12m 33s` (100%) |
| Turns / User msgs | `1` / `1` |
| Tool calls | `64` |
| Tokens | `5.45M` total (`5.41M` input, `42.5K` output, `17.7K` reasoning) |
| Cache rate | `98.6%` cached input (`5.34M / 5.41M`) |
| Events | `394` |

Generated artifacts:

- `session-analysis/codex-sessions/rollout-2026-03-04T19-48-53-019cb877-0545-7a70-9c93-f87f34564fc3.jsonl` (baseline reference)
- `session-analysis/codex-sessions/rollout-2026-03-05T13-49-25-019cbc54-445c-7721-a313-f748f91b7dd2.jsonl`
- `session-analysis/chat-logs/019cbc54-445c-7721-a313-f748f91b7dd2.md`
- `session-analysis/reports/019cbc54-summary.txt`
- `session-analysis/reports/019cbc54-phases.txt`
- `session-analysis/reports/019cbc54-summary.json`
- `session-analysis/reports/cleanroom-5.2-vs-5.3.txt` (comparison report)

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

### `extract_chat_log.py`

Extract role-ordered user/assistant text from a Codex session JSONL into Markdown.

```bash
python3 extract_chat_log.py \
  codex-sessions/rollout-2026-03-05T13-49-25-019cbc54-445c-7721-a313-f748f91b7dd2.jsonl \
  --out chat-logs/019cbc54-445c-7721-a313-f748f91b7dd2.md
```

## Archived Session

| Session ID | File | Duration | Tool Calls | Tokens | Summary |
|---|---|---|---|---|---|
| `019cb877` | `rollout-...-019cb877-...jsonl` (906K) | 26m | 79 | 8.2M | cleanroom-5.2 baseline session retained for comparison only |
| `019cbc54` | `rollout-...-019cbc54-...jsonl` (632K) | 12m | 64 | 5.45M | cleanroom-5.3 implementation run (verifier/search/construction/proof artifacts) |

Raw session JSONLs are archived in `codex-sessions/` for posterity and future analysis.

## Session Data Locations

### Codex CLI (live)
```
~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl
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

A phase is classified as **autonomous** if the wall time between user messages exceeds the threshold (default 5 minutes). Otherwise it's **interactive**.
