from pathlib import Path

from app.domain.cost_calculator import CostCalculator
from app.domain.policy_repository import PolicyRepository
from app.tools.employment_cost import calculate_employment_cost


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def build_calculator() -> CostCalculator:
    return CostCalculator(PolicyRepository(DATA_DIR))


def test_singapore_cost_applies_contribution_caps_and_customary_bonus():
    calculator = build_calculator()

    result = calculator.calculate("Singapore", 8000)

    assert result.country == "Singapore"
    assert result.currency == "SGD"
    assert result.gross_salary_monthly == 8000

    cpf = next(item for item in result.monthly.employer_contributions if item.name.startswith("CPF"))
    sdl = next(item for item in result.monthly.employer_contributions if item.name.startswith("SDL"))

    assert cpf.base == 7400
    assert cpf.rate == 0.17
    assert cpf.monthly_amount == 1258
    assert cpf.annual_amount == 15096
    assert sdl.base == 4500
    assert sdl.monthly_amount == 11.25

    assert result.monthly.bonus_accrual == 666.67
    assert result.monthly.total == 9935.92
    assert result.annual.total == 119231.0
    assert result.bonus.months_per_year == 1
    assert result.bonus.basis == "customary"


def test_vietnam_cost_uses_each_contribution_cap_independently():
    calculator = build_calculator()

    result = calculator.calculate("VN", 120_000_000)

    amounts = {item.name: item for item in result.monthly.employer_contributions}

    assert amounts["社会保险（雇主缴纳）"].base == 46_800_000
    assert amounts["社会保险（雇主缴纳）"].monthly_amount == 8_190_000
    assert amounts["医疗保险（雇主缴纳）"].base == 46_800_000
    assert amounts["医疗保险（雇主缴纳）"].monthly_amount == 1_404_000
    assert amounts["失业保险（雇主缴纳）"].base == 99_200_000
    assert amounts["失业保险（雇主缴纳）"].monthly_amount == 992_000
    assert amounts["工会经费"].base == 46_800_000
    assert amounts["工会经费"].monthly_amount == 936_000

    assert result.monthly.bonus_accrual == 10_000_000
    assert result.monthly.total == 141_522_000
    assert result.annual.total == 1_698_264_000


def test_philippines_statutory_thirteenth_month_is_included():
    calculator = build_calculator()

    result = calculator.calculate("Philippines", 50_000)

    assert result.bonus.months_per_year == 1
    assert result.bonus.basis == "statutory"
    assert result.monthly.bonus_accrual == 4166.67
    assert result.annual.bonus == 50_000


def test_japan_customary_bonus_uses_fixture_simulation_of_two_months():
    calculator = build_calculator()

    result = calculator.calculate("Japan", 700_000)

    assert result.bonus.months_per_year == 2
    assert result.bonus.basis == "customary"
    assert result.monthly.bonus_accrual == 116666.67
    assert "2 个月赏与" in result.bonus.citation.quote


def test_employment_cost_tool_returns_serializable_breakdown():
    result = calculate_employment_cost(DATA_DIR, "SG", 8000)

    assert result["country"] == "Singapore"
    assert result["currency"] == "SGD"
    assert result["monthly"]["total"] == 9935.92
    assert any(
        item["name"] == "CPF 公积金（雇主缴纳）"
        and item["base"] == 7400
        and item["monthly_amount"] == 1258
        for item in result["monthly"]["employer_contributions"]
    )

