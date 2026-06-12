"""Phase 2 — behavioral evals (LLM-graded, pass@k=3).

LOCAL-ONLY. Never runs in CI.
Run manually: pytest evals/test_behavioral.py -v -m behavioral

Requires:
  - claude CLI in PATH (`which claude`)
  - Active Claude subscription (no API key needed)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from evals.conftest import FIXTURES_DIR, passes_at_k, run_agent

pytestmark = pytest.mark.behavioral

AGENTS_DIR = Path(__file__).parent.parent / ".claude" / "agents"


# ---------------------------------------------------------------------------
# (a) Reviewer scenario — code-based grading
# ---------------------------------------------------------------------------

REVIEWER_AGENTS = ["architecture-reviewer", "performance-reviewer", "security-reviewer"]


@pytest.mark.parametrize("agent_name", REVIEWER_AGENTS)
def test_reviewer_flags_testclient_and_bare_except(agent_name: str) -> None:
    """Each reviewer must flag TestClient usage and bare except in a known-bad diff."""
    bad_diff = (FIXTURES_DIR / "bad_diff.patch").read_text()
    prompt = f"Review this diff and identify any violations:\n\n{bad_diff}"

    outputs = run_agent(agent_name, prompt, k=3)

    def check(output: str) -> bool:
        lower = output.lower()
        return "testclient" in lower and "except" in lower

    assert passes_at_k(outputs, check, min_pass=2), (
        f"Agent '{agent_name}' failed to flag both 'TestClient' and 'except' in ≥2/3 runs.\n"
        f"Outputs:\n" + "\n---\n".join(outputs[:3])
    )


# ---------------------------------------------------------------------------
# (b) Planner scenario — structural grading
# ---------------------------------------------------------------------------

REQUIRED_PLAN_SECTIONS = ["## Scope", "## Endpoints", "## Test plan"]


def test_planner_produces_required_sections() -> None:
    """Planner must produce a plan with required structural sections."""
    feature_desc = (FIXTURES_DIR / "short_feature.txt").read_text().strip()

    outputs = run_agent("planner", feature_desc, k=3)

    def check(output: str) -> bool:
        return all(section in output for section in REQUIRED_PLAN_SECTIONS) and (
            "src/" in output or "tests/" in output
        )

    assert passes_at_k(outputs, check, min_pass=2), (
        f"Planner failed to produce required sections {REQUIRED_PLAN_SECTIONS} in ≥2/3 runs.\n"
        f"Outputs:\n" + "\n---\n".join(outputs[:3])
    )


# ---------------------------------------------------------------------------
# (c) Implementer scenario — output-text grading (local-only, no file writes)
# ---------------------------------------------------------------------------

IMPLEMENTER_EXPECTED_PATTERNS = [
    "async def",
    "response_model",
    "status_code",
    "AsyncClient",
]


def test_implementer_output_follows_conventions() -> None:
    """Implementer output must reference FastAPI async conventions from the plan."""
    plan = (FIXTURES_DIR / "minimal_plan.md").read_text()
    prompt = (
        "Read the following plan and describe (do not implement yet) the code you would write, "
        "including the specific FastAPI patterns and test patterns you would use:\n\n"
        + plan
    )

    outputs = run_agent("implementer", prompt, k=3)

    def check(output: str) -> bool:
        return all(pattern in output for pattern in IMPLEMENTER_EXPECTED_PATTERNS)

    assert passes_at_k(outputs, check, min_pass=2), (
        f"Implementer failed to reference required conventions in ≥2/3 runs.\n"
        f"Expected patterns: {IMPLEMENTER_EXPECTED_PATTERNS}\n"
        f"Outputs:\n" + "\n---\n".join(outputs[:3])
    )
