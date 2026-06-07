# Base
FROM python:3.11-slim AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV TZ=Europe/Berlin
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get full-upgrade -y && \
    apt-get install -y --no-install-recommends locales tzdata curl ca-certificates make git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen en_US.UTF-8 && \
    useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app



ENV LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH" \
    UV_PROJECT_ENVIRONMENT=/app/.venv


# Deps
# ============================================================
FROM base AS deps

COPY pyproject.toml uv.lock ./

# Stub src so uv sync doesn't complain about missing project
RUN mkdir -p src/app && \
    touch src/app/__init__.py

RUN uv venv -p /usr/local/bin/python3 /app/.venv/ && \
    uv sync --frozen --no-dev --no-install-project && \
    uv cache clean



# Build
# ============================================================
FROM base AS builder

COPY --from=deps /app/.venv /app/.venv
COPY pyproject.toml uv.lock ./
COPY src/ ./src/

# Install the project itself (source only, deps already in venv)
RUN uv sync --frozen --no-dev --no-cache


# Dev
# ============================================================
FROM base AS development

COPY --from=deps /app/.venv /app/.venv

COPY pyproject.toml uv.lock ./
COPY src/ ./src/

RUN chown -R appuser:appuser /app
USER appuser

RUN uv sync --frozen --group dev && \
    uv cache clean

RUN curl -fsSL https://claude.ai/install.sh | bash
RUN echo 'unset VIRTUAL_ENV' >> /home/appuser/.bashrc
ENV PATH="/home/appuser/.local/bin:$PATH"

CMD ["sleep", "infinity"]


# Test 
# ============================================================
FROM base AS test

COPY --from=deps /app/.venv /app/.venv
COPY pyproject.toml uv.lock ./

ENV UV_COMPILE_BYTECODE=0

COPY src/ ./src/
COPY tests/ ./tests/

RUN uv sync --frozen --no-cache --group test && \
    uv cache clean

USER appuser

CMD ["pytest", "tests/", \
     "-v", \
     "--cov=app", \
     "--cov-report=term-missing", \
     "--cov-report=xml:coverage.xml", \
     "--junitxml=report.xml"]


# Prod 
# ============================================================
FROM base AS production

COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/

USER appuser

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]