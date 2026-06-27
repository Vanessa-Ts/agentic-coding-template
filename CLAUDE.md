# CLAUDE.md

## Project

`agentic-coding-template` — FastAPI service with Claude Code patterns.
Stack: FastAPI 0.136, Pydantic v2, uv, pytest-asyncio, ruff, mypy --strict, Python 3.11+.

---

## Code style

- All route handlers **must** be `async def`.
- Every function must have full type annotations — no implicit `Any`.
- Return type on every route decorator: `response_model=` and `status_code=`.
- Pydantic v2 only: `.model_dump()` / `.model_validate()` — never `.dict()` / `.from_orm()`.
- Use `Depends()` for every injectable collaborator. Never instantiate in route handlers.
- Map exceptions to HTTP via `@app.exception_handler`. Never bare `except`.
- One resource = one router module mounted in `main.py` via `app.include_router()`.

---

## Test conventions

- **`TestClient` is forbidden.** Always use `httpx.AsyncClient` + `ASGITransport`.
- Every new route requires 3 tests minimum: happy path · validation failure (422) · not-found (404).
- Use `@pytest_asyncio.fixture` for async fixtures — not `@pytest.fixture`.
- Use `pytest.mark.parametrize` over loops.
- `asyncio_mode = "auto"` is set in `pyproject.toml` — no manual event loop management.

Fixture baseline (`tests/conftest.py`):
```python
@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
```

---

## Branch rules

- **Never commit directly on `main`.** Feature branches only: `feat/<name>`.
- Each logical unit is a separate commit (models, store, routes, tests = 4 commits minimum).
- PR title ≤70 chars. Body must reference the plan file from `docs/plans/`.

---

## Git commit style

- Use `git commit -m "<message>"` with a plain, descriptive one-line message. No HEREDOC.
- **Never** append attribution lines to commit messages.

---

## Forbidden patterns

| Pattern | Replacement |
|---|---|
| `from starlette.testclient import TestClient` | `httpx.AsyncClient + ASGITransport` |
| `pip install` / `pip3` / `poetry add` | `uv add <pkg>` |
| `import os; os.environ[...]` mutate | `monkeypatch.setenv(...)` in tests |
| `@app.on_event(...)` | `@asynccontextmanager` lifespan |
| bare `except:` | catch a named exception type |
| write to `.env` directly | edit `.env.template`, use pydantic-settings |

---

## Dependency management

Always use `uv`. Never touch `uv.lock` by hand. Commit both `pyproject.toml` and `uv.lock`.

```bash
uv add <pkg>           # runtime dep
uv add --dev <pkg>     # dev/test dep
```

Run tools **directly** — do not prefix with `uv run`:
```bash
pytest -x
mypy --strict src/
ruff check .
ruff format --check .
```

---

## Quality gate

All four must pass before pushing:
```bash
ruff format --check .
ruff check .
mypy --strict src/
pytest -x
```
The `pre_push_quality_gate` hook enforces this inline on every `git push`.

---

## Token-saving strategies

Quality is the priority; cost is managed through these strategies, not by downgrading models.

| Strategy | Mechanism | Scope |
|---|---|---|
| Model tiering | Opus for reasoning-heavy agents (planner, ai-service-generator, reviewers); Sonnet for implementer | Per-agent `model` field |
| Effort tuning | `xhigh` for planner, `high` for reviewers and ai-service-generator, default for implementer | Per-agent `effort` field |
| Autocompact | Context window compacted at 80% capacity | `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=80` in settings.json |
| Tool restrictions | Reviewers limited to Read, Glob, Grep, restricted Bash | Agent `tools` field |
| Bash whitelisting | Reviewers restricted to `git diff/log` and `rg` only | Agent system prompts |
| Checklist-based reviews | Bounded reasoning via fixed checklists (7-8 points each) | Agent system prompts |
| Hooks | Pre/post tool validation prevents wasted token loops | settings.json `hooks` config |
| Reviewer staggering | Sequential reviewer execution prevents Opus rate-limit retry loops | `/review` command |

**Observability**: Use `/usage` to view per-agent token consumption after any session.

---

## Agent / Skill / Command map

| Artifact | Purpose |
|---|---|
| `planner` agent | Read-only; writes `docs/plans/<feature>.md` |
| `implementer` agent | Writes `src/` + `tests/` only; reads plan first |
| `ai-service-generator` agent | Specialist implementer for Anthropic SDK / LLM features |
| `architecture-reviewer` agent | Read-only; BCE layer compliance and import dependency flow |
| `performance-reviewer` agent | Read-only; N+1 queries, blocking I/O, async anti-patterns |
| `security-reviewer` agent | Read-only; secrets/input validation/OWASP-lite |
| `fastapi-conventions` skill | Auto-loads for `src/app/routes/`, `models/`, `main.py` |
| `pytest-patterns` skill | Auto-loads for `tests/`, `conftest.py` |
| `uv-workflows` skill | Auto-loads for `pyproject.toml`, `uv.lock` |
| `infrastructure` skill | Auto-loads for `Dockerfile`, `docker-compose*`, CI workflows, Helm |
| `spec-feature` skill | 2-phase interview → `docs/specs/<feature>/{requirements,design,tasks}.md` before planning |
| `openapi` skill | Auto-loads for `openapi*.yml/json`; spec authoring and codegen |
| `review` skill | Inline BCE + FastAPI + Python checklist for ad-hoc code review |
| `doc` skill | Reads source → writes project docs into `docs/` |
| `blog-post` skill | Audience interview → structured technical blog post |
| `frontend` skill | Auto-loads for `*.html`, `ui/**`; Jinja2, Tailwind, HTMX patterns |
| `infografik` skill | AI image generation via Hugging Face FLUX.1 → `docs/assets/` |
| `/plan <feature>` | Invokes planner → `docs/plans/<feature>.md` |
| `/implement` | Reads latest plan, creates `feat/<name>` branch, builds |
| `/review` | Invokes architecture + performance + security reviewers sequentially |
| `/ship` | Full quality gate + `gh pr create` |

---

## Reuse-first policy

Before building any new `.claude/` artifact, check `docs/inventory.md` for an existing source
that can be reused or wrapped. Document source + license for every artifact in that table.

---

## /compact preservation

When context is compacted, preserve: current branch name, latest plan file path, any open
violations from the last `/review` run, the phase being implemented, current agent model
assignments (planner=opus, ai-service-generator=opus, reviewers=opus, implementer=sonnet),
and cumulative token usage from the session.
