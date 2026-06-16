from typing import Literal

from pydantic import BaseModel, ConfigDict


class AgentOrSkill(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["agent", "skill"]
    name: str
    role: str
    description: str = ""
    icon: str
    connects_to: list[str] = []


class AgentCatalogue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agents: list[AgentOrSkill]
    skills: list[AgentOrSkill]
