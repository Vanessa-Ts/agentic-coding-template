"""Tests for GET /api/agents."""

from pathlib import Path

import pytest
from httpx import AsyncClient

import app.services.agent_catalogue as agent_catalogue_module


async def test_list_agents_happy_path(client: AsyncClient) -> None:
    """GET /api/agents returns 200 when agents.json is present and valid."""
    response = await client.get("/api/agents")
    assert response.status_code == 200


async def test_list_agents_response_keys(client: AsyncClient) -> None:
    """Response body contains top-level 'agents' and 'skills' keys."""
    response = await client.get("/api/agents")
    assert response.status_code == 200
    body = response.json()
    assert "agents" in body
    assert "skills" in body


async def test_list_agents_agents_non_empty(client: AsyncClient) -> None:
    """The 'agents' list contains at least one entry."""
    response = await client.get("/api/agents")
    assert response.status_code == 200
    body = response.json()
    assert len(body["agents"]) > 0


async def test_list_agents_skills_non_empty(client: AsyncClient) -> None:
    """The 'skills' list contains at least one entry."""
    response = await client.get("/api/agents")
    assert response.status_code == 200
    body = response.json()
    assert len(body["skills"]) > 0


@pytest.mark.parametrize("field", ["type", "name", "role", "icon", "connects_to"])
async def test_list_agents_first_entry_has_required_fields(
    client: AsyncClient, field: str
) -> None:
    """First entry in 'agents' has all required fields."""
    first = (await client.get("/api/agents")).json()["agents"][0]
    assert field in first


async def test_list_agents_missing_file(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Returns 500 when agents.json does not exist on the filesystem."""
    missing = tmp_path / "nonexistent.json"
    monkeypatch.setattr(agent_catalogue_module, "_AGENTS_JSON", missing)
    response = await client.get("/api/agents")
    assert response.status_code == 500


async def test_list_agents_malformed_json(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Returns 500 when agents.json contains invalid JSON."""
    bad_file = tmp_path / "agents.json"
    bad_file.write_text("{", encoding="utf-8")
    monkeypatch.setattr(agent_catalogue_module, "_AGENTS_JSON", bad_file)
    response = await client.get("/api/agents")
    assert response.status_code == 500


async def test_list_agents_schema_validation_error(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Returns 500 when agents.json is valid JSON but fails schema validation."""
    bad_file = tmp_path / "agents.json"
    bad_file.write_text('{"agents": "not-a-list", "skills": []}', encoding="utf-8")
    monkeypatch.setattr(agent_catalogue_module, "_AGENTS_JSON", bad_file)
    response = await client.get("/api/agents")
    assert response.status_code == 500
