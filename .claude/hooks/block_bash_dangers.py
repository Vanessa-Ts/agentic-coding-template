#!/usr/bin/env python3
"""PreToolUse hook for Bash — blocks destructive git/shell patterns."""

import json
import re
import subprocess
import sys

DANGER_PATTERNS = [
    r"rm\s+-rf",
    r"git\s+push\s+(-f\b|--force(?!-with-lease)|--force$)",
    r"git\s+reset\s+--hard",
    r"git\s+push\s+.*\bmain\b",
]

payload = json.load(sys.stdin)
command = payload.get("tool_input", {}).get("command", "")

for pattern in DANGER_PATTERNS:
    if re.search(pattern, command):
        print(f"Blocked: dangerous pattern '{pattern}' in command", file=sys.stderr)
        sys.exit(2)

# Block git commit on main branch
if re.search(r"git\s+commit", command):
    try:
        branch = subprocess.check_output(
            ["git", "branch", "--show-current"], text=True
        ).strip()
        if branch == "main":
            print("Blocked: git commit directly on main branch", file=sys.stderr)
            sys.exit(2)
    except subprocess.SubprocessError:
        pass
