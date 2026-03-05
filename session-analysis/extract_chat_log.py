#!/usr/bin/env python3
"""
Extract a readable chat log from a Codex session JSONL file.

Usage:
    python3 extract_chat_log.py SESSION.jsonl --out chat-log.md
"""
import argparse
import json
import re
from pathlib import Path


def extract_messages(path: Path):
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            if entry.get("type") != "response_item":
                continue
            payload = entry.get("payload", {})
            role = payload.get("role")
            if role not in {"user", "assistant"}:
                continue
            if payload.get("type") != "message":
                continue

            parts = []
            for item in payload.get("content", []):
                if item.get("type") in {"input_text", "output_text"}:
                    text = item.get("text", "").strip()
                    if text:
                        parts.append(text)
            if not parts:
                continue
            rows.append(
                {
                    "timestamp": entry.get("timestamp", ""),
                    "role": role,
                    "text": "\n".join(parts).strip(),
                }
            )
    return rows


def write_markdown(rows, source: Path, out: Path):
    m = re.search(
        r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
        source.name,
    )
    session_id = m.group(1) if m else source.stem
    lines = [
        f"# Chat Log - Session {session_id}",
        "",
        f"- Source: `{source}`",
        f"- Messages extracted: {len(rows)}",
        "",
    ]
    for i, row in enumerate(rows, start=1):
        lines.append(f"## {i}. {row['role'].title()} ({row['timestamp']})")
        lines.append("")
        lines.append(row["text"])
        lines.append("")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Extract chat log from Codex JSONL.")
    parser.add_argument("session_jsonl", help="Input rollout-*.jsonl file")
    parser.add_argument(
        "--out",
        required=True,
        help="Output markdown path",
    )
    args = parser.parse_args()

    source = Path(args.session_jsonl)
    rows = extract_messages(source)
    write_markdown(rows, source, Path(args.out))
    print(f"Wrote {args.out} ({len(rows)} messages)")


if __name__ == "__main__":
    main()
