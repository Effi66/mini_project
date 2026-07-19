from fastapi import APIRouter, HTTPException, Request

from app.agent.orchestrator import AgentOrchestrator
from app.agent.schemas import HireRequest
from app.domain.policy_repository import PolicyRepository


router = APIRouter(prefix="/api/agent", tags=["agent"])


def get_orchestrator(request: Request) -> AgentOrchestrator:
    repository: PolicyRepository = request.app.state.policy_repository
    return AgentOrchestrator(repository, agent_mode=request.app.state.settings.agent_mode)


@router.post("/hire")
def hire(payload: HireRequest, request: Request) -> dict:
    orchestrator = get_orchestrator(request)
    try:
        return orchestrator.run(payload.message).model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
