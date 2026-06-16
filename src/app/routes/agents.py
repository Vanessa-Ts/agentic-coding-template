from fastapi import APIRouter, Depends

from app.models.agent import AgentCatalogue
from app.services.agent_catalogue import get_catalogue

router = APIRouter()


@router.get("/agents", response_model=AgentCatalogue, status_code=200)
async def list_agents(
    catalogue: AgentCatalogue = Depends(get_catalogue),
) -> AgentCatalogue:
    """Return the full agent and skill catalogue."""
    return catalogue
