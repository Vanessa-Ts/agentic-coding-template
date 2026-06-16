from typing import Literal

from pydantic import BaseModel


class AgentOrSkill(BaseModel):
    type: Literal["agent", "skill"]
    name: str
    role: str
    icon: str
    connects_to: list[str]


class AgentCatalogue(BaseModel):
    agents: list[AgentOrSkill]
    skills: list[AgentOrSkill]
