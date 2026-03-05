#!/usr/bin/env python3
"""
Analyze Claude Code and Codex CLI session JSONL files.

Extracts timing, turns, token usage, active/idle time, and user messages
from session logs stored by each tool's native format.

Usage:
    # Analyze specific session file(s)
    python3 analyze_sessions.py session.jsonl
    python3 analyze_sessions.py codex-sessions/*.jsonl claude-sessions/*.jsonl

    # Discover sessions from default locations
    python3 analyze_sessions.py --project-filter fsr4    # filter by project path
    python3 analyze_sessions.py --idle-threshold 600     # 10-min idle gap threshold

    # Output formats
    python3 analyze_sessions.py session.jsonl --json     # machine-readable JSON
    python3 analyze_sessions.py session.jsonl --phases   # phase breakdown (Codex)
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def format_duration(seconds):
    """Human-readable duration string."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"
    else:
        return f"{int(seconds // 3600)}h {int((seconds % 3600) // 60)}m"


def format_tokens(n):
    """Human-readable token count."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def parse_ts(ts_str):
    """Parse an ISO timestamp string to a timezone-aware datetime."""
    return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))


def load_jsonl(filepath):
    """Load a JSONL file, skipping malformed lines."""
    entries = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


# ---------------------------------------------------------------------------
# Active / idle time analysis
# ---------------------------------------------------------------------------

def compute_activity(timestamps, idle_threshold=300):
    """
    Given a sorted list of datetimes, split wall time into active vs idle.

    A gap between consecutive events larger than idle_threshold seconds is
    considered idle time.  Returns a dict with active_seconds, idle_seconds,
    and a list of idle_gaps (start, end, gap_seconds).
    """
    if len(timestamps) < 2:
        return {"active_seconds": 0, "idle_seconds": 0, "idle_gaps": []}

    active = 0.0
    idle = 0.0
    gaps = []

    for i in range(1, len(timestamps)):
        gap = (timestamps[i] - timestamps[i - 1]).total_seconds()
        if gap < idle_threshold:
            active += gap
        else:
            idle += gap
            gaps.append({
                "start": timestamps[i - 1].isoformat(),
                "end": timestamps[i].isoformat(),
                "seconds": gap,
            })

    return {"active_seconds": active, "idle_seconds": idle, "idle_gaps": gaps}


def compute_hourly_histogram(timestamps):
    """Return a dict of {hour_label: event_count}."""
    hist = {}
    for ts in timestamps:
        key = ts.strftime("%Y-%m-%d %H:00 UTC")
        hist[key] = hist.get(key, 0) + 1
    return dict(sorted(hist.items()))


# ---------------------------------------------------------------------------
# Claude Code session parser
# ---------------------------------------------------------------------------

def analyze_claude_session(filepath, idle_threshold=300):
    """
    Parse a Claude Code JSONL session file.

    Entry types:
      - type: "user"      -> user turn, message.content has text
      - type: "assistant"  -> assistant turn, message.usage has token counts
      - type: "progress"   -> tool progress events
      - type: "system"     -> system events (hooks, etc.)
    """
    entries = load_jsonl(filepath)
    if not entries:
        return None

    user_turns = 0
    assistant_turns = 0
    total_input = 0
    total_output = 0
    total_cache_create = 0
    total_cache_read = 0
    first_user_msg = ""
    model = ""
    timestamps = []

    for entry in entries:
        ts_str = entry.get("timestamp")
        if ts_str:
            try:
                timestamps.append(parse_ts(ts_str))
            except (ValueError, TypeError):
                pass

        etype = entry.get("type", "")

        if etype == "user":
            user_turns += 1
            if not first_user_msg:
                msg = entry.get("message", {})
                content = msg.get("content", "")
                if isinstance(content, list):
                    for c in content:
                        if isinstance(c, dict) and c.get("type") == "text":
                            first_user_msg = c["text"][:300]
                            break
                elif isinstance(content, str):
                    first_user_msg = content[:300]

        elif etype == "assistant":
            assistant_turns += 1
            msg = entry.get("message", {})
            if not model:
                model = msg.get("model", "")
            usage = msg.get("usage", {})
            if usage:
                total_input += usage.get("input_tokens", 0)
                total_output += usage.get("output_tokens", 0)
                total_cache_create += usage.get("cache_creation_input_tokens", 0)
                total_cache_read += usage.get("cache_read_input_tokens", 0)

    if not timestamps:
        return None

    timestamps.sort()
    start = timestamps[0]
    end = timestamps[-1]
    duration = (end - start).total_seconds()
    activity = compute_activity(timestamps, idle_threshold)

    return {
        "tool": "claude-code",
        "session_id": Path(filepath).stem,
        "file": os.path.basename(filepath),
        "model": model,
        "first_user_msg": first_user_msg,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "wall_seconds": duration,
        "active_seconds": activity["active_seconds"],
        "idle_seconds": activity["idle_seconds"],
        "idle_gaps": activity["idle_gaps"],
        "user_turns": user_turns,
        "assistant_turns": assistant_turns,
        "tokens": {
            "input": total_input,
            "output": total_output,
            "cache_create": total_cache_create,
            "cache_read": total_cache_read,
            "total_api": total_input + total_output + total_cache_create + total_cache_read,
        },
    }


# ---------------------------------------------------------------------------
# Codex CLI session parser
# ---------------------------------------------------------------------------

def analyze_codex_session(filepath, idle_threshold=300):
    """
    Parse a Codex CLI JSONL session file.

    Entry types:
      - type: "session_meta"   -> session metadata (cwd, model, cli_version)
      - type: "turn_context"   -> per-turn context (model, cwd, approval_policy)
      - type: "event_msg"      -> events (task_started/completed, token_count, etc.)
      - type: "response_item"  -> messages and function calls
      - type: "compacted"      -> compacted history with replacement_history array
    """
    entries = load_jsonl(filepath)
    if not entries:
        return None

    meta = {}
    timestamps = []
    last_token_usage = None
    turn_count = 0
    tool_calls = 0
    model = ""
    user_messages = []  # list of (timestamp, text)

    for entry in entries:
        ts_str = entry.get("timestamp")
        ts = None
        if ts_str:
            try:
                ts = parse_ts(ts_str)
                timestamps.append(ts)
            except (ValueError, TypeError):
                pass

        etype = entry.get("type", "")
        payload = entry.get("payload", {})

        if etype == "session_meta":
            meta = payload

        elif etype == "turn_context":
            turn_count += 1
            if not model:
                model = payload.get("model", "")

        elif etype == "event_msg":
            pt = payload.get("type", "")
            if pt == "token_count":
                info = payload.get("info")
                if info and "total_token_usage" in info:
                    last_token_usage = info["total_token_usage"]

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
                                user_messages.append((ts, text[:300]))
                            break
            elif item_type == "function_call":
                tool_calls += 1

        elif etype == "compacted":
            replacement = payload.get("replacement_history", [])
            for item in replacement:
                if isinstance(item, dict) and item.get("role") == "user":
                    content = item.get("content", [])
                    if isinstance(content, list):
                        for c in content:
                            if isinstance(c, dict) and c.get("type") == "input_text":
                                text = c["text"]
                                if not text.startswith("#") and not text.startswith("<"):
                                    user_messages.append((ts, text[:300]))
                                break

    if not timestamps:
        return None

    timestamps.sort()
    start = timestamps[0]
    end = timestamps[-1]
    duration = (end - start).total_seconds()
    activity = compute_activity(timestamps, idle_threshold)
    hourly = compute_hourly_histogram(timestamps)

    cwd = meta.get("cwd", "")
    tokens = last_token_usage or {}

    # Deduplicate user messages (compacted replays produce duplicates)
    seen_texts = set()
    unique_messages = []
    for ts_val, text in user_messages:
        key = text[:80]
        if key not in seen_texts:
            seen_texts.add(key)
            unique_messages.append({
                "timestamp": ts_val.isoformat() if ts_val else None,
                "text": text,
            })

    return {
        "tool": "codex-cli",
        "session_id": meta.get("id", Path(filepath).stem),
        "file": os.path.basename(filepath),
        "cwd": cwd,
        "model": model,
        "cli_version": meta.get("cli_version", ""),
        "first_user_msg": unique_messages[0]["text"] if unique_messages else "",
        "start": start.isoformat(),
        "end": end.isoformat(),
        "wall_seconds": duration,
        "active_seconds": activity["active_seconds"],
        "idle_seconds": activity["idle_seconds"],
        "idle_gaps": activity["idle_gaps"],
        "turns": turn_count,
        "unique_user_messages": len(unique_messages),
        "user_messages": unique_messages,
        "tool_calls": tool_calls,
        "hourly_events": hourly,
        "tokens": {
            "input": tokens.get("input_tokens", 0),
            "cached_input": tokens.get("cached_input_tokens", 0),
            "output": tokens.get("output_tokens", 0),
            "reasoning": tokens.get("reasoning_output_tokens", 0),
            "total": tokens.get("total_tokens", 0),
        },
        "total_events": len(entries),
    }


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def find_claude_sessions(claude_dir):
    """Find all Claude Code session JSONL files in a project directory."""
    p = Path(claude_dir)
    if not p.exists():
        return []
    return sorted(p.glob("*.jsonl"))


def find_codex_sessions(codex_base, date_dirs=None):
    """
    Find Codex session JSONL files.

    If date_dirs is provided, search only those subdirectories.
    Otherwise search all date directories under codex_base/sessions/.
    """
    base = Path(codex_base) / "sessions"
    if not base.exists():
        return []

    if date_dirs:
        dirs = [base / d for d in date_dirs if (base / d).exists()]
    else:
        dirs = sorted(base.rglob("*.jsonl"))
        return dirs

    results = []
    for d in dirs:
        results.extend(sorted(d.glob("rollout-*.jsonl")))
    return results


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_claude_session(r):
    """Print a Claude Code session summary."""
    print(f"\n  Session:    {r['session_id'][:36]}")
    print(f"  Model:      {r['model']}")
    print(f"  First msg:  {r['first_user_msg'][:100]}...")
    print(f"  Time span:  {r['start'][:16]} -> {r['end'][11:16]} UTC")
    print(f"  Wall time:  {format_duration(r['wall_seconds'])}")
    print(f"  Active:     {format_duration(r['active_seconds'])} ({r['active_seconds'] / max(r['wall_seconds'], 1) * 100:.0f}%)")
    print(f"  Turns:      {r['user_turns']} user / {r['assistant_turns']} assistant")
    t = r["tokens"]
    print(f"  Tokens:     {format_tokens(t['input'])} input + {format_tokens(t['cache_create'])} cache-create + {format_tokens(t['cache_read'])} cache-read + {format_tokens(t['output'])} output")
    print(f"              = {format_tokens(t['total_api'])} total API tokens")
    if r["idle_gaps"]:
        print(f"  Idle gaps:  {len(r['idle_gaps'])}")
        for g in r["idle_gaps"]:
            print(f"              {g['start'][11:16]} -> {g['end'][11:16]} UTC ({format_duration(g['seconds'])})")


def print_codex_session(r):
    """Print a Codex CLI session summary."""
    print(f"\n  Session:    {r['session_id'][:36]}")
    print(f"  Model:      {r['model']} (CLI {r.get('cli_version', '?')})")
    print(f"  CWD:        {r['cwd']}")
    print(f"  First msg:  {r['first_user_msg'][:100]}...")
    print(f"  Time span:  {r['start'][:16]} -> {r['end'][:16]} UTC")
    print(f"  Wall time:  {format_duration(r['wall_seconds'])}")
    print(f"  Active:     {format_duration(r['active_seconds'])} ({r['active_seconds'] / max(r['wall_seconds'], 1) * 100:.0f}%)")
    print(f"  Turns:      {r['turns']} (turn contexts)")
    print(f"  User msgs:  {r['unique_user_messages']} unique")
    print(f"  Tool calls: {r['tool_calls']}")
    t = r["tokens"]
    if t["total"]:
        print(f"  Tokens:     {format_tokens(t['input'])} input ({format_tokens(t['cached_input'])} cached) + {format_tokens(t['output'])} output ({format_tokens(t['reasoning'])} reasoning)")
        print(f"              = {format_tokens(t['total'])} total")
    else:
        print(f"  Tokens:     (no token_count events)")
    print(f"  Events:     {r['total_events']}")

    if r["idle_gaps"]:
        print(f"  Idle gaps:  {len(r['idle_gaps'])}")
        for g in r["idle_gaps"]:
            print(f"              {g['start'][11:16]} -> {g['end'][11:16]} UTC ({format_duration(g['seconds'])})")

    if r["hourly_events"]:
        print(f"  Hourly events:")
        for hour, count in r["hourly_events"].items():
            bar = "#" * min(count // 20, 50)
            print(f"    {hour}: {bar} ({count})")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def detect_session_type(filepath):
    """Detect whether a JSONL file is a Claude Code or Codex CLI session."""
    with open(filepath) as f:
        first_line = f.readline().strip()
        if not first_line:
            return None
        try:
            entry = json.loads(first_line)
        except json.JSONDecodeError:
            return None
    if entry.get("type") in ("user", "assistant", "system", "progress"):
        return "claude"
    if entry.get("type") == "session_meta":
        return "codex"
    # Fallback: check filename
    name = os.path.basename(filepath)
    if name.startswith("rollout-"):
        return "codex"
    return "claude"


def analyze_file(filepath, idle_threshold=300, phases=False):
    """Analyze a single session file, auto-detecting type."""
    stype = detect_session_type(filepath)
    if stype == "codex":
        if phases:
            return ("codex-phases", extract_codex_phases(filepath, idle_threshold))
        return ("codex", analyze_codex_session(filepath, idle_threshold))
    else:
        return ("claude", analyze_claude_session(filepath, idle_threshold))


# ---------------------------------------------------------------------------
# Codex phase analysis (extracted from analyze_claudescycles.py)
# ---------------------------------------------------------------------------

def extract_codex_phases(filepath, autonomous_threshold=300):
    """
    Split a Codex session into phases bounded by user messages.

    Each phase starts with a user message (or session start) and ends at the
    next user message (or session end).  Returns a dict with per-phase timing,
    token deltas, tool call counts, and classification.

    autonomous_threshold: minimum seconds between user messages to classify
    a phase as "autonomous" (default 5 minutes).
    """
    entries = load_jsonl(filepath)
    if not entries:
        return None

    meta = {}
    all_timestamps = []
    user_messages = []
    token_snapshots = []
    tool_call_indices = []
    turn_indices = []

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
                            if not text.startswith("#") and not text.startswith("<"):
                                user_messages.append((i, ts, text))
                            break
            elif item_type == "function_call":
                tool_call_indices.append(i)

    if not all_timestamps:
        return None

    all_timestamps.sort()
    session_start = all_timestamps[0]
    session_end = all_timestamps[-1]
    model = meta.get("model", "")
    if not model:
        for entry in entries:
            if entry.get("type") == "turn_context":
                model = entry.get("payload", {}).get("model", "")
                if model:
                    break

    phases = []
    for pi in range(len(user_messages)):
        um_idx, um_ts, um_text = user_messages[pi]
        phase_start_idx = um_idx
        phase_start_ts = um_ts

        if pi + 1 < len(user_messages):
            next_um_idx, next_um_ts, _ = user_messages[pi + 1]
            phase_end_idx = next_um_idx
            phase_end_ts = next_um_ts
            is_last = False
        else:
            phase_end_idx = len(entries)
            phase_end_ts = session_end
            is_last = True

        duration = (phase_end_ts - phase_start_ts).total_seconds() if phase_start_ts and phase_end_ts else 0

        phase_tool_calls = sum(1 for idx in tool_call_indices if phase_start_idx <= idx < phase_end_idx)
        phase_turns = sum(1 for idx in turn_indices if phase_start_idx <= idx < phase_end_idx)

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
            token_delta = {
                "input": tokens_at_end.get("input_tokens", 0),
                "output": tokens_at_end.get("output_tokens", 0),
                "total": tokens_at_end.get("total_tokens", 0),
            }
        else:
            token_delta = {"input": 0, "output": 0, "total": 0}

        phase_timestamps = [
            ts for ts in all_timestamps
            if phase_start_ts and phase_end_ts and phase_start_ts <= ts <= phase_end_ts
        ]
        phase_activity = compute_activity(phase_timestamps, idle_threshold=autonomous_threshold)

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
        "tool": "codex-cli",
        "session_id": meta.get("id", Path(filepath).stem),
        "file": os.path.basename(filepath),
        "cwd": meta.get("cwd", ""),
        "model": model,
        "cli_version": meta.get("cli_version", ""),
        "start": session_start.isoformat(),
        "end": session_end.isoformat(),
        "wall_seconds": (session_end - session_start).total_seconds(),
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


def print_phase_analysis(result):
    """Print a detailed phase breakdown of a Codex session."""
    print(f"\n{'=' * 80}")
    print(f"CODEX SESSION (phase analysis)")
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
    print(f"\n  {'_' * 40}")
    print(f"  Autonomous: {s['autonomous_phases']} phases, "
          f"{format_duration(s['autonomous_seconds'])}, "
          f"{s['autonomous_tool_calls']} tool calls, "
          f"{format_tokens(s['autonomous_output_tokens'])} output tokens")
    print(f"  Interactive: {s['interactive_phases']} phases, "
          f"{format_duration(s['interactive_seconds'])}, "
          f"{s['interactive_tool_calls']} tool calls, "
          f"{format_tokens(s['interactive_output_tokens'])} output tokens")

    print(f"\n  {'_' * 40}")
    print(f"  PHASE BREAKDOWN")
    print(f"  {'_' * 40}")

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


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Claude Code and Codex CLI session JSONL files."
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Session JSONL file(s) to analyze. If omitted, discovers from default locations.",
    )
    parser.add_argument(
        "--claude-dir",
        default=os.path.expanduser("~/.claude/projects"),
        help="Claude Code projects directory (default: ~/.claude/projects)",
    )
    parser.add_argument(
        "--codex-dir",
        default=os.path.expanduser("~/.codex"),
        help="Codex CLI base directory (default: ~/.codex)",
    )
    parser.add_argument(
        "--project-filter",
        default=None,
        help="Only show sessions whose path/cwd contains this substring",
    )
    parser.add_argument(
        "--idle-threshold",
        type=int,
        default=300,
        help="Seconds of inactivity before a gap is considered idle (default: 300)",
    )
    parser.add_argument(
        "--phases",
        action="store_true",
        help="Show phase breakdown for Codex sessions",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output machine-readable JSON instead of human-readable text",
    )
    args = parser.parse_args()

    all_results = []

    if args.files:
        # --- Analyze specific files ---
        for filepath in args.files:
            if not os.path.exists(filepath):
                print(f"Warning: {filepath} not found, skipping", file=sys.stderr)
                continue
            rtype, result = analyze_file(filepath, args.idle_threshold, phases=args.phases)
            if result:
                all_results.append((rtype, result))
    else:
        # --- Discover from default locations ---
        claude_base = Path(args.claude_dir)
        if claude_base.exists():
            for project_dir in sorted(claude_base.iterdir()):
                if not project_dir.is_dir():
                    continue
                if args.project_filter and args.project_filter not in str(project_dir):
                    continue
                for f in sorted(project_dir.glob("*.jsonl")):
                    r = analyze_claude_session(f, args.idle_threshold)
                    if r and r["user_turns"] > 0:
                        all_results.append(("claude", r))

        codex_sessions = Path(args.codex_dir) / "sessions"
        if codex_sessions.exists():
            for f in sorted(codex_sessions.rglob("rollout-*.jsonl")):
                if args.phases:
                    r = extract_codex_phases(f, args.idle_threshold)
                else:
                    r = analyze_codex_session(f, args.idle_threshold)
                if not r:
                    continue
                if not args.phases and r["wall_seconds"] < 10 and r["tokens"]["total"] == 0:
                    continue
                if args.project_filter and args.project_filter not in r.get("cwd", ""):
                    continue
                rtype = "codex-phases" if args.phases else "codex"
                all_results.append((rtype, r))

    # --- Output ---
    if args.json_output:
        print(json.dumps([r for _, r in all_results], indent=2, default=str))
        return

    for rtype, r in all_results:
        if rtype == "claude":
            print_claude_session(r)
        elif rtype == "codex-phases":
            print_phase_analysis(r)
        elif rtype == "codex":
            print_codex_session(r)

    if not all_results:
        print("No sessions found.")
        if args.project_filter:
            print(f"  (filter: '{args.project_filter}')")


if __name__ == "__main__":
    main()
