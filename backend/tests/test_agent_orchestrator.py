from pathlib import Path

from fastapi.testclient import TestClient

from app.agent.orchestrator import AgentOrchestrator
from app.domain.policy_repository import PolicyRepository
from app.main import create_app


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def build_orchestrator() -> AgentOrchestrator:
    return AgentOrchestrator(PolicyRepository(DATA_DIR))


def test_single_country_request_generates_plan_with_trace_and_citations():
    orchestrator = build_orchestrator()

    response = orchestrator.run("我想在新加坡雇一名月薪 8000 SGD 的高级工程师，10 月入职")

    assert response.plan.request_summary.country == "Singapore"
    assert response.plan.request_summary.role == "高级工程师"
    assert response.plan.request_summary.gross_salary == 8000
    assert response.plan.request_summary.currency == "SGD"
    assert response.plan.request_summary.start_date == "2026-10"
    assert response.plan.cost_breakdowns[0].monthly.total == 9935.92
    assert response.plan.compliance_results[0].overall_status == "pass"
    assert response.plan.employment_terms[0].annual_leave == "建议 14 天，法定最低 7 天。"
    assert response.plan.policy_citation_status == "complete"

    step_names = [step.name for step in response.trace]
    assert step_names == [
        "parse_hiring_terms",
        "get_country_policy",
        "calculate_employment_cost",
        "check_compliance",
        "compose_hiring_plan",
    ]
    assert response.trace[1].tool_name == "get_country_policy"
    assert response.trace[2].tool_name == "calculate_employment_cost"


def test_compliance_conflict_is_preserved_in_final_plan():
    orchestrator = build_orchestrator()

    response = orchestrator.run("我想在越南雇一名月薪 40000000 VND 的工程师，试用期 6 个月，年假 10 天")

    compliance = response.plan.compliance_results[0]
    probation = next(check for check in compliance.checks if check.item == "试用期")
    annual_leave = next(check for check in compliance.checks if check.item == "年假")

    assert compliance.overall_status == "fail"
    assert probation.status == "fail"
    assert probation.recommendation == "将试用期调整为 2 个月以内。"
    assert annual_leave.status == "fail"
    assert annual_leave.recommendation == "将年假调整为至少 12 天。"
    assert "需要调整" in response.plan.client_ready_summary


def test_multi_country_request_generates_comparison_for_each_country():
    orchestrator = build_orchestrator()

    response = orchestrator.run("在新加坡和越南雇同样的人，月薪 8000，哪个成本低？")

    countries = [item.country for item in response.plan.comparison]
    assert countries == ["Singapore", "Vietnam"]
    assert len(response.plan.cost_breakdowns) == 2
    assert response.plan.recommended_country == "Singapore"
    assert response.plan.comparison[0].monthly_total < response.plan.comparison[1].monthly_total

    tool_steps = [step for step in response.trace if step.event_type == "tool.completed"]
    assert [step.tool_name for step in tool_steps].count("get_country_policy") == 2
    assert [step.tool_name for step in tool_steps].count("calculate_employment_cost") == 2
    assert [step.tool_name for step in tool_steps].count("check_compliance") == 2


def test_agent_api_returns_serializable_hiring_plan():
    app = create_app(data_dir=DATA_DIR)
    client = TestClient(app)

    response = client.post(
        "/api/agent/hire",
        json={"message": "我想在新加坡雇一名月薪 8000 SGD 的高级工程师，10 月入职"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["plan"]["request_summary"]["country"] == "Singapore"
    assert payload["plan"]["cost_breakdowns"][0]["monthly"]["total"] == 9935.92
    assert payload["trace"][0]["name"] == "parse_hiring_terms"


def test_agent_api_rejects_request_without_salary():
    app = create_app(data_dir=DATA_DIR)
    client = TestClient(app)

    response = client.post("/api/agent/hire", json={"message": "我想在新加坡雇一个工程师"})

    assert response.status_code == 422
    assert "月薪" in response.json()["detail"]

