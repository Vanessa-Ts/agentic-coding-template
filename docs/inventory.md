# `.claude/` Artifact Inventory

Generated 2026-06-05 during Phase 3; updated 2026-06-07 with agent/skill overhaul. Every `.claude/` file has exactly one row.
Re-run this scan before creating any new artifact (CLAUDE.md reuse-first policy).

External reference sources checked:
- `/mnt/skills/public/` — not mounted
- `/mnt/skills/user/` — not mounted
- `shanraisshan/claude-code-best-practice` — patterns reviewed; no direct copies
- `mgoericke/claude-skills-devcontainer` — patterns reviewed; no direct copies

---

## Skills

| artifact | source | license | reuse-as-is | wrap | rebuild | rationale |
|---|---|---|---|---|---|---|
| `skills/fastapi-conventions/SKILL.md` | project-internal | proprietary | ✓ for any FastAPI+Pydantic v2 project | — | — | Encodes async-first routes, `Depends()`, `.model_dump()`, `@app.exception_handler` patterns. No project-specific coupling; portable as-is to any FastAPI service. |
| `skills/pytest-patterns/SKILL.md` | project-internal | proprietary | ✓ for any httpx+pytest-asyncio project | — | — | Bans `TestClient`, enforces `AsyncClient+ASGITransport`, documents fixture baseline and 3-test minimum. No project-specific logic; portable as-is. |
| `skills/uv-workflows/SKILL.md` | project-internal | proprietary | ✓ for any uv-managed Python project | — | — | Documents `uv add`, `uv sync`, `uv run` idioms and bans `pip`/`poetry`. Fully generic; reuse verbatim in any Python project using uv. |
| `skills/infrastructure/SKILL.md` | project-internal | proprietary | ✓ for any Python+uv project with Docker/CI | — | — | Multi-stage Dockerfile, docker-compose healthchecks, GitHub Actions with `astral-sh/setup-uv`, Helm chart structure. Stack-agnostic patterns; swap `pytest` for your test runner. |
| `skills/spec-feature/SKILL.md` | project-internal | proprietary | — | — | ✓ | Rebuilt: 2-phase 8-question interview (requirements + design) with approval gate; produces 3 files under `docs/specs/<feature>/` (`requirements.md`, `design.md`, `tasks.md`). EARS notation embedded. |
| `skills/openapi/SKILL.md` | project-internal | proprietary | ✓ for any FastAPI/Python project | — | — | OpenAPI 3.x YAML structure, `datamodel-codegen` and `fastapi-codegen` usage, spec export from running FastAPI app. |
| `skills/review/SKILL.md` | project-internal | proprietary | — | ✓ | — | Inline BCE + FastAPI + Python checklist. Wrap: replace FastAPI-specific items for non-FastAPI stacks. |
| `skills/doc/SKILL.md` | project-internal | proprietary | — | ✓ | — | Doc-generation workflow reading `main.py`, routes, models, config. Wrap: adjust source paths for non-FastAPI layouts. |
| `skills/blog-post/SKILL.md` | project-internal | proprietary | ✓ | — | — | 5-question audience interview + post structure template. Fully generic content skill; stack-agnostic. |
| `skills/frontend/SKILL.md` | project-internal | proprietary | ✓ for FastAPI+Jinja2 projects | — | — | Jinja2 templates, Tailwind CSS (CDN + CLI), HTMX partial updates, TailAdmin layout patterns. Wrap for non-Jinja2 templating. |
| `skills/infografik/SKILL.md` | project-internal | proprietary | ✓ for any Python project with `httpx` | — | — | Hugging Face Inference API + FLUX.1-dev for AI image generation. Requires `HF_TOKEN`; output to `docs/assets/`. |

---

## Agents

