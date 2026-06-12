# Frontend Skill

**Trigger paths**: `src/app/ui/**`, `**/*.html`, `**/templates/**`
**Trigger keywords**: dashboard, landing page, Tailwind, HTML, frontend, UI, web page, HTMX, TailAdmin

---

## FastAPI + Jinja2 — template setup

Templates are rendered by the existing `Jinja2Templates` instance in `main.py`. Add new pages by:

1. Creating the HTML file in `src/app/ui/` (or `src/app/templates/`)
2. Adding a GET route that calls `templates.TemplateResponse`

```python
@router.get("/dashboard", response_class=HTMLResponse, status_code=200)
async def dashboard(request: Request) -> Response:
    return templates.TemplateResponse(request, "dashboard.html", {"title": "Dashboard"})
```

---

## Tailwind CSS — via CDN (dev / small projects)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ title }}</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 text-gray-900">
  <!-- content -->
</body>
</html>
```

For production, use the Tailwind CLI (no Node required):
```bash
# Download standalone CLI binary for the platform
# uv add --dev tailwindcss  # not available — use the standalone binary
curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64
chmod +x tailwindcss-linux-x64
./tailwindcss-linux-x64 -i src/app/ui/input.css -o src/app/ui/output.css --minify
```

---

## Common UI patterns

### Simple data table
```html
<div class="overflow-x-auto">
  <table class="min-w-full divide-y divide-gray-200">
    <thead class="bg-gray-100">
      <tr>
        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
      </tr>
    </thead>
    <tbody class="divide-y divide-gray-200">
      {% for item in items %}
      <tr>
        <td class="px-6 py-4 whitespace-nowrap text-sm">{{ item.name }}</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm">{{ item.status }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
```

### HTMX — lightweight interactivity without JavaScript

Add `htmx.org` to the template head for partial page updates:
```html
<script src="https://unpkg.com/htmx.org@2/dist/htmx.min.js"></script>
```

Fetch a partial and swap into a div:
```html
<button hx-post="/items"
        hx-target="#item-list"
        hx-swap="afterbegin"
        hx-include="[name='item-form']">
  Add item
</button>
<div id="item-list">
  {% include "partials/item_list.html" %}
</div>
```

The corresponding route returns an HTML fragment (not a full page):
```python
@router.post("/items/partial", response_class=HTMLResponse, status_code=200)
async def create_item_partial(request: Request, ...) -> Response:
    return templates.TemplateResponse(request, "partials/item_card.html", {"item": new_item})
```

### TailAdmin dashboard layout

TailAdmin is a Tailwind-based admin dashboard template. Use its sidebar + topbar layout as a base:
- Sidebar: `<aside class="fixed left-0 top-0 h-screen w-72 ...">`
- Main content: `<main class="ml-72 p-8">`
- Cards: `<div class="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">`

---

## Static files

Already mounted in `main.py` at `/static → src/app/ui/`. Reference in templates:
```html
<link rel="stylesheet" href="/static/output.css">
<script src="/static/app.js"></script>
```

---

## Rules

- Keep JavaScript minimal — prefer HTMX for interactivity, avoid SPA frameworks for simple pages
- All pages must be served through a FastAPI route with proper `response_class=HTMLResponse`
- Never include secrets or API keys in HTML/JS
- Test pages by starting the dev server (`uvicorn app.main:app --reload`) and visiting in a browser
