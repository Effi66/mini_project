from app.agent.schemas import AgentTraceStep


def agent_step(name: str, message: str) -> AgentTraceStep:
    return AgentTraceStep(event_type="agent.step", name=name, message=message)


def tool_completed(name: str, tool_name: str, message: str) -> AgentTraceStep:
    return AgentTraceStep(
        event_type="tool.completed",
        name=name,
        tool_name=tool_name,
        message=message,
    )

