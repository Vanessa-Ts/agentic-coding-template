# Doc Skill

**Trigger paths**: `docs/**/*.md`
**Trigger keywords**: document, write docs, generate docs, README, API reference, add documentation

---

## Purpose

Read source code and configuration; write accurate project documentation into `docs/`. Never invent behaviour that isn't in the code.

---

## Workflow

1. Read `src/app/main.py` — understand routes mounted, lifespan, middleware.
2. Read `src/app/routes/*.py` — collect all endpoints (method, path, request/response models, status codes).
3. Read `src/app/models/*.py` — collect field names, types, validators.
4. Read `src/app/core/config.py` — collect all settings and their env var names.
5. Read `pyproject.toml` — collect Python version, runtime dependencies.
6. Read `Dockerfile` / `docker-compose.yml` if present — collect port, volume, env requirements.
7. Write to `docs/` only — never modify `src/`.

---

## Standard doc sections

### Project overview (`docs/README.md` or root `README.md`)
```markdown
# <Project name>

One-paragraph description: what it does, who uses it, key technology choices.

## Quick start
Steps to run locally (clone → configure env → start).

## Architecture
ASCII diagram of layers (routes → store → models) and external dependencies.
```

### API reference (`docs/api.md`)
Auto-generate from the running app or from source:
```bash
python3 -c "
import json, sys
sys.path.insert(0, 'src')
from app.main import app
schema = app.openapi()
for path, methods in schema['paths'].items():
    for method, op in methods.items():
        print(f'{method.upper()} {path} — {op.get(\"summary\",\"\")}')
"
```

Format each endpoint as:
```markdown
### POST /items
**Request body**: `ItemCreate` — `name: str`, `description: str | None`
**Response** `201`: `Item`
**Response** `422`: validation error
```

### Environment variables (`docs/configuration.md`)
For each field in `Settings`:
```markdown
| Variable | Default | Required | Description |
|---|---|---|---|
| `APP_NAME` | `my-service` | No | Application display name |
| `ANTHROPIC_API_KEY` | — | Yes | Anthropic API key for Claude calls |
```

### Architecture diagram (ASCII)
```
┌──────────────┐     HTTP      ┌─────────────┐
│   Client     │ ───────────▶  │  FastAPI    │
└──────────────┘               │  routes/    │
                               └──────┬──────┘
                                      │ Depends()
                               ┌──────▼──────┐
                               │   store/    │
                               └──────┬──────┘
                                      │
                               ┌──────▼──────┐
                               │   models/   │
                               └─────────────┘
```

---

## Rules

- Only document behaviour that exists in the source code — never speculate.
- If a setting has no default, mark it as **Required**.
- Keep code examples runnable — test them before writing.
- Update existing docs rather than creating duplicates.
- After writing, tell the user which files were created/updated and suggest running `/review` if code was touched.
