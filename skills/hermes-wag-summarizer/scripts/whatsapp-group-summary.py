#!/usr/bin/env python3
"""
WhatsApp Group Summary Parser
Reads ~/.hermes/whatsapp/messages.jsonl and filters messages for a target group
within the last N hours.

Usage: python whatsapp-group-summary.py <chat_id> [<hours_back>]
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

def sanitize_text(text: str) -> str:
    """Remove invisible Unicode characters that can trigger cron prompt-injection scanner."""
    if not isinstance(text, str):
        return text
    invisible_chars = {
        '\u200b', '\u200c', '\u200d', '\u2060', '\ufeff',
        '\u202a', '\u202b', '\u202c', '\u202d', '\u202e'
    }
    for char in invisible_chars:
        text = text.replace(char, '')
    return text

def get_messages_file():
    """Find the messages.jsonl file."""
    home = Path.home()
    base = home / ".hermes" / "whatsapp" / "messages.jsonl"
    if base.exists():
        return base
    backup = home / ".hermes" / "whatsapp" / "messages.jsonl.1"
    if backup.exists():
        return backup
    return base

def main():
    if len(sys.argv) < 2:
        print("Usage: whatsapp-group-summary.py <chat_id> [hours_back]", file=sys.stderr)
        sys.exit(1)

    target_chat = sys.argv[1].strip()
    hours_back = int(sys.argv[2]) if len(sys.argv) > 2 else 12

    messages_file = get_messages_file()
    if not messages_file.exists():
        print(json.dumps({
            "error": "messages.jsonl not found",
            "checked_path": str(messages_file),
            "message_count": 0,
            "messages": [],
        }))
        sys.exit(0)

    now_ts = datetime.now(timezone.utc).timestamp()
    cutoff_ts = now_ts - (hours_back * 3600)

    messages = []
    total_lines = 0
    matched_lines = 0

    try:
        with open(messages_file, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                total_lines += 1
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if obj.get("chatId") != target_chat:
                    continue

                timestamp = obj.get("timestamp", 0)
                if timestamp < cutoff_ts:
                    continue

                matched_lines += 1
                messages.append({
                    "senderName": sanitize_text(obj.get("senderName", "Unknown")),
                    "senderId": obj.get("senderId", ""),
                    "body": sanitize_text(obj.get("body", "")),
                    "timestamp": timestamp,
                    "hasMedia": obj.get("hasMedia", False),
                    "mediaType": obj.get("mediaType", ""),
                })

        result = {
            "target_chat": target_chat,
            "hours_back": hours_back,
            "now_utc": datetime.now(timezone.utc).isoformat(),
            "cutoff_utc": datetime.fromtimestamp(cutoff_ts, tz=timezone.utc).isoformat(),
            "total_lines_scanned": total_lines,
            "matched_messages": matched_lines,
            "message_count": len(messages),
            "messages": messages,
        }

        print(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:
        print(json.dumps({
            "error": str(e),
            "message_count": 0,
            "messages": [],
        }), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
