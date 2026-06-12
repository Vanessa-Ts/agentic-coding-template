"""Phase 3 — skill activation matrix.

Asserts that each skill's path globs match exactly the file paths they should trigger on,
using fnmatch — no LLM calls. Runs in CI on every push.
"""

from __future__ import annotations

import fnmatch
import re
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"

KEYWORD_ONLY_SKILLS: frozenset[str] = frozenset({"blog-post", "review", "infografik"})


def _strip_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    fm: dict[str, Any] = yaml.safe_load(parts[1]) or {}
    return fm, parts[2].strip()


def _load_skill_paths(skill_name: str) -> list[str]:
    """Return glob patterns for a skill. Raises if keyword-only."""
    skill_dir = SKILLS_DIR / skill_name
    content = (skill_dir / "SKILL.md").read_text()
    fm, body = _strip_frontmatter(content)
    if "paths" in fm:
        return [str(p) for p in fm["paths"]]
    for line in body.splitlines()[:10]:
        m = re.search(r"\*\*Trigger paths\*\*:\s*(.+)", line)
        if m:
            return re.findall(r"`([^`]+)`", m.group(1))
    return []


def _matches_skill(file_path: str, skill_name: str) -> bool:
    """True if file_path matches any of the skill's path globs."""
    for pattern in _load_skill_paths(skill_name):
        if fnmatch.fnmatch(file_path, pattern):
            return True
    return False


# ---------------------------------------------------------------------------
# Trigger matrix parametrization
# Each entry: (skill_name, file_path, should_match)
# ---------------------------------------------------------------------------

TRIGGER_MATRIX: list[tuple[str, str, bool]] = [
    # fastapi-conventions
    ("fastapi-conventions", "src/app/routes/items.py", True),
    ("fastapi-conventions", "src/app/models/item.py", True),
    ("fastapi-conventions", "src/app/main.py", True),
    ("fastapi-conventions", "tests/test_items.py", False),
    ("fastapi-conventions", "pyproject.toml", False),
    # pytest-patterns
    ("pytest-patterns", "tests/test_items.py", True),
    ("pytest-patterns", "tests/conftest.py", True),
    ("pytest-patterns", "evals/conftest.py", True),
    ("pytest-patterns", "src/app/routes/items.py", False),
    # uv-workflows
    ("uv-workflows", "pyproject.toml", True),
    ("uv-workflows", "uv.lock", True),
    ("uv-workflows", "src/app/main.py", False),
    # infrastructure
    ("infrastructure", "Dockerfile", True),
    ("infrastructure", ".github/workflows/ci.yml", True),
    ("infrastructure", "docker-compose.yml", True),
    ("infrastructure", "src/app/main.py", False),
    # spec-feature
    ("spec-feature", "docs/specs/my-feature.md", True),
    ("spec-feature", "docs/plans/my-plan.md", False),
    # openapi
    ("openapi", "openapi.yml", True),
    ("openapi", "openapi.json", True),
    ("openapi", "docs/api/reference.md", True),
    ("openapi", "src/app/main.py", False),
    # doc — pattern is docs/**/*.md (requires at least one subdir)
    ("doc", "docs/plans/agent-evals.md", True),
    ("doc", "docs/api/reference.md", True),
    ("doc", "src/app/main.py", False),
    # frontend — src/app/ui/** matches all files in that dir including non-html
    ("frontend", "src/app/ui/dashboard.html", True),
    ("frontend", "templates/index.html", True),
    ("frontend", "src/app/routes/items.py", False),
]


@pytest.mark.parametrize(
    ("skill", "file_path", "expected"),
    TRIGGER_MATRIX,
    ids=[f"{s}::{p}=={'match' if e else 'no-match'}" for s, p, e in TRIGGER_MATRIX],
)
def test_skill_activation(skill: str, file_path: str, expected: bool) -> None:
    result = _matches_skill(file_path, skill)
    if expected:
        assert result, (
            f"Skill '{skill}' should trigger on '{file_path}' "
            f"but none of its patterns matched. Patterns: {_load_skill_paths(skill)}"
        )
    else:
        assert not result, (
            f"Skill '{skill}' should NOT trigger on '{file_path}' "
            f"but a pattern matched. Patterns: {_load_skill_paths(skill)}"
        )


@pytest.mark.parametrize(
    "skill_name",
    sorted(KEYWORD_ONLY_SKILLS),
    ids=lambda s: s,
)
def test_keyword_only_skills_have_empty_path_list(skill_name: str) -> None:
    paths = _load_skill_paths(skill_name)
    assert paths == [], (
        f"Skill '{skill_name}' is keyword-only but returned paths: {paths}"
    )
