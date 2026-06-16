import asyncio
import json
from pathlib import Path

from pydantic import ValidationError

from app.models.agent import AgentCatalogue

_AGENTS_JSON: Path = Path(__file__).resolve().parent.parent / "ui" / "agents.json"


class CatalogueError(Exception):
    pass


async def get_catalogue() -> AgentCatalogue:
    """Read, parse, and validate agents.json on every request."""
    try:
        raw = await asyncio.to_thread(_AGENTS_JSON.read_text, encoding="utf-8")
    except FileNotFoundError:
        raise CatalogueError("agents.json not found")

    try:
        data = json.loads(raw)
        return AgentCatalogue.model_validate(data)
    except (json.JSONDecodeError, ValidationError):
        raise CatalogueError("agents.json is malformed")
