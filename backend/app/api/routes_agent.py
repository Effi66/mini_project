from collections.abc import Iterator

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.agent.events import format_sse_event
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


@router.post("/hire/stream")
def hire_stream(payload: HireRequest, request: Request) -> StreamingResponse:
    orchestrator = get_orchestrator(request)

    def event_generator() -> Iterator[str]:
        yield format_sse_event("agent.started", {"message": "开始处理雇佣需求。"})
        try:
            result = orchestrator.run(payload.message)
        except ValueError as exc:
            yield format_sse_event("agent.error", {"detail": str(exc)})
            return

        for step in result.trace:
            if step.event_type == "tool.completed":
                yield format_sse_event(
                    "tool.called",
                    {
                        "tool": step.tool_name,
                        "message": f"正在调用 {step.tool_name}。",
                    },
                )
                yield format_sse_event(
                    "tool.completed",
                    {
                        "tool": step.tool_name,
                        "message": step.message,
                    },
                )
            else:
                yield format_sse_event(
                    step.event_type,
                    {
                        "step": step.name,
                        "message": step.message,
                    },
                )

        yield format_sse_event("agent.completed", {"plan": result.plan.model_dump()})

    return StreamingResponse(event_generator(), media_type="text/event-stream")
