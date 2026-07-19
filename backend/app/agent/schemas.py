from pydantic import BaseModel

from app.models.response import ComplianceResult, EmploymentCostBreakdown


class ParsedHiringRequest(BaseModel):
    countries: list[str]
    role: str | None
    gross_salary: float
    currency: str
    start_date: str | None
    probation_months: float | None
    annual_leave_days: float | None
    working_hours_per_week: float | None
    notice_days: float | None
    include_13th_month: bool | None


class AgentTraceStep(BaseModel):
    event_type: str
    name: str
    message: str
    tool_name: str | None = None


class HiringRequestSummary(BaseModel):
    countries: list[str]
    country: str
    role: str | None
    gross_salary: float
    currency: str
    start_date: str | None


class EmploymentTermsSummary(BaseModel):
    country: str
    probation: str
    annual_leave: str
    termination_notice: str
    working_hours: str
    bonus: str


class ComparisonItem(BaseModel):
    country: str
    currency: str
    monthly_total: float
    annual_total: float
    compliance_status: str


class HiringPlan(BaseModel):
    request_summary: HiringRequestSummary
    cost_breakdowns: list[EmploymentCostBreakdown]
    compliance_results: list[ComplianceResult]
    employment_terms: list[EmploymentTermsSummary]
    comparison: list[ComparisonItem]
    recommended_country: str | None
    client_ready_summary: str
    policy_citation_status: str


class AgentRunResponse(BaseModel):
    plan: HiringPlan
    trace: list[AgentTraceStep]


class HireRequest(BaseModel):
    message: str

