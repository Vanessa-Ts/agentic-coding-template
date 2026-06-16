import json
from pathlib import Path

from fastapi import HTTPException
from pydantic import ValidationError

from app.models.agent import AgentCatalogue

_AGENTS_JSON: Path = Path(__file__).resolve().parent.parent / "ui" / "agents.json"


async def get_catalogue() -> AgentCatalogue:
    """Read, parse, and validate agents.json on every request."""
    try:
        raw = _AGENTS_JSON.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="agents.json not found")

    try:
        data = json.loads(raw)
        return AgentCatalogue.model_validate(data)
    except (json.JSONDecodeError, ValidationError):
        raise HTTPException(status_code=500, detail="agents.json is malformed")
