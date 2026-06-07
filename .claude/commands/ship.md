Run the full quality gate. All four checks must pass.

```bash
ruff format --check .
ruff check .
mypy --strict src/
pytest -x
```

Run each command in sequence. If any command fails:
- Print the full output of the failing command
- Stop and report what needs fixing

If all four pass, remind the user to update the version before opening the PR:

```
Current version in pyproject.toml: <output of: grep '^version' pyproject.toml>
Bump it there before merging if this release warrants a version change (patch · minor · major).
config.py reads the version from pyproject.toml automatically — no separate update needed.
Proceed to create the PR? (y/n)
```

Wait for confirmation before continuing. If the user says no, stop so they can bump the version first.

If confirmed, open a pull request:

```bash
gh pr create --title "<current-branch>" --body "$(cat <<'EOF'
## Summary
<bullet points from the plan or commit log>

## Test plan
- [ ] All tests pass (`pytest -x`)
- [ ] Type-checked (`mypy --strict src/`)
- [ ] Lint clean (`ruff check .`)

Generated with [Claude Code](https://claude.ai/code)
EOF
)"
```

Use `git branch --show-current` to get the branch name. Reference the plan file from `docs/plans/` in the summary if one exists for this feature.

Do NOT write any state file.
