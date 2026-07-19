import re
from dataclasses import dataclass
from datetime import date

from app.agent.events import agent_step, tool_completed
from app.agent.schemas import (
    AgentRunResponse,
    AgentTraceStep,
    ComparisonItem,
    EmploymentTermsSummary,
    HiringPlan,
    HiringRequestSummary,
    ParsedHiringRequest,
)
from app.domain.compliance_checker import ComplianceChecker
from app.domain.cost_calculator import CostCalculator
from app.domain.policy_repository import PolicyRepository
from app.models.request import HiringTerms
from app.models.response import ComplianceResult, EmploymentCostBreakdown
from app.tools.country_policy import get_country_policy


@dataclass(frozen=True)
class CountryPlanParts:
    country: str
    cost: EmploymentCostBreakdown
    compliance: ComplianceResult
    terms: EmploymentTermsSummary


class AgentOrchestrator:
    def __init__(
        self,
        policy_repository: PolicyRepository,
        current_date: date | None = None,
        agent_mode: str = "deterministic",
    ):
        self.policy_repository = policy_repository
        self.cost_calculator = CostCalculator(policy_repository)
        self.compliance_checker = ComplianceChecker(policy_repository)
        self.current_date = current_date or date.today()
        self.agent_mode = agent_mode

    def run(self, message: str) -> AgentRunResponse:
        trace: list[AgentTraceStep] = []
        parsed = self._parse_request(message)
        trace.append(agent_step("parse_hiring_terms", "已解析国家、薪资、岗位和雇佣条款。"))

        country_parts = [self._build_country_plan(country, parsed, trace) for country in parsed.countries]
        comparison = self._build_comparison(country_parts)
        recommended_country = self._recommend_country(comparison)
        summary = self._compose_summary(country_parts, recommended_country)
        trace.append(agent_step("compose_hiring_plan", "已生成客户可读雇佣方案。"))

        plan = HiringPlan(
            request_summary=HiringRequestSummary(
                countries=parsed.countries,
                country=country_parts[0].country,
                role=parsed.role,
                gross_salary=parsed.gross_salary,
                currency=parsed.currency,
                start_date=parsed.start_date,
            ),
            cost_breakdowns=[part.cost for part in country_parts],
            compliance_results=[part.compliance for part in country_parts],
            employment_terms=[part.terms for part in country_parts],
            comparison=comparison,
            recommended_country=recommended_country,
            client_ready_summary=summary,
            policy_citation_status=self._citation_status([part.compliance for part in country_parts]),
        )
        return AgentRunResponse(plan=plan, trace=trace)

    def _build_country_plan(
        self,
        country: str,
        parsed: ParsedHiringRequest,
        trace: list[AgentTraceStep],
    ) -> CountryPlanParts:
        policy_summary = get_country_policy(self.policy_repository, country)
        trace.append(
            tool_completed(
                "get_country_policy",
                "get_country_policy",
                f"已读取 {policy_summary.country} 雇佣政策。",
            )
        )

        cost = self.cost_calculator.calculate(country, parsed.gross_salary)
        trace.append(
            tool_completed(
                "calculate_employment_cost",
                "calculate_employment_cost",
                f"已计算 {cost.country} 雇主成本。",
            )
        )

        compliance = self.compliance_checker.check(
            country,
            HiringTerms(
                gross_salary=parsed.gross_salary,
                probation_months=parsed.probation_months,
                annual_leave_days=parsed.annual_leave_days,
                working_hours_per_week=parsed.working_hours_per_week,
                notice_days=parsed.notice_days,
                include_13th_month=parsed.include_13th_month,
            ),
        )
        trace.append(
            tool_completed(
                "check_compliance",
                "check_compliance",
                f"已完成 {compliance.country} 合规检查。",
            )
        )

        policy = self.policy_repository.get_policy(country)
        terms = EmploymentTermsSummary(
            country=policy.country,
            probation=self._format_probation_term(policy),
            annual_leave=(
                f"建议 {policy.annual_leave.market_typical_days} 天，"
                f"法定最低 {policy.annual_leave.statutory_min_days} 天。"
            ),
            termination_notice=policy.termination_notice.notes,
            working_hours=f"标准每周 {policy.standard_working_hours_per_week} 小时。",
            bonus=policy.thirteenth_month.notes,
        )
        return CountryPlanParts(country=policy.country, cost=cost, compliance=compliance, terms=terms)

    def _parse_request(self, message: str) -> ParsedHiringRequest:
        if self.agent_mode not in {"deterministic", "llm"}:
            raise ValueError("AGENT_MODE 必须是 deterministic 或 llm。")

        countries = self._parse_countries(message)
        gross_salary = self._parse_salary(message)
        if gross_salary is None:
            raise ValueError("请在雇佣需求中提供月薪，例如：月薪 8000 SGD。")

        currency = self._parse_currency(message) or self.policy_repository.get_policy(countries[0]).currency
        return ParsedHiringRequest(
            countries=countries,
            role=self._parse_role(message),
            gross_salary=gross_salary,
            currency=currency,
            start_date=self._parse_start_date(message),
            probation_months=self._parse_number_before_keyword(message, "试用期", "个月"),
            annual_leave_days=self._parse_number_before_keyword(message, "年假", "天"),
            working_hours_per_week=self._parse_number_before_keyword(message, "每周", "小时"),
            notice_days=self._parse_number_before_keyword(message, "通知期", "天"),
            include_13th_month=self._parse_thirteenth_month(message),
        )

    def _parse_countries(self, message: str) -> list[str]:
        found: list[str] = []
        country_markers = [
            ("新加坡", "Singapore"),
            ("Singapore", "Singapore"),
            ("SG", "Singapore"),
            ("越南", "Vietnam"),
            ("Vietnam", "Vietnam"),
            ("VN", "Vietnam"),
            ("印尼", "Indonesia"),
            ("印度尼西亚", "Indonesia"),
            ("Indonesia", "Indonesia"),
            ("菲律宾", "Philippines"),
            ("Philippines", "Philippines"),
            ("日本", "Japan"),
            ("Japan", "Japan"),
        ]
        for marker, country in country_markers:
            if marker in message and country not in found:
                found.append(country)
        if not found:
            raise ValueError("请提供支持的雇佣国家，例如新加坡、越南、印尼、菲律宾或日本。")
        return found

    def _parse_salary(self, message: str) -> float | None:
        match = re.search(r"月薪\s*([0-9][0-9,]*)", message, flags=re.IGNORECASE)
        if match is None:
            return None
        return float(match.group(1).replace(",", ""))

    def _parse_currency(self, message: str) -> str | None:
        match = re.search(r"\b(SGD|VND|IDR|PHP|JPY)\b", message, flags=re.IGNORECASE)
        if match is None:
            return None
        return match.group(1).upper()

    def _parse_role(self, message: str) -> str | None:
        match = re.search(r"名(?:月薪\s*[0-9][0-9,]*\s*[A-Z]{0,3}\s*的)?([^，,。？?]+)", message)
        if match:
            role = match.group(1).strip()
            if role and not role.startswith("月薪"):
                return role
        if "工程师" in message:
            return "工程师"
        return None

    def _parse_start_date(self, message: str) -> str | None:
        match = re.search(r"(\d{1,2})\s*月入职", message)
        if match is None:
            return None
        month = int(match.group(1))
        year = self.current_date.year
        if month < self.current_date.month:
            year += 1
        return f"{year}-{month:02d}"

    def _parse_number_before_keyword(self, message: str, leading: str, trailing: str) -> float | None:
        pattern = rf"{re.escape(leading)}\s*(?:为|是)?\s*(\d+(?:\.\d+)?)\s*{re.escape(trailing)}"
        match = re.search(pattern, message)
        if match is None:
            return None
        return float(match.group(1))

    def _parse_thirteenth_month(self, message: str) -> bool | None:
        if "不发放13薪" in message or "不发放 13 薪" in message or "不发13薪" in message:
            return False
        if "13薪" in message or "13 薪" in message:
            return True
        return None

    def _build_comparison(self, country_parts: list[CountryPlanParts]) -> list[ComparisonItem]:
        if len(country_parts) < 2:
            return []
        return [
            ComparisonItem(
                country=part.country,
                currency=part.cost.currency,
                monthly_total=part.cost.monthly.total,
                annual_total=part.cost.annual.total,
                compliance_status=part.compliance.overall_status,
            )
            for part in country_parts
        ]

    def _recommend_country(self, comparison: list[ComparisonItem]) -> str | None:
        if not comparison:
            return None
        passing = [item for item in comparison if item.compliance_status == "pass"]
        candidates = passing or comparison
        return min(candidates, key=lambda item: item.monthly_total).country

    def _compose_summary(self, country_parts: list[CountryPlanParts], recommended_country: str | None) -> str:
        if any(part.compliance.overall_status == "fail" for part in country_parts):
            return "方案中存在合规冲突，需要调整后再推进雇佣。"
        if recommended_country:
            return f"多国对比完成，推荐优先考虑 {recommended_country}。"
        part = country_parts[0]
        return (
            f"在 {part.country} 雇佣该岗位的月度雇主总成本约为 "
            f"{part.cost.monthly.total:g} {part.cost.currency}。"
        )

    def _citation_status(self, compliance_results: list[ComplianceResult]) -> str:
        for result in compliance_results:
            for check in result.checks:
                if check.status != "unknown" and check.citation is None:
                    return "incomplete"
        return "complete"

    def _format_probation_term(self, policy) -> str:
        if policy.probation.max_months is None:
            return f"建议 {policy.probation.typical_months} 个月；法律无强制上限。"
        return f"建议不超过 {policy.probation.max_months} 个月。"
