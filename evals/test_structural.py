"""Phase 1 — structural validation of .claude/ agentic artifacts.

All tests are deterministic, LLM-free, and run in CI on every push.
"""

from __future__ import annotations

import fnmatch
import re
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent
AGENTS_DIR = REPO_ROOT / ".claude" / "agents"
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"
COMMANDS_DIR = REPO_ROOT / ".claude" / "commands"

KNOWN_MODELS: frozenset[str] = frozenset(
    {
        "claude-sonnet-4-6",
        "claude-haiku-4-5-20251001",
        "claude-opus-4-8",
    }
)

KNOWN_TOOLS: frozenset[str] = frozenset(
    {
        "Read",
        "Write",
        "Edit",
        "MultiEdit",
        "Glob",
        "Grep",
        "Bash",
        "WebFetch",
        "WebSearch",
        "Task",
        "TodoRead",
        "TodoWrite",
    }
)

WRITE_TOOLS: frozenset[str] = frozenset({"Edit", "Write", "MultiEdit"})

KEYWORD_ONLY_SKILLS: frozenset[str] = frozenset({"blog-post", "review", "infografik"})


def _strip_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    fm: dict[str, Any] = yaml.safe_load(parts[1]) or {}
    return fm, parts[2].strip()


def _agent_files() -> list[Path]:
    return sorted(AGENTS_DIR.glob("*.md"))


def _skill_dirs() -> list[Path]:
    return sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir())


def _command_files() -> list[Path]:
    return sorted(COMMANDS_DIR.glob("*.md"))


# ---------------------------------------------------------------------------
# Agent structural tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("agent_file", _agent_files(), ids=lambda p: p.stem)
def test_agent_frontmatter_parses(agent_file: Path) -> None:
    content = agent_file.read_text()
    assert content.startswith("---"), (
        f"{agent_file.name}: must start with YAML frontmatter"
    )
    fm, _ = _strip_frontmatter(content)
    assert isinstance(fm, dict), (
        f"{agent_file.name}: frontmatter must be a YAML mapping"
    )


@pytest.mark.parametrize("agent_file", _agent_files(), ids=lambda p: p.stem)
def test_agent_required_fields(agent_file: Path) -> None:
    fm, _ = _strip_frontmatter(agent_file.read_text())
    for field in ("name", "description", "tools"):
        assert field in fm, f"{agent_file.name}: missing required field '{field}'"
    assert fm["description"], f"{agent_file.name}: 'description' must be non-empty"


@pytest.mark.parametrize("agent_file", _agent_files(), ids=lambda p: p.stem)
def test_agent_model_is_known(agent_file: Path) -> None:
    fm, _ = _strip_frontmatter(agent_file.read_text())
    model = fm.get("model")
    if model is None:
        return
    assert model in KNOWN_MODELS, (
        f"{agent_file.name}: model '{model}' is not a known Claude model ID. "
        f"Known: {sorted(KNOWN_MODELS)}"
    )


@pytest.mark.parametrize("agent_file", _agent_files(), ids=lambda p: p.stem)
def test_agent_tools_are_known(agent_file: Path) -> None:
    fm, _ = _strip_frontmatter(agent_file.read_text())
    tools: list[str] = fm.get("tools", [])
    unknown = [t for t in tools if t not in KNOWN_TOOLS]
    assert not unknown, (
        f"{agent_file.name}: unknown tools {unknown}. Known: {sorted(KNOWN_TOOLS)}"
    )


@pytest.mark.parametrize("agent_file", _agent_files(), ids=lambda p: p.stem)
def test_agent_write_targets_documented(agent_file: Path) -> None:
    fm, body = _strip_frontmatter(agent_file.read_text())
    tools: list[str] = fm.get("tools", [])
    is_write_capable = any(t in WRITE_TOOLS for t in tools)
    if not is_write_capable:
        return
    body_lower = body.lower()
    has_constraint = "write_targets" in fm or (
        "write" in body_lower
        and any(kw in body_lower for kw in ("target", "allowed", "forbidden"))
    )
    assert has_constraint, (
        f"{agent_file.name}: write-capable agent must document write targets "
        "(add 'write_targets:' to frontmatter or an 'Allowed write targets' section in the body)"
    )


@pytest.mark.parametrize("agent_file", _agent_files(), ids=lambda p: p.stem)
def test_readonly_agent_has_no_write_tools(agent_file: Path) -> None:
    fm, _ = _strip_frontmatter(agent_file.read_text())
    tools: list[str] = fm.get("tools", [])
    is_write_capable = any(t in WRITE_TOOLS for t in tools)
    if is_write_capable:
        return
    # Read-only agent: body should assert read-only constraint
    _, body = _strip_frontmatter(agent_file.read_text())
    body_lower = body.lower()
    assert "read-only" in body_lower or "never edit" in body_lower, (
        f"{agent_file.name}: non-write agent should state its read-only constraint in the body"
    )


