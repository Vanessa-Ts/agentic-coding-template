#!/usr/bin/env python3
"""PostToolUse hook for Edit|Write|MultiEdit — auto-formats changed Python files."""

import json
import shutil
import subprocess
import sys

payload = json.load(sys.stdin)
tool_input = payload.get("tool_input", {})
tool_name = payload.get("tool_name", "")

paths: list[str] = []
if tool_name == "Write":
    paths.append(tool_input.get("file_path", ""))
elif tool_name == "Edit":
    paths.append(tool_input.get("file_path", ""))
elif tool_name == "MultiEdit":
    paths.append(tool_input.get("file_path", ""))

ruff = shutil.which("ruff") or "ruff"

for path in paths:
    if not path.endswith(".py"):
        continue
    subprocess.run([ruff, "format", path], capture_output=True)
    subprocess.run([ruff, "check", "--fix", path], capture_output=True)

sys.exit(0)
