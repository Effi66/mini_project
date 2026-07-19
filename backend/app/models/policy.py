from pathlib import Path

from pydantic import BaseModel, ConfigDict


class Citation(BaseModel):
    source_file: str
    json_path: str
    quote: str


class CountryMetadata(BaseModel):
    country: str
    country_code: str
    currency: str


class EmployerContribution(BaseModel):
    name: str
    rate: float
    monthly_salary_cap: float | None
    notes: str


class ThirteenthMonth(BaseModel):
    statutory: bool
    customary: bool
    notes: str


class AnnualLeave(BaseModel):
    statutory_min_days: int
    market_typical_days: int
    notes: str


class Probation(BaseModel):
    max_months: int | None
    typical_months: int | None
    notes: str


class TerminationRule(BaseModel):
    tenure: str
    notice: str


class TerminationNotice(BaseModel):
    rules: list[TerminationRule]
    notes: str


class MinimumWage(BaseModel):
    monthly: float | None
    notes: str


class TaxBracket(BaseModel):
    up_to: float | None
    rate: float


class Policy(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    country: str
    country_code: str
    currency: str
    employer_contributions: list[EmployerContribution]
    thirteenth_month: ThirteenthMonth
    annual_leave: AnnualLeave
    probation: Probation
    termination_notice: TerminationNotice
    minimum_wage: MinimumWage
    public_holidays_per_year: int
    standard_working_hours_per_week: int
    source_path: Path

    income_tax_brackets_annual: list[TaxBracket] | None = None
    income_tax_brackets_monthly: list[TaxBracket] | None = None


class PolicySummary(BaseModel):
    country: str
    country_code: str
    currency: str
    employer_contributions: list[str]
    annual_leave_min_days: int
    probation_notes: str
    termination_notice_notes: str
    citations: list[Citation]

    model_config = ConfigDict(json_schema_extra={"additionalProperties": False})
