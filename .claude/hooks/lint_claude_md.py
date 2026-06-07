"""PostToolUse hook: run structural eval lint after any .claude/**/*.md edit.

Reads tool input from stdin (JSON), checks if the edited file is under .claude/.
If so, runs pytest evals/test_structural.py. Exits 2 on failure to block the action.
"""

from __future__ import annotations

import fnmatch
import json
import subprocess
import sys


def main() -> None:
    try:
        payload = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    file_path: str = payload.get("tool_input", {}).get("file_path", "")
    if not file_path:
        sys.exit(0)

    # Normalize to relative path for matching
    relative = file_path.lstrip("/")
    if not fnmatch.fnmatch(relative, "*.claude/**/*.md") and not fnmatch.fnmatch(
        file_path, "*/.claude/**/*.md"
    ):
        # Also handle paths like /app/.claude/agents/foo.md
        if ".claude/" not in file_path or not file_path.endswith(".md"):
            sys.exit(0)

    result = subprocess.run(  # noqa: S603
        [  # noqa: S607
            "pytest",
            "evals/test_structural.py",
            "-q",
            "--tb=short",
            "--no-header",
        ],
        capture_output=False,
    )
    sys.exit(result.returncode if result.returncode == 0 else 2)


if __name__ == "__main__":
    main()
