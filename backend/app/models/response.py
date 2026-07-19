from pydantic import BaseModel

from app.models.policy import Citation


class ContributionCostItem(BaseModel):
    name: str
    base: float
    rate: float
    monthly_amount: float
    annual_amount: float
    note: str


class BonusBreakdown(BaseModel):
    months_per_year: int
    basis: str
    monthly_accrual: float
    annual_amount: float
    citation: Citation


class MonthlyCostBreakdown(BaseModel):
    base_salary: float
    employer_contributions: list[ContributionCostItem]
    employer_contributions_total: float
    bonus_accrual: float
    total: float


class AnnualCostBreakdown(BaseModel):
    base_salary: float
    employer_contributions: float
    bonus: float
    total: float


class EmploymentCostBreakdown(BaseModel):
    country: str
    country_code: str
    currency: str
    gross_salary_monthly: float
    monthly: MonthlyCostBreakdown
    annual: AnnualCostBreakdown
    bonus: BonusBreakdown

