import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def parse_sse_events(raw_text: str) -> list[dict]:
    events = []
    current_event: str | None = None
    current_data: str | None = None

    for line in raw_text.splitlines():
        if line.startswith("event: "):
            current_event = line.removeprefix("event: ")
        elif line.startswith("data: "):
            current_data = line.removeprefix("data: ")
        elif line == "" and current_event is not None and current_data is not None:
            events.append({"event": current_event, "data": json.loads(current_data)})
            current_event = None
            current_data = None

    return events


def test_hire_stream_emits_ordered_agent_and_tool_events():
    app = create_app(data_dir=DATA_DIR)
    client = TestClient(app)

    with client.stream(
        "POST",
        "/api/agent/hire/stream",
        json={"message": "我想在新加坡雇一名月薪 8000 SGD 的高级工程师，10 月入职"},
    ) as response:
        body = response.read().decode("utf-8")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")

    events = parse_sse_events(body)
    event_names = [event["event"] for event in events]
    assert event_names == [
        "agent.started",
        "agent.step",
        "tool.called",
        "tool.completed",
        "tool.called",
        "tool.completed",
        "tool.called",
        "tool.completed",
        "agent.step",
        "agent.completed",
    ]

    assert events[0]["data"]["message"] == "开始处理雇佣需求。"
    assert events[2]["data"]["tool"] == "get_country_policy"
    assert events[4]["data"]["tool"] == "calculate_employment_cost"
    assert events[6]["data"]["tool"] == "check_compliance"
    assert events[-1]["data"]["plan"]["request_summary"]["country"] == "Singapore"
    assert events[-1]["data"]["plan"]["cost_breakdowns"][0]["monthly"]["total"] == 9935.92


def test_hire_stream_emits_agent_error_for_invalid_request():
    app = create_app(data_dir=DATA_DIR)
    client = TestClient(app)

    with client.stream(
        "POST",
        "/api/agent/hire/stream",
        json={"message": "我想在新加坡雇一个工程师"},
    ) as response:
        body = response.read().decode("utf-8")

    assert response.status_code == 200
    events = parse_sse_events(body)
    assert [event["event"] for event in events] == ["agent.started", "agent.error"]
    assert "月薪" in events[-1]["data"]["detail"]

