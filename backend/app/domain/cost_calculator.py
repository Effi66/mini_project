from app.domain.citations import build_citation
from app.domain.policy_repository import PolicyRepository
from app.models.policy import Policy
from app.models.response import (
    AnnualCostBreakdown,
    BonusBreakdown,
    ContributionCostItem,
    EmploymentCostBreakdown,
    MonthlyCostBreakdown,
)


class CostCalculator:
    def __init__(self, policy_repository: PolicyRepository):
        self.policy_repository = policy_repository

    def calculate(self, country: str, gross_salary: float) -> EmploymentCostBreakdown:
        policy = self.policy_repository.get_policy(country)
        contributions = [
            self._calculate_contribution(gross_salary, contribution)
            for contribution in policy.employer_contributions
        ]
        bonus = self._normalize_bonus(policy, gross_salary)

        monthly_contributions_total = round(
            sum(item.monthly_amount for item in contributions),
            2,
        )
        monthly_total = round(gross_salary + monthly_contributions_total + bonus.monthly_accrual, 2)
        annual_base_salary = round(gross_salary * 12, 2)
        annual_contributions_total = round(sum(item.annual_amount for item in contributions), 2)
        annual_total = round(annual_base_salary + annual_contributions_total + bonus.annual_amount, 2)

        return EmploymentCostBreakdown(
            country=policy.country,
            country_code=policy.country_code,
            currency=policy.currency,
            gross_salary_monthly=round(gross_salary, 2),
            monthly=MonthlyCostBreakdown(
                base_salary=round(gross_salary, 2),
                employer_contributions=contributions,
                employer_contributions_total=monthly_contributions_total,
                bonus_accrual=bonus.monthly_accrual,
                total=monthly_total,
            ),
            annual=AnnualCostBreakdown(
                base_salary=annual_base_salary,
                employer_contributions=annual_contributions_total,
                bonus=bonus.annual_amount,
                total=annual_total,
            ),
            bonus=bonus,
        )

    def _calculate_contribution(self, gross_salary: float, contribution) -> ContributionCostItem:
        cap = contribution.monthly_salary_cap
        base = gross_salary if cap is None else min(gross_salary, cap)
        monthly_amount = round(base * contribution.rate, 2)
        return ContributionCostItem(
            name=contribution.name,
            base=round(base, 2),
            rate=contribution.rate,
            monthly_amount=monthly_amount,
            annual_amount=round(monthly_amount * 12, 2),
            note=contribution.notes,
        )

    def _normalize_bonus(self, policy: Policy, gross_salary: float) -> BonusBreakdown:
        months_per_year = 0
        basis = "none"

        if policy.thirteenth_month.statutory:
            months_per_year = 1
            basis = "statutory"
        elif policy.country_code == "JP" and policy.thirteenth_month.customary:
            months_per_year = 2
            basis = "customary"
        elif policy.thirteenth_month.customary:
            months_per_year = 1
            basis = "customary"

        citation = build_citation(
            self.policy_repository.data_dir,
            policy.source_path,
            "thirteenth_month.notes",
            policy.thirteenth_month.notes,
        )
        return BonusBreakdown(
            months_per_year=months_per_year,
            basis=basis,
            monthly_accrual=round(gross_salary * months_per_year / 12, 2),
            annual_amount=round(gross_salary * months_per_year, 2),
            citation=citation,
        )
