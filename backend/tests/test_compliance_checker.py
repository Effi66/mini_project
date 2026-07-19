from pathlib import Path

from app.domain.compliance_checker import ComplianceChecker
from app.domain.policy_repository import PolicyRepository
from app.models.request import HiringTerms
from app.tools.compliance import check_compliance


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def build_checker() -> ComplianceChecker:
    return ComplianceChecker(PolicyRepository(DATA_DIR))


def test_vietnam_probation_six_months_fails_with_citation_and_alternative():
    checker = build_checker()

    result = checker.check(
        "Vietnam",
        HiringTerms(gross_salary=40_000_000, probation_months=6),
    )

    probation = next(check for check in result.checks if check.item == "试用期")
    assert result.overall_status == "fail"
    assert probation.status == "fail"
    assert probation.requested == "6 个月"
    assert probation.required == "不超过 2 个月"
    assert "试用期上限" in probation.citation.quote
    assert probation.citation.source_file == "data/vietnam.json"
    assert probation.recommendation == "将试用期调整为 2 个月以内。"


def test_singapore_probation_without_legal_cap_passes_with_typical_guidance():
    checker = build_checker()

    result = checker.check(
        "Singapore",
        HiringTerms(gross_salary=8000, probation_months=6),
    )

    probation = next(check for check in result.checks if check.item == "试用期")
    assert probation.status == "pass"
    assert probation.required == "法律无强制上限；市场惯例 3 个月。"
    assert probation.recommendation is None


def test_indonesia_salary_below_minimum_wage_fails():
    checker = build_checker()

    result = checker.check("Indonesia", HiringTerms(gross_salary=5_000_000))

    minimum_wage = next(check for check in result.checks if check.item == "最低工资")
    assert result.overall_status == "fail"
    assert minimum_wage.status == "fail"
    assert minimum_wage.requested == "5000000 IDR/月"
    assert minimum_wage.required == "至少 5396761 IDR/月"
    assert minimum_wage.citation.json_path == "minimum_wage.notes"
    assert "5,396,761 IDR/月" in minimum_wage.citation.quote
    assert minimum_wage.recommendation == "将月薪调整为至少 5396761 IDR。"


def test_philippines_omitted_statutory_thirteenth_month_fails():
    checker = build_checker()

    result = checker.check("Philippines", HiringTerms(gross_salary=50_000, include_13th_month=False))

    thirteenth_month = next(check for check in result.checks if check.item == "13 薪/强制奖金")
    assert result.overall_status == "fail"
    assert thirteenth_month.status == "fail"
    assert thirteenth_month.requested == "不发放"
    assert thirteenth_month.required == "必须发放"
    assert "第 13 月薪为法定强制" in thirteenth_month.citation.quote
    assert thirteenth_month.recommendation == "将法定 13 薪或强制奖金纳入雇佣方案。"


def test_missing_optional_terms_are_unknown_not_failures():
    checker = build_checker()

    result = checker.check("Japan", HiringTerms(gross_salary=700_000))

    statuses = {check.item: check.status for check in result.checks}
    assert statuses["试用期"] == "unknown"
    assert statuses["年假"] == "unknown"
    assert statuses["工作时长"] == "unknown"
    assert statuses["解雇通知期"] == "unknown"
    assert result.overall_status == "pass"


def test_annual_leave_working_hours_and_notice_fail_with_recommendations():
    checker = build_checker()

    result = checker.check(
        "Philippines",
        HiringTerms(
            gross_salary=50_000,
            annual_leave_days=3,
            working_hours_per_week=60,
            notice_days=14,
        ),
    )

    annual_leave = next(check for check in result.checks if check.item == "年假")
    working_hours = next(check for check in result.checks if check.item == "工作时长")
    notice = next(check for check in result.checks if check.item == "解雇通知期")

    assert annual_leave.status == "fail"
    assert annual_leave.required == "至少 5 天"
    assert annual_leave.recommendation == "将年假调整为至少 5 天。"
    assert working_hours.status == "fail"
    assert working_hours.required == "不超过每周 48 小时"
    assert working_hours.recommendation == "将标准工作时长调整为每周 48 小时以内。"
    assert notice.status == "fail"
    assert notice.required == "至少 30 天"
    assert notice.recommendation == "将解雇通知期调整为至少 30 天。"


def test_compliance_tool_returns_serializable_result():
    result = check_compliance(
        DATA_DIR,
        "VN",
        {"gross_salary": 40_000_000, "probation_months": 6},
    )

    assert result["country"] == "Vietnam"
    assert result["overall_status"] == "fail"
    assert any(
        check["item"] == "试用期"
        and check["status"] == "fail"
        and check["citation"]["source_file"] == "data/vietnam.json"
        for check in result["checks"]
    )
