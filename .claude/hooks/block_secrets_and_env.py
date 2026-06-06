#!/usr/bin/env python3
"""PreToolUse hook for Edit|Write|MultiEdit — blocks .env writes and secret patterns."""

import json
import os
import re
import sys

SECRET_PATTERNS = [
    r"AKIA[A-Z0-9]{16}",
    r"ghp_[A-Za-z0-9]{36}",
    r"sk-[a-zA-Z0-9]{48}",
    r"sk-ant-[a-zA-Z0-9\-_]{90,}",
    r"-----BEGIN .* PRIVATE KEY-----",
]

payload = json.load(sys.stdin)
tool_input = payload.get("tool_input", {})
tool_name = payload.get("tool_name", "")

# Collect (file_path, text_to_scan) pairs
targets: list[tuple[str, str]] = []

if tool_name == "Write":
    targets.append((tool_input.get("file_path", ""), tool_input.get("content", "")))
elif tool_name == "Edit":
    targets.append((tool_input.get("file_path", ""), tool_input.get("new_string", "")))
elif tool_name == "MultiEdit":
    fp = tool_input.get("file_path", "")
    for edit in tool_input.get("edits", []):
        targets.append((fp, edit.get("new_string", "")))

for file_path, text in targets:
    if os.path.basename(file_path) == ".env":
        print(f"Blocked: direct write to .env file ({file_path})", file=sys.stderr)
        sys.exit(2)
    for pattern in SECRET_PATTERNS:
        match = re.search(pattern, text)
        if match:
            print(
                f"Blocked: secret pattern '{pattern}' found in {file_path}",
                file=sys.stderr,
            )
            sys.exit(2)