# ---------------------------------------------------------------------------
# Skill structural tests
# ---------------------------------------------------------------------------


def _load_skill_paths(skill_dir: Path) -> list[str] | None:
    """Return glob patterns for a skill, or None if keyword-only (no paths)."""
    content = (skill_dir / "SKILL.md").read_text()
    fm, body = _strip_frontmatter(content)
    if "paths" in fm:
        return [str(p) for p in fm["paths"]]
    for line in body.splitlines()[:10]:
        m = re.search(r"\*\*Trigger paths\*\*:\s*(.+)", line)
        if m:
            return re.findall(r"`([^`]+)`", m.group(1))
    return None


@pytest.mark.parametrize("skill_dir", _skill_dirs(), ids=lambda d: d.name)
def test_skill_frontmatter_or_header_present(skill_dir: Path) -> None:
    content = (skill_dir / "SKILL.md").read_text()
    fm, body = _strip_frontmatter(content)
    has_yaml_trigger = "paths" in fm or "trigger" in fm
    has_markdown_trigger = bool(re.search(r"\*\*Trigger (paths|keywords)\*\*", body))
    assert has_yaml_trigger or has_markdown_trigger, (
        f"{skill_dir.name}/SKILL.md: must have a 'paths:'/'trigger:' frontmatter field "
        "or a '**Trigger paths**:'/'**Trigger keywords**:' heading"
    )


@pytest.mark.parametrize("skill_dir", _skill_dirs(), ids=lambda d: d.name)
def test_skill_paths_are_valid_globs(skill_dir: Path) -> None:
    if skill_dir.name in KEYWORD_ONLY_SKILLS:
        return
    paths = _load_skill_paths(skill_dir)
    if paths is None:
        return
    for glob in paths:
        try:
            re.compile(fnmatch.translate(glob))
        except re.error as exc:
            pytest.fail(f"{skill_dir.name}: invalid glob pattern '{glob}': {exc}")


@pytest.mark.parametrize("skill_dir", _skill_dirs(), ids=lambda d: d.name)
def test_keyword_only_skills_have_no_paths(skill_dir: Path) -> None:
    if skill_dir.name not in KEYWORD_ONLY_SKILLS:
        return
    paths = _load_skill_paths(skill_dir)
    assert paths is None, (
        f"{skill_dir.name}: expected keyword-only skill (no paths:), but paths were found: {paths}"
    )


# ---------------------------------------------------------------------------
# Command structural tests
# ---------------------------------------------------------------------------


def _known_agent_names() -> set[str]:
    return {p.stem for p in AGENTS_DIR.glob("*.md")}


def _known_skill_names() -> set[str]:
    return {d.name for d in SKILLS_DIR.iterdir() if d.is_dir()}


@pytest.mark.parametrize("cmd_file", _command_files(), ids=lambda p: p.stem)
def test_command_agent_references_exist(cmd_file: Path) -> None:
    content = cmd_file.read_text()
    known_agents = _known_agent_names()
    # Extract bold hyphenated-or-alphanumeric words (agent naming convention)
    bold_refs = set(re.findall(r"\*\*([a-z][a-z0-9-]+)\*\*", content))
    for ref in bold_refs:
        if "-" in ref:
            # Hyphenated bold words must be known agents (e.g. architecture-reviewer)
            assert ref in known_agents, (
                f"{cmd_file.name}: references '**{ref}**' but no agent named '{ref}' exists "
                f"in .claude/agents/. Known: {sorted(known_agents)}"
            )


@pytest.mark.parametrize("cmd_file", _command_files(), ids=lambda p: p.stem)
def test_command_skill_references_exist(cmd_file: Path) -> None:
    content = cmd_file.read_text()
    known_skills = _known_skill_names()
    # Backtick-quoted words that look like skill names (contain hyphen or match a known skill)
    backtick_refs = set(re.findall(r"`([a-z][a-z0-9-]+)`", content))
    for ref in backtick_refs:
        if ref in known_skills:
            continue
        if "-" in ref and ref not in known_skills:
            # Only fail if the ref plausibly looks like a skill name AND doesn't exist
            # (avoid false positives on things like `git diff`)
            if not any(c in ref for c in ("/", ".", "*", " ")):
                assert ref in known_skills, (
                    f"{cmd_file.name}: references '`{ref}`' but no skill named '{ref}' exists "
                    f"in .claude/skills/. Known: {sorted(known_skills)}"
                )
