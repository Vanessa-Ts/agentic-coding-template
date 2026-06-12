# Infrastructure Skill

**Trigger paths**: `Dockerfile`, `docker-compose*.yml`, `.github/workflows/*.yml`, `helm/**`, `k8s/**`
**Trigger keywords**: Dockerfile, docker-compose, CI/CD, GitHub Actions, Helm chart, Kubernetes, container, pipeline, deploy

---

## Dockerfile — Python best practices

Always use multi-stage builds to keep the final image small:

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.11-slim AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev

FROM python:3.11-slim AS runtime
WORKDIR /app
# Non-root user — never run as root in production
RUN addgroup --system app && adduser --system --group app
COPY --from=builder /app/.venv ./.venv
COPY src/ ./src/
USER app
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Rules:
- Always add a `.dockerignore` (exclude `.venv/`, `__pycache__/`, `.env`, `tests/`, `docs/`)
- Pin the Python base image version — never use `:latest`
- `COPY` only what the layer needs — keep `pyproject.toml`/`uv.lock` in an earlier layer to maximise cache hits
- Set `ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1` in the runtime stage

---

## docker-compose — local dev

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/live"]
      interval: 10s
      timeout: 5s
      retries: 3
    volumes:
      - ./src:/app/src   # hot-reload in dev only; remove in prod compose
```

Rules:
- Always add a `healthcheck` for each service
- Use `env_file: .env` — never inline secrets in `docker-compose.yml`
- Use named volumes for databases; anonymous volumes only for caches

---

## GitHub Actions — Python CI pipeline

```yaml
name: CI
on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - uses: astral-sh/setup-uv@v4          # official uv action
        with:
          enable-cache: true                  # caches .venv across runs
      - run: uv sync --frozen
      - run: ruff format --check .
      - run: ruff check .
      - run: mypy --strict src/
      - run: pytest -x --cov=app
```

Rules:
- Use `astral-sh/setup-uv` (not `pip install uv`) for proper caching
- `uv sync --frozen` — never `uv sync` without `--frozen` in CI (prevents surprise upgrades)
- Run format check before lint — format violations surface faster
- Cache key should include `uv.lock` hash for reliable invalidation

---

## Helm chart structure (Python service)

```
helm/
  Chart.yaml
  values.yaml
  templates/
    deployment.yaml    # image, env from secrets, readiness probe
    service.yaml       # ClusterIP → Ingress
    configmap.yaml     # non-secret config
    secret.yaml        # sealed-secrets or external-secrets operator ref
    hpa.yaml           # HorizontalPodAutoscaler
    ingress.yaml
```

Rules:
- Never hardcode secrets in `values.yaml` — use External Secrets or Sealed Secrets
- Set `readinessProbe` and `livenessProbe` to the FastAPI `/health/ready` and `/health/live` endpoints
- Set `resources.requests` and `resources.limits` — never leave them unset in production charts
- Use `{{ .Values.image.tag | default .Chart.AppVersion }}` as the image tag default
