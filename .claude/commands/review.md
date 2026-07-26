Invoke **architecture-reviewer**, **performance-reviewer**, and **security-reviewer** sequentially (in that order) on the current branch diff.

Before invoking the reviewers, assess the diff complexity once and apply the same model to all three:
- **Use Sonnet** (pass `model: claude-sonnet-4-6` to all three agents) for: small diffs (<100 lines), single-file changes, config-only changes, documentation updates.
- **Use Opus** (default, no override needed) for: large diffs, multi-file changes, new routes/models, security-sensitive changes, architectural changes.

First invoke architecture-reviewer and wait for it to complete. Then invoke performance-reviewer and wait for it to complete. Then invoke security-reviewer. This prevents Opus rate-limit throttling on Pro plan, avoiding costly retry loops.

All three agents must:
- Run `git diff main...HEAD` to see all changes
- Run `git log main...HEAD --oneline` to understand the commit structure
- Apply their full review checklist from their system prompt

After all three complete, print their outputs under headings:

```
## Architecture Review
<architecture-reviewer output>

## Performance Review
<performance-reviewer output>

## Security Review
<security-reviewer output>
```

If any output contains violations:
- List all violations together
- Suggest specific fixes with file and line references
- Ask whether to invoke `/implement` to address them, or proceed to `/ship`
- If fixes are applied, re-run all three reviewers (counts as iteration 1)
- Maximum 2 self-correcting iterations before escalating to the user for a manual decision

If all three output LGTM, print: `All clear — run /ship to push.`
