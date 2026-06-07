# Blog-Post Skill

**Trigger keywords**: blog, article, write a post, technical post, blog post, write about, publish

---

## Purpose

Produce a structured technical blog post through a short audience interview followed by drafting.

---

## Interview — 5 questions

Ask these **one at a time**:

1. **Topic** — what is the post about? One sentence.
2. **Audience** — who is the reader? (e.g. "Python developers who know FastAPI basics but haven't used async generators")
3. **Goal** — what should the reader be able to do or understand after reading? One sentence.
4. **Tone** — pick one: tutorial / deep-dive / opinion / case-study / quick-tip
5. **Call to action** — what should the reader do next? (e.g. "try the code", "read the docs", "star the repo", "nothing")

---

## Post structure

```markdown
# <Title — specific, not generic>

<Hook: one short paragraph. A problem, a surprising fact, or a bold claim that makes the reader want to continue.>

## The problem
<What pain or gap does this address? Be concrete — show, don't tell.>

## The solution
<High-level explanation. Why this approach? What makes it the right choice here?>

## How it works
<Step-by-step or layered explanation. Include code examples from the actual project stack.>

### Step 1 — <name>
<Explanation + code block>

### Step 2 — <name>
<Explanation + code block>

## Gotchas & edge cases
<2–3 things that trip people up. Honest about limitations.>

## Takeaway
<One paragraph. What did we learn? What can the reader do right now?>

<CTA: one sentence matching what was specified in the interview.>
```

---

## Code snippet rules

- All code uses the project's actual stack (Python 3.11+, FastAPI, Pydantic v2, uv, httpx, pytest-asyncio)
- Snippets must be complete enough to run — no `# ... rest of code`
- Always annotate types in code examples
- If a snippet imports from the project, use the actual module paths (`from app.routes.items import ...`)

---

## Rules

- Title must be specific: "Streaming Claude responses in FastAPI with Server-Sent Events" not "Using Claude in Python"
- No filler phrases ("In this article, I will...", "As we can see...", "It's worth noting that...")
- Maximum one H1 (the title) — use H2/H3 for sections
- Keep the post to 800–1500 words unless the user specifies otherwise
- After drafting, ask: "Want me to adjust the tone, expand any section, or add more code examples?"
