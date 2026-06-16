import asyncio
import json
from pathlib import Path

from pydantic import ValidationError

from app.exceptions import CatalogueError
from app.models.agent import AgentCatalogue

_AGENTS_JSON: Path = Path(__file__).resolve().parent.parent / "ui" / "agents.json"

_catalogue: AgentCatalogue | None = None


async def _load() -> AgentCatalogue:
    try:
        raw = await asyncio.to_thread(_AGENTS_JSON.read_text, encoding="utf-8")
    except FileNotFoundError:
        raise CatalogueError("agents.json not found")
    try:
        data = json.loads(raw)
        return AgentCatalogue.model_validate(data)
    except (json.JSONDecodeError, ValidationError):
        raise CatalogueError("agents.json is malformed")


async def get_catalogue() -> AgentCatalogue:
    """Return the cached catalogue, loading from agents.json on first call."""
    global _catalogue
    if _catalogue is None:
        _catalogue = await _load()
    return _catalogue
