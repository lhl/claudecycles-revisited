#!/usr/bin/env python3
"""
Analyze Claude Code and Codex CLI sessions for the claudescycles project.

Extends the base session analyzer with:
  - Phase detection: splits Codex sessions into autonomous/interactive phases
    bounded by user messages
  - Per-phase token deltas, tool call counts, and duration
  - Phase classification (autonomous vs interactive) by gap duration
  - In-progress session support
  - Project-specific session discovery and labeling

Usage:
    python3 analyze_claudescycles.py                    # full analysis
    python3 analyze_claudescycles.py --json             # machine-readable JSON
    python3 analyze_claudescycles.py --phases-only      # just the main session phases
    python3 analyze_claudescycles.py --autonomous-threshold 600  # 10-min threshold
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Import base utilities
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent))
from analyze_sessions import (
    format_duration,
    format_tokens,
    parse_ts,
    load_jsonl,
    compute_activity,
    compute_hourly_histogram,
    analyze_claude_session,
    print_claude_session,
)

# ---------------------------------------------------------------------------
# Project constants
# ---------------------------------------------------------------------------
PROJECT_CWD = "/home/lhl/github/lhl/claudescycles"
PROJECT_FILTER = "claudescycles"
CLAUDE_PROJECT_DIR = os.path.expanduser(
    "~/.claude/projects/-home-lhl-github-lhl-claudescycles"
)
CODEX_SESSIONS_DIR = os.path.expanduser("~/.codex/sessions")


# ---------------------------------------------------------------------------
# Phase analysis for Codex sessions
# ---------------------------------------------------------------------------

def extract_codex_phases(filepath, autonomous_threshold=300):
    """
    Split a Codex session into phases bounded by user messages.

    Each phase starts with a user message (or session start) and ends at the
    next user message (or session end).  Returns a list of phase dicts with
    timing, token deltas, tool call counts, and classification.

    autonomous_threshold: minimum seconds between user messages to classify
    a phase as "autonomous" (default 5 minutes).
    """
    entries = load_jsonl(filepath)
    if not entries:
        return None

    # --- Collect structured events ---
    meta = {}
    all_timestamps = []
    user_messages = []      # (entry_index, timestamp, text)
    token_snapshots = []    # (entry_index, timestamp, usage_dict)
    tool_call_indices = []  # entry indices of function_call events
    turn_indices = []       # entry indices of turn_context events

    for i, entry in enumerate(entries):
        ts_str = entry.get("timestamp")
        ts = None
        if ts_str:
            try:
                ts = parse_ts(ts_str)
                all_timestamps.append(ts)
            except (ValueError, TypeError):
                pass

        etype = entry.get("type", "")
        payload = entry.get("payload", {})

        if etype == "session_meta":
            meta = payload

        elif etype == "turn_context":
            turn_indices.append(i)

        elif etype == "event_msg":
            pt = payload.get("type", "")
            if pt == "token_count":
                info = payload.get("info")
                if info is None:
                    continue
                usage = info.get("total_token_usage")
                if usage:
                    token_snapshots.append((i, ts, usage))

        elif etype == "response_item":
            role = payload.get("role", "")
            item_type = payload.get("type", "")
            if role == "user":
                content = payload.get("content", [])
                if isinstance(content, list):
                    for c in content:
                        if isinstance(c, dict) and c.get("type") == "input_text":
                            text = c["text"]
                            # Skip system/developer instructions
                            if not text.startswith("#") and not text.startswith("<"):
                                user_messages.append((i, ts, text))
                            break
            elif item_type == "function_call":
                tool_call_indices.append(i)

        elif etype == "compacted":
            # Don't double-count user messages from compacted history
            pass

    if not all_timestamps:
        return None

    all_timestamps.sort()
    session_start = all_timestamps[0]
    session_end = all_timestamps[-1]
    model = meta.get("model", "")
    # Try to get model from turn_context if meta doesn't have it
    if not model:
        for entry in entries:
            if entry.get("type") == "turn_context":
                model = entry.get("payload", {}).get("model", "")
                if model:
                    break

    # --- Build phases ---
    # Phase boundaries are at each user message
    # Phase i: from user_messages[i] to user_messages[i+1] (or session end)
    phases = []
    for pi in range(len(user_messages)):
        um_idx, um_ts, um_text = user_messages[pi]

        # Phase start = this user message
        phase_start_idx = um_idx
        phase_start_ts = um_ts

        # Phase end = next user message or session end
        if pi + 1 < len(user_messages):
            next_um_idx, next_um_ts, _ = user_messages[pi + 1]
            phase_end_idx = next_um_idx
            phase_end_ts = next_um_ts
            is_last = False
        else:
            phase_end_idx = len(entries)
            phase_end_ts = session_end
            is_last = True

        # Duration
        if phase_start_ts and phase_end_ts:
            duration = (phase_end_ts - phase_start_ts).total_seconds()
        else:
            duration = 0

        # Tool calls in this phase
        phase_tool_calls = sum(
            1 for idx in tool_call_indices
            if phase_start_idx <= idx < phase_end_idx
        )

        # Turn contexts in this phase
        phase_turns = sum(
            1 for idx in turn_indices
            if phase_start_idx <= idx < phase_end_idx
        )

        # Token deltas: find last token snapshot before phase start and end
        def last_snapshot_before(entry_idx):
            result = None
            for tidx, tts, tusage in token_snapshots:
                if tidx < entry_idx:
                    result = tusage
                else:
                    break
            return result

        def last_snapshot_in_range(start_idx, end_idx):
            result = None
            for tidx, tts, tusage in token_snapshots:
                if start_idx <= tidx < end_idx:
                    result = tusage
            return result

        tokens_at_start = last_snapshot_before(phase_start_idx)
        tokens_at_end = last_snapshot_in_range(phase_start_idx, phase_end_idx)
        if tokens_at_end is None:
            tokens_at_end = last_snapshot_before(phase_end_idx)

        if tokens_at_start and tokens_at_end:
            token_delta = {
                "input": tokens_at_end.get("input_tokens", 0) - tokens_at_start.get("input_tokens", 0),
                "output": tokens_at_end.get("output_tokens", 0) - tokens_at_start.get("output_tokens", 0),
                "total": tokens_at_end.get("total_tokens", 0) - tokens_at_start.get("total_tokens", 0),
            }
        elif tokens_at_end and pi == 0:
            # First phase: absolute values
            token_delta = {
                "input": tokens_at_end.get("input_tokens", 0),
                "output": tokens_at_end.get("output_tokens", 0),
                "total": tokens_at_end.get("total_tokens", 0),
            }
        else:
            token_delta = {"input": 0, "output": 0, "total": 0}

        # Activity within this phase
        phase_timestamps = [
            ts for ts in all_timestamps
            if phase_start_ts and phase_end_ts
            and phase_start_ts <= ts <= phase_end_ts
        ]
        phase_activity = compute_activity(phase_timestamps, idle_threshold=autonomous_threshold)

        # Classify: autonomous if duration > threshold and driven by single prompt
        classification = "autonomous" if duration > autonomous_threshold else "interactive"

        phases.append({
            "phase_index": pi,
            "classification": classification,
            "prompt": um_text[:300],
            "prompt_short": " ".join(um_text.split())[:120],
            "start": phase_start_ts.isoformat() if phase_start_ts else None,
            "end": phase_end_ts.isoformat() if phase_end_ts else None,
            "wall_seconds": duration,
            "active_seconds": phase_activity["active_seconds"],
            "idle_seconds": phase_activity["idle_seconds"],
            "tool_calls": phase_tool_calls,
            "turns": phase_turns,
            "entry_range": [phase_start_idx, phase_end_idx],
            "tokens": token_delta,
            "is_last": is_last,
        })

    # --- Session-level summary ---
    last_token = token_snapshots[-1][2] if token_snapshots else {}
    total_tokens = {
        "input": last_token.get("input_tokens", 0),
        "cached_input": last_token.get("cached_input_tokens", 0),
        "output": last_token.get("output_tokens", 0),
        "reasoning": last_token.get("reasoning_output_tokens", 0),
        "total": last_token.get("total_tokens", 0),
    }

    autonomous_phases = [p for p in phases if p["classification"] == "autonomous"]
    interactive_phases = [p for p in phases if p["classification"] == "interactive"]

    return {
        "session_id": meta.get("id", Path(filepath).stem),
        "file": os.path.basename(filepath),
        "cwd": meta.get("cwd", ""),
        "model": model,
        "cli_version": meta.get("cli_version", ""),
        "start": session_start.isoformat(),
        "end": session_end.isoformat(),
        "wall_seconds": (session_end - session_start).total_seconds(),
        "status": "in-progress" if phases and phases[-1]["is_last"] and (
            session_end == all_timestamps[-1]
        ) else "completed",
        "total_events": len(entries),
        "total_user_messages": len(user_messages),
        "total_tool_calls": len(tool_call_indices),
        "tokens": total_tokens,
        "phases": phases,
        "summary": {
            "autonomous_phases": len(autonomous_phases),
            "interactive_phases": len(interactive_phases),
            "autonomous_seconds": sum(p["wall_seconds"] for p in autonomous_phases),
            "interactive_seconds": sum(p["wall_seconds"] for p in interactive_phases),
            "autonomous_tool_calls": sum(p["tool_calls"] for p in autonomous_phases),
            "interactive_tool_calls": sum(p["tool_calls"] for p in interactive_phases),
            "autonomous_output_tokens": sum(p["tokens"]["output"] for p in autonomous_phases),
            "interactive_output_tokens": sum(p["tokens"]["output"] for p in interactive_phases),
        },
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_phase_analysis(result):
    """Print a detailed phase breakdown of a Codex session."""
    print(f"\n{'=' * 80}")
    print(f"CODEX SESSION: claudescycles (phase analysis)")
    print(f"{'=' * 80}")
    print(f"\n  Session:    {result['session_id'][:36]}")
    print(f"  Model:      {result['model']} (CLI {result.get('cli_version', '?')})")
    print(f"  CWD:        {result['cwd']}")
    print(f"  Time span:  {result['start'][:16]} -> {result['end'][:16]} UTC")
    print(f"  Wall time:  {format_duration(result['wall_seconds'])}")
    print(f"  Events:     {result['total_events']}")
    print(f"  User msgs:  {result['total_user_messages']}")
    print(f"  Tool calls: {result['total_tool_calls']}")

    t = result["tokens"]
    if t["total"]:
        print(f"  Tokens:     {format_tokens(t['input'])} input ({format_tokens(t['cached_input'])} cached)")
        print(f"              {format_tokens(t['output'])} output ({format_tokens(t['reasoning'])} reasoning)")
        print(f"              {format_tokens(t['total'])} total")

    s = result["summary"]
    print(f"\n  {'─' * 40}")
    print(f"  Autonomous: {s['autonomous_phases']} phases, "
          f"{format_duration(s['autonomous_seconds'])}, "
          f"{s['autonomous_tool_calls']} tool calls, "
          f"{format_tokens(s['autonomous_output_tokens'])} output tokens")
    print(f"  Interactive: {s['interactive_phases']} phases, "
          f"{format_duration(s['interactive_seconds'])}, "
          f"{s['interactive_tool_calls']} tool calls, "
          f"{format_tokens(s['interactive_output_tokens'])} output tokens")

    print(f"\n  {'─' * 40}")
    print(f"  PHASE BREAKDOWN")
    print(f"  {'─' * 40}")

    for p in result["phases"]:
        tag = "AUTONOMOUS" if p["classification"] == "autonomous" else "INTERACTIVE"
        status = " (in-progress)" if p["is_last"] else ""
        print(f"\n  Phase {p['phase_index']}: [{tag}]{status}")
        print(f"    Prompt:     {p['prompt_short']}")
        if p["start"] and p["end"]:
            print(f"    Time:       {p['start'][11:19]} -> {p['end'][11:19]} UTC "
                  f"({format_duration(p['wall_seconds'])})")
        if p["active_seconds"] > 0:
            pct = p["active_seconds"] / max(p["wall_seconds"], 1) * 100
            print(f"    Active:     {format_duration(p['active_seconds'])} ({pct:.0f}%)")
        print(f"    Tool calls: {p['tool_calls']}")
        pt = p["tokens"]
        if pt["total"]:
            print(f"    Tokens:     {format_tokens(pt['input'])} input + "
                  f"{format_tokens(pt['output'])} output = "
                  f"{format_tokens(pt['total'])} total")
        print(f"    Entries:    [{p['entry_range'][0]}:{p['entry_range'][1]}]")


def print_setup_session(result, label=""):
    """Print a compact summary for a setup/short session."""
    tag = f" ({label})" if label else ""
    print(f"\n  Session{tag}: {result['session_id'][:36]}")
    print(f"    Model:      {result['model']} (CLI {result.get('cli_version', '?')})")
    print(f"    Time:       {result['start'][:16]} -> {result['end'][:16]} UTC "
          f"({format_duration(result['wall_seconds'])})")
    print(f"    User msgs:  {result['total_user_messages']}")
    print(f"    Tool calls: {result['total_tool_calls']}")
    t = result["tokens"]
    if t["total"]:
        print(f"    Tokens:     {format_tokens(t['total'])} total "
              f"({format_tokens(t['output'])} output)")


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def find_project_codex_sessions():
    """Find all Codex sessions for the claudescycles project."""
    base = Path(CODEX_SESSIONS_DIR)
    if not base.exists():
        return []

    results = []
    for f in sorted(base.rglob("rollout-*.jsonl")):
        # Quick check: read session_meta to filter by cwd
        try:
            with open(f) as fh:
                first_line = fh.readline().strip()
                if first_line:
                    entry = json.loads(first_line)
                    cwd = entry.get("payload", {}).get("cwd", "")
                    if PROJECT_FILTER in cwd:
                        results.append(f)
        except (json.JSONDecodeError, IOError):
            continue
    return results


def find_project_claude_sessions():
    """Find all Claude Code sessions for the claudescycles project."""
    p = Path(CLAUDE_PROJECT_DIR)
    if not p.exists():
        return []
    return sorted(p.glob("*.jsonl"))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Analyze claudescycles project sessions (Claude Code + Codex CLI)."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output machine-readable JSON",
    )
    parser.add_argument(
        "--phases-only",
        action="store_true",
        help="Only show the main session's phase breakdown",
    )
    parser.add_argument(
        "--autonomous-threshold",
        type=int,
        default=300,
        help="Seconds between user messages to classify as autonomous (default: 300)",
    )
    parser.add_argument(
        "--idle-threshold",
        type=int,
        default=300,
        help="Seconds of inactivity before a gap is considered idle (default: 300)",
    )
    args = parser.parse_args()

    all_results = {"codex_sessions": [], "claude_sessions": []}

    # --- Codex sessions ---
    codex_files = find_project_codex_sessions()
    for f in codex_files:
        result = extract_codex_phases(f, args.autonomous_threshold)
        if result:
            all_results["codex_sessions"].append(result)

    # --- Claude Code sessions ---
    claude_files = find_project_claude_sessions()
    for f in claude_files:
        result = analyze_claude_session(f, args.idle_threshold)
        if result and result["user_turns"] > 0:
            all_results["claude_sessions"].append(result)

    # --- JSON output ---
    if args.json_output:
        print(json.dumps(all_results, indent=2, default=str))
        return

    # --- Human-readable output ---

    # Find the main session (largest by event count)
    codex_sessions = all_results["codex_sessions"]
    main_session = None
    setup_sessions = []
    if codex_sessions:
        codex_sessions.sort(key=lambda r: r["total_events"])
        main_session = codex_sessions[-1]  # largest
        setup_sessions = sorted(codex_sessions[:-1], key=lambda r: r["start"])

    if not args.phases_only and setup_sessions:
        print("=" * 80)
        print("CODEX SETUP SESSIONS")
        print("=" * 80)
        for i, r in enumerate(setup_sessions):
            label = f"setup-{i}"
            print_setup_session(r, label)

    if main_session:
        print_phase_analysis(main_session)

    if not args.phases_only and all_results["claude_sessions"]:
        print()
        print("=" * 80)
        print("CLAUDE CODE SESSIONS (interactive review)")
        print("=" * 80)
        for r in all_results["claude_sessions"]:
            print_claude_session(r)

    # --- Grand summary ---
    if not args.phases_only:
        print()
        print("=" * 80)
        print("GRAND SUMMARY")
        print("=" * 80)

        total_codex_tokens = sum(
            r["tokens"]["total"] for r in codex_sessions
        )
        total_claude_tokens = sum(
            r["tokens"]["total_api"] for r in all_results["claude_sessions"]
        )

        print(f"\n  Codex sessions:   {len(codex_sessions)} "
              f"({format_tokens(total_codex_tokens)} total tokens)")
        print(f"  Claude sessions:  {len(all_results['claude_sessions'])} "
              f"({format_tokens(total_claude_tokens)} total tokens)")

        if main_session:
            s = main_session["summary"]
            total_auto = s["autonomous_seconds"]
            total_inter = s["interactive_seconds"]
            print(f"\n  Main session autonomous time:  {format_duration(total_auto)}")
            print(f"  Main session interactive time: {format_duration(total_inter)}")
            auto_out = s["autonomous_output_tokens"]
            inter_out = s["interactive_output_tokens"]
            print(f"  Autonomous output tokens:      {format_tokens(auto_out)}")
            print(f"  Interactive output tokens:      {format_tokens(inter_out)}")

    if not codex_sessions and not all_results["claude_sessions"]:
        print("No sessions found for claudescycles project.")


if __name__ == "__main__":
    main()