| artifact | source | license | reuse-as-is | wrap | rebuild | rationale |
|---|---|---|---|---|---|---|
| `agents/planner.md` | project-internal | proprietary | — | ✓ | — | Output schema (scope/endpoints/models/store/test-plan/open-questions) is generic for any REST resource. Wrap: strip FastAPI-specific mentions for non-FastAPI projects. Model: `claude-sonnet-4-6`. |
| `agents/implementer.md` | project-internal | proprietary | — | ✓ | — | Write targets and forbidden zones (`pyproject.toml`, `.github/`, `.claude/`) are project-specific. Wrap: update allowed/forbidden paths per project layout. Model: `claude-sonnet-4-6`. |
| `agents/ai-service-generator.md` | project-internal | proprietary | — | ✓ | — | Anthropic SDK patterns (AsyncAnthropic, streaming, tool use, prompt management, error handling). Wrap: swap SDK for a different LLM provider. Model: `claude-sonnet-4-6`. |
| `agents/architecture-reviewer.md` | project-internal | proprietary | — | ✓ | — | BCE layer compliance for FastAPI (routes/services/store/models). Wrap: adjust layer names and import patterns for non-FastAPI projects. Model: `claude-haiku-4-5-20251001`. |
| `agents/performance-reviewer.md` | project-internal | proprietary | ✓ for any async Python project | — | — | Blocking I/O, missing await, N+1, unbounded lists, unclosed resources, over-serialization. Mostly framework-agnostic; reuse as-is for any async Python service. Model: `claude-haiku-4-5-20251001`. |
| `agents/security-reviewer.md` | project-internal | proprietary | — | ✓ | — | OWASP-lite checks and hook-safety checks are mostly framework-agnostic. Wrap: add framework-specific checks (e.g. Django CSRF) as needed. Model: `claude-haiku-4-5-20251001`. |

---

## Commands

| artifact | source | license | reuse-as-is | wrap | rebuild | rationale |
|---|---|---|---|---|---|---|
| `commands/plan.md` | project-internal | proprietary | ✓ | — | — | Delegates to planner agent with `$ARGUMENTS`; no hardcoded project details. Reuse as-is in any project that adopts the planner agent. |
| `commands/implement.md` | project-internal | proprietary | ✓ | — | — | Reads latest plan via `ls -t docs/plans/*.md`; creates `feat/<name>` branch; no hardcoded paths. Fully generic for any repo following the same plan-then-implement workflow. |
| `commands/review.md` | project-internal | proprietary | — | ✓ | — | Runs architecture-reviewer, performance-reviewer, and security-reviewer in parallel; 2-iteration self-correction loop. Wrap: adjust agent names if reviewers change. |
| `commands/ship.md` | project-internal | proprietary | — | ✓ | — | Quality gate commands (`ruff`, `mypy --strict src/`, `pytest -x`) and `gh pr create` template are semi-portable. Wrap: adjust tool invocations for different stacks (e.g. replace `mypy` with `pyright`). |

---

## Hooks

| artifact | source | license | reuse-as-is | wrap | rebuild | rationale |
|---|---|---|---|---|---|---|
| `hooks/autoformat_python.py` | project-internal | proprietary | ✓ for any ruff-using project | — | — | PostToolUse Edit/Write/MultiEdit. Runs `ruff format` + `ruff check --fix` on every changed `.py` file. Pure stdlib + ruff; no project coupling. |
| `hooks/block_bash_dangers.py` | project-internal | proprietary | ✓ | — | — | PreToolUse Bash. Blocks `rm -rf`, force-push, `git reset --hard`, push-to-main, and `git commit` on `main`. All rules are project-agnostic safety guards. |
| `hooks/block_secrets_and_env.py` | project-internal | proprietary | ✓ | — | — | PreToolUse Edit/Write/MultiEdit. Blocks writes to `.env` and matches AWS/GitHub/Anthropic/OpenAI key patterns. Extend the `SECRET_PATTERNS` list for additional providers. |
| `hooks/enforce_uv.py` | project-internal | proprietary | ✓ for any uv project | — | — | PreToolUse Bash. Blocks `pip install`, `pip3 install`, `python -m pip`, `poetry add`. Reuse verbatim in any project that mandates uv. |
| `hooks/pre_push_quality_gate.py` | project-internal | proprietary | — | ✓ | — | PreToolUse Bash matching `git push`. Runs ruff/mypy/pytest inline; exits 2 on failure. Wrap: swap tool list for non-Python stacks (e.g. `tsc`, `eslint`, `vitest`). |

---

## Configuration

| artifact | source | license | reuse-as-is | wrap | rebuild | rationale |
|---|---|---|---|---|---|---|
| `settings.json` | project-internal | proprietary | — | ✓ | — | Wires all five hooks, sets `model`, env overrides, permission allow/deny/ask lists, and `plansDirectory`. Wrap: adopt hook wiring and permission structure; replace model and env vars per project. |
| `settings.local.json` | project-internal | proprietary | — | — | ✓ | Contains machine-local directory permissions for devcontainer setup. Rebuild per environment; do not commit to shared repos without scrubbing paths. |

---

## Hook README

| artifact | source | license | reuse-as-is | wrap | rebuild | rationale |
|---|---|---|---|---|---|---|
| `hooks/README.md` | project-internal | proprietary | — | ✓ | — | Documents hook event types, exit-code semantics, and per-hook purpose. Wrap: update table rows when hooks are added or removed. |
