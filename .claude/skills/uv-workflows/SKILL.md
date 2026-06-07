---
paths:
  - "pyproject.toml"
  - "uv.lock"
trigger: "Use whenever adding/removing/upgrading a dependency, syncing the environment, running Python scripts, or when pip/poetry/venv are mentioned."
---

# uv Workflows

## Adding dependencies

```bash
uv add <pkg>          # runtime dependency
uv add --dev <pkg>    # dev/test-only dependency
```

## Syncing the environment

```bash
uv sync               # install all deps from uv.lock
```

## Running commands

```bash
uv run pytest         # run tests
uv run mypy src/      # type check
uv run ruff check .   # lint
uv run python script.py
```

## Upgrading a specific package

```bash
uv lock --upgrade-package <pkg>
uv sync
```

## Rules

- **Never** edit `uv.lock` by hand.
- **Never** use `pip install`, `pip3 install`, `python -m pip`, or `poetry add`.
- Do not create or activate virtualenvs manually — uv manages `.venv` automatically.
- Commit both `pyproject.toml` and `uv.lock` when adding or upgrading a dependency.
