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

If all four pass, open a pull request:

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
