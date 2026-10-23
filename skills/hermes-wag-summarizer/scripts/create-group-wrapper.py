#!/usr/bin/env python3
"""
Helper script to create a new WhatsApp group summary wrapper.

Usage:
    python create-group-wrapper.py \\
        --chat-id "120363402262217562@g.us" \\
        --group-name "VibeDev ID" \\
        --hours 12
"""

import argparse
import os
from pathlib import Path

TEMPLATE = '''#!/usr/bin/env python3
"""
Auto-generated wrapper for {group_name} WhatsApp Group Summary.
"""

import subprocess
import sys

TARGET_CHAT = "{chat_id}"
HOURS_BACK = {hours_back}

result = subprocess.run(
    [sys.executable, "whatsapp-group-summary.py", TARGET_CHAT, str(HOURS_BACK)],
    capture_output=True,
    text=True,
)

if result.stdout:
    print(result.stdout, end="")
if result.stderr:
    print(result.stderr, end="", file=sys.stderr)

sys.exit(result.returncode)
'''

def main():
    parser = argparse.ArgumentParser(description="Create WhatsApp group summary wrapper")
    parser.add_argument("--chat-id", required=True, help="WhatsApp group chat ID (e.g. 12036...@g.us)")
    parser.add_argument("--group-name", required=True, help="Group name (used for filename)")
    parser.add_argument("--hours", type=int, default=12, help="Hours back to summarize (default: 12)")
    args = parser.parse_args()

    safe_name = args.group_name.lower().replace(" ", "-").replace("_", "-")
    filename = f"{safe_name}-summary.py"
    output_path = Path.home() / ".hermes" / "scripts" / filename

    content = TEMPLATE.format(
        group_name=args.group_name,
        chat_id=args.chat_id,
        hours_back=args.hours
    )

    output_path.write_text(content)
    os.chmod(output_path, 0o755)

    print(f"✅ Wrapper created: {output_path}")
    print(f"   Chat ID : {args.chat_id}")
    print(f"   Hours   : {args.hours}")
    print()
    print("Next step: create cronjob with:")
    print(f'hermes cron create --name "{args.group_name} Summary" --script "{output_path}" --schedule "0 5,17 * * *" --deliver "whatsapp:{args.chat_id}"')

if __name__ == "__main__":
    main()
