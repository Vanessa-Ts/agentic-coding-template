Invoke **quality-reviewer** AND **security-reviewer** in parallel on the current branch diff.

Both agents must:
- Run `git diff main...HEAD` to see all changes
- Run `git log main...HEAD --oneline` to understand the commit structure
- Apply their full review checklist from their system prompt

After both complete, print their outputs under headings:

```
## Quality Review
<quality-reviewer output>

## Security Review
<security-reviewer output>
```

If either output contains violations:
- List all violations together
- Suggest specific fixes with file and line references
- Ask whether to invoke `/implement` to address them, or proceed to `/ship`
- If fixes are applied, re-run both reviewers (counts as iteration 1)
- Maximum 2 self-correcting iterations before escalating to the user for a manual decision

If both output LGTM, print: `All clear — run /ship to push.`
