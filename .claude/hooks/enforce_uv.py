#!/usr/bin/env python3
"""PreToolUse hook for Bash — enforces uv over pip/poetry."""

import json
import re
import sys

BLOCKED_PATTERNS = [
    r"pip\s+install",
    r"pip3\s+install",
    r"python\s+-m\s+pip",
    r"poetry\s+add",
]

payload = json.load(sys.stdin)
command = payload.get("tool_input", {}).get("command", "")

for pattern in BLOCKED_PATTERNS:
    if re.search(pattern, command):
        print(
            "Blocked: use `uv add <pkg>` instead — see uv-workflows skill",
            file=sys.stderr,
        )
        sys.exit(2)
