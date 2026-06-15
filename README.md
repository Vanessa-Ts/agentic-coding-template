# agentic-coding-template

Template for a containered FastAPI service with Claude Code support: typed agents, auto-trigger skills, inline push gate, and a Spec→Plan→Implement→Review→Ship loop.


---

## Features

- **FastAPI 0.136 + Pydantic v2** — fully preconfigured with async route handlers, strict type annotations, dependency injection via `Depends()`, and response models on every endpoint
- **BCE Architecture (Boundary / Control / Entity)** — enforced by parallel reviewer agents (`architecture-reviewer`, `performance-reviewer`, `security-reviewer`) that run on every `/review` call
- **Automated quality gate** — `ruff format`, `ruff check`, `mypy --strict`, and `pytest` must all pass before any `git push`; enforced inline by the `pre_push_quality_gate` hook
- **Docker-based dev environment** — `docker compose up --build` brings up the full dev container; no local Python setup required
- **Guard-rail hook suite** — blocks secrets in `.env`, dangerous Bash patterns (`rm -rf`, force-push), `pip` in favour of `uv`, and auto-formats Python after every edit
- **Spec→Plan→Implement→Review→Ship loop** — structured agentic workflow from fuzzy requirement to merged PR, all driven from the Claude Code chat; no external project-management tool needed
- **`docs/plans/` as the single source of truth** — every feature starts as a plan file that the `planner` agent writes and the `implementer` agent reads; the plan is referenced in the PR body and versioned alongside the code

---

## Agents

| Agent | Model | Write targets | Purpose |
|---|---|---|---|
| `planner` | Sonnet 4.6 | `docs/plans/` | Reads codebase, writes implementation plan |
| `implementer` | Sonnet 4.6 | `src/`, `tests/` | Turns plan into working code + tests |
| `architecture-reviewer` | Haiku 4.5 | none (read-only) |
| `performance-reviewer` | Haiku 4.5 | none (read-only) |
| `security-reviewer` | Haiku 4.5 | none (read-only) | Secrets, OWASP-lite, input validation |


---

## Skills

Skills extend Claude Code with domain-specific context — path-triggered ones load automatically when you open a matching file; manual ones are invoked on demand.

| Skill | `paths:` trigger | Purpose |
|---|---|---|
| `fastapi-conventions` | `src/app/routes/**`, `src/app/models/**`, `src/app/main.py` | Route/DI/response-model conventions |
| `pytest-patterns` | `tests/**`, `**/conftest.py` | AsyncClient fixtures, parametrize patterns |
| `uv-workflows` | `pyproject.toml`, `uv.lock` | `uv add`, `uv sync`, `uv run` idioms |
| `infrastructure` | `Dockerfile`, `docker-compose*`, CI workflows | Container, compose, and CI pipeline patterns |
| `openapi` | `openapi*.yml`, `openapi*.json` | Spec authoring and codegen |
| `frontend` | `*.html`, `ui/**` | Jinja2, Tailwind, HTMX patterns |
| `spec-feature` | manual | 2-phase interview → `docs/specs/<feature>/` before planning |
| `review` | manual | Inline BCE + FastAPI + Python checklist for ad-hoc review |
| `doc` | manual | Reads source → writes project docs into `docs/` |
| `blog-post` | manual | Audience interview → structured technical blog post |
| `infografik` | manual | AI image generation via Hugging Face FLUX.1 → `docs/assets/` |


---

### Agentic loop

```
spec → plan → implement → review → ship
```

| Step | How to trigger | Output |
|---|---|---|
| **Spec** | Describe the feature in plain English — `spec-feature` skill auto-triggers | `docs/specs/<feature>.md` |
| **Plan** | `/plan <feature>` | `docs/plans/<feature>.md` |
| **Implement** | `/implement` | `feat/<name>` branch with code + tests |
| **Review** | `/review` | Violations or LGTM from parallel reviewer agents |
| **Ship** | `/ship` | Quality gate + PR |

Skip the spec step for well-understood changes (bug fixes, small additive work). Use it when requirements are fuzzy or need alignment before any code is written — the skill runs a structured 6-question interview and records what was agreed.


---

## Quick Start

```bash
git clone <repository-url>         # clone the repo
docker compose up --build          # start dev container
cp .env.template .env              # configure environment
```

This template uses Claude Code subscription per default. For API connection add the ANTHROPIC_API_KEY to the .env`.



---

## Hook Table

| Hook | Event | What it blocks |
|---|---|---|
| `block_secrets_and_env.py` | PreToolUse Edit\|Write\|MultiEdit | Writes to `.env`; AWS/GH/Anthropic key patterns |
| `block_bash_dangers.py` | PreToolUse Bash | `rm -rf`, force-push, `--hard` reset, commit on main |
| `enforce_uv.py` | PreToolUse Bash | `pip install`, `pip3`, `python -m pip`, `poetry add` |
| `autoformat_python.py` | PostToolUse Edit\|Write\|MultiEdit | Stale formatting; runs `ruff format` + `ruff check --fix` |
| `pre_push_quality_gate.py` | PreToolUse Bash | `git push` unless ruff + mypy + pytest all pass inline |

See [.claude/hooks/README.md](.claude/hooks/README.md) for exit codes and how to add a hook.


---

## Stack

| Tool | Version | Purpose |
|---|---|---|
| FastAPI | 0.136 | Async API framework |
| Pydantic v2 | 2.x | Typed models, settings |
| uv | latest | Dependency management |
| pytest-asyncio | latest | Async test runner |
| ruff | latest | Formatter + linter |
| mypy | latest | Strict static typing |
| httpx | latest | Async test client |


---

## Further Reading

- [WALKTHROUGH.md](WALKTHROUGH.md) — step-by-step session log with real hook blocks and a broken push
- [docs/AGENTIC_WORKFLOW.md](docs/AGENTIC_WORKFLOW.md) — loop diagram, hook semantics, escalation policy
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) — decode every `Blocked:` message
- [docs/PROMPTS.md](docs/PROMPTS.md) — 10 paste-ready plan-mode prompts
- [docs/inventory.md](docs/inventory.md) — artifact source/license table
- [CLAUDE.md](CLAUDE.md) — coding standards and conventions
