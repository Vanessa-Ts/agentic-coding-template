Invoke **architecture-reviewer**, **performance-reviewer**, and **security-reviewer** in parallel on the current branch diff.

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
