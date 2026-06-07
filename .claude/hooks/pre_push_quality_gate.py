#!/usr/bin/env python3
"""PreToolUse hook for Bash — runs full quality gate before git push."""

import json
import re
import subprocess
import sys

payload = json.load(sys.stdin)
command = payload.get("tool_input", {}).get("command", "")

if not re.search(r"git\s+push", command):
    sys.exit(0)

CHECKS = [
    ["ruff", "format", "--check", "."],
    ["ruff", "check", "."],
    ["mypy", "--strict", "src/"],
    ["pytest", "-x", "-q", "--no-header"],
]

for cmd in CHECKS:
    result = subprocess.run(cmd, capture_output=True, text=True)  # noqa: S603
    if result.returncode != 0:
        label = " ".join(cmd)
        print(f"Blocked: quality gate failed — {label}", file=sys.stderr)
        if result.stdout.strip():
            print(result.stdout, file=sys.stderr)
        if result.stderr.strip():
            print(result.stderr, file=sys.stderr)
        sys.exit(2)
