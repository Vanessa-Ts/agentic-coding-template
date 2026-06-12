# Infografik Skill

**Trigger keywords**: infographic, infografik, image generation, generate image, FLUX, Hugging Face, visualise data, create a diagram image

---

## Purpose

Generate AI images (infographics, diagrams, illustrations) via the Hugging Face Inference API using the FLUX.1 model family. Images are saved to `docs/assets/`.

---

## Requirements

- `HF_TOKEN` environment variable must be set (Hugging Face access token with Inference API permission)
- `httpx` is already in the project dependencies
- Output directory: `docs/assets/` (create if missing)

---

## Python implementation

```python
import asyncio
import httpx
from pathlib import Path

HF_API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"

async def generate_image(prompt: str, output_path: Path, hf_token: str) -> Path:
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {"inputs": prompt}

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(HF_API_URL, headers=headers, json=payload)
        response.raise_for_status()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(response.content)
    return output_path
```

Usage:
```python
import asyncio, os
from pathlib import Path

asyncio.run(generate_image(
    prompt="...",
    output_path=Path("docs/assets/my-infographic.png"),
    hf_token=os.environ["HF_TOKEN"],
))
```

---

## Prompt structure for infographics

A good FLUX.1 infographic prompt has 4 parts:

```
<Style> infographic showing <topic>. <Layout description>. <Visual elements>. Clean white background, professional design, high resolution.
```

Examples:
```
Flat design infographic showing FastAPI request lifecycle. Horizontal flow diagram with 5 steps: Client → Router → Depends → Handler → Response. Each step in a rounded rectangle with icon. Arrows connecting steps. Sans-serif typography, blue and teal color palette. Clean white background, professional design, high resolution.

Minimal infographic comparing sync vs async Python. Two-column layout. Left column labeled "sync" with a single worker serving one request. Right column labeled "async" with one worker serving multiple requests concurrently. Simple icons, red and green accent colors. Clean white background, professional design, high resolution.
```

---

## FastAPI route (optional — for on-demand generation)

```python
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

router = APIRouter(prefix="/infografik", tags=["infografik"])

class ImageRequest(BaseModel):
    prompt: str

@router.post("/generate", status_code=200)
async def generate(payload: ImageRequest, settings: Settings = Depends(get_settings)) -> Response:
    if not settings.hf_token:
        raise HTTPException(status_code=503, detail="HF_TOKEN not configured")
    try:
        image_bytes = await _call_flux(payload.prompt, settings.hf_token)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"Hugging Face API error: {exc.response.status_code}")
    return Response(content=image_bytes, media_type="image/png")
```

---

## Rules

- `HF_TOKEN` must come from `pydantic-settings` / env — never hardcoded
- Set `timeout=120.0` — FLUX generation can take 30–90 seconds for cold starts
- Always save images to `docs/assets/` with a descriptive filename (kebab-case, `.png`)
- If the model returns a 503 ("loading"), wait 20 seconds and retry once
- Do not commit generated images to git — add `docs/assets/*.png` to `.gitignore`
