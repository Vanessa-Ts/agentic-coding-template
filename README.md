# agentic-coding-template

A FastAPI service demonstrating senior-grade Claude Code patterns: typed agents, auto-trigger skills, inline push gate, and a full Research→Plan→Execute→Review→Ship loop.

---

## Quick Start

```bash
docker compose up --build          # start dev container
cp .env.template .env              # configure environment
uv run uvicorn app.main:app --reload --app-dir src
```

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

## Agent Map

| Agent | Model | Write targets | Purpose |
|---|---|---|---|
| `planner` | Sonnet 4.6 | `docs/plans/` | Reads codebase, writes implementation plan |
| `implementer` | Sonnet 4.6 | `src/`, `tests/` | Turns plan into working code + tests |
| `architecture-reviewer` | Haiku 4.5 | none (read-only) |  |
| `performance-reviewer` | Haiku 4.5 | none (read-only) |  |
| `security-reviewer` | Haiku 4.5 | none (read-only) | Secrets, OWASP-lite, input validation |

---

## Skill Roster

| Skill | `paths:` trigger | Purpose |
|---|---|---|
| `fastapi-conventions` | `src/app/routes/**`, `src/app/models/**`, `src/app/main.py` | Route/DI/response-model conventions |
| `pytest-patterns` | `tests/**`, `**/conftest.py` | AsyncClient fixtures, parametrize patterns |
| `uv-workflows` | `pyproject.toml`, `uv.lock` | `uv add`, `uv sync`, `uv run` idioms |

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

## Command Map

| Command | What it does |
|---|---|
| `/plan <feature>` | Invokes `planner` → writes `docs/plans/<feature>.md` |
| `/implement` | Reads latest plan, creates `feat/<name>` branch, builds code |
| `/review` | Invokes `architecture-reviewer`, `architecture-reviewer` and `security-reviewer` in parallel |
| `/ship` | Runs quality gate, then `gh pr create` |

---

## Demo Feature: `/items` CRUD

Five in-memory endpoints proving the full loop works end-to-end:

```
POST   /items           → 201  create item
GET    /items           → 200  list all
GET    /items/{id}      → 200  get by id
PUT    /items/{id}      → 200  update
DELETE /items/{id}      → 204  delete
```

Run the 15 tests: `uv run pytest tests/test_items.py -v`

---

## Further Reading

- [WALKTHROUGH.md](WALKTHROUGH.md) — step-by-step session log with real hook blocks and a broken push
- [docs/AGENTIC_WORKFLOW.md](docs/AGENTIC_WORKFLOW.md) — loop diagram, hook semantics, escalation policy
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) — decode every `Blocked:` message
- [docs/PROMPTS.md](docs/PROMPTS.md) — 10 paste-ready plan-mode prompts
- [docs/inventory.md](docs/inventory.md) — artifact source/license table
- [CLAUDE.md](CLAUDE.md) — coding standards and conventions
