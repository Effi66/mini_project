from pathlib import Path

from app.domain.cost_calculator import CostCalculator
from app.domain.policy_repository import PolicyRepository


def calculate_employment_cost(data_dir: Path, country: str, gross_salary: float) -> dict:
    calculator = CostCalculator(PolicyRepository(data_dir))
    return calculator.calculate(country, gross_salary).model_dump()

