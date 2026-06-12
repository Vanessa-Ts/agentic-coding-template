"""Shared helpers for behavioral evals (Phase 2 — local-only, pass@k)."""

from __future__ import annotations

import json
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).parent.parent
AGENTS_DIR = REPO_ROOT / ".claude" / "agents"
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _strip_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Return (frontmatter_dict, body) from a markdown file."""
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    fm: dict[str, Any] = yaml.safe_load(parts[1]) or {}
    return fm, parts[2].strip()


def load_agent_spec(name: str) -> tuple[str, str]:
    """Return (model, system_prompt) for a named agent."""
    content = (AGENTS_DIR / f"{name}.md").read_text()
    fm, body = _strip_frontmatter(content)
    model: str = fm.get("model", "claude-sonnet-4-6")
    return model, body


def run_agent(agent_name: str, user_prompt: str, k: int = 3) -> list[str]:
    """Invoke an agent via claude CLI k times. Returns list of text outputs.

    Uses --system-prompt to load the agent's instruction set.
    Requires claude CLI in PATH and an active Claude subscription.
    """
    model, system_prompt = load_agent_spec(agent_name)
    outputs: list[str] = []
    for _ in range(k):
        proc = subprocess.run(  # noqa: S603
            [  # noqa: S607
                "claude",
                "-p",
                user_prompt,
                "--output-format",
                "json",
                "--model",
                model,
                "--system-prompt",
                system_prompt,
            ],
            capture_output=True,
            text=True,
            timeout=180,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            try:
                data = json.loads(proc.stdout.strip())
                outputs.append(str(data.get("result", proc.stdout)))
            except json.JSONDecodeError:
                outputs.append(proc.stdout)
        else:
            outputs.append("")
    return outputs


def passes_at_k(
    outputs: list[str],
    check: Callable[[str], bool],
    min_pass: int = 2,
) -> bool:
    """Return True if at least min_pass outputs satisfy check."""
    return sum(1 for o in outputs if check(o)) >= min_pass
