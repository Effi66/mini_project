import re

from app.domain.citations import build_citation
from app.domain.policy_repository import PolicyRepository
from app.models.policy import Citation, Policy
from app.models.request import HiringTerms
from app.models.response import ComplianceCheck, ComplianceResult


class ComplianceChecker:
    def __init__(self, policy_repository: PolicyRepository):
        self.policy_repository = policy_repository

    def check(self, country: str, terms: HiringTerms) -> ComplianceResult:
        policy = self.policy_repository.get_policy(country)
        checks = [
            self._check_minimum_wage(policy, terms),
            self._check_probation(policy, terms),
            self._check_annual_leave(policy, terms),
            self._check_working_hours(policy, terms),
            self._check_termination_notice(policy, terms),
            self._check_thirteenth_month(policy, terms),
        ]
        overall_status = "fail" if any(check.status == "fail" for check in checks) else "pass"
        return ComplianceResult(
            country=policy.country,
            country_code=policy.country_code,
            currency=policy.currency,
            overall_status=overall_status,
            checks=checks,
        )

    def _check_minimum_wage(self, policy: Policy, terms: HiringTerms) -> ComplianceCheck:
        citation = self._citation(policy, "minimum_wage.notes", policy.minimum_wage.notes)
        if terms.gross_salary is None:
            return self._unknown("最低工资", citation, "用户未提供月薪，无法检查最低工资。")
        if policy.minimum_wage.monthly is None:
            return self._pass(
                "最低工资",
                f"{self._format_number(terms.gross_salary)} {policy.currency}/月",
                "本地 fixture 未设置全国最低工资。",
                citation,
            )

        required = policy.minimum_wage.monthly
        if terms.gross_salary < required:
            return ComplianceCheck(
                item="最低工资",
                status="fail",
                requested=f"{self._format_number(terms.gross_salary)} {policy.currency}/月",
                required=f"至少 {self._format_number(required)} {policy.currency}/月",
                citation=citation,
                recommendation=f"将月薪调整为至少 {self._format_number(required)} {policy.currency}。",
            )
        return self._pass(
            "最低工资",
            f"{self._format_number(terms.gross_salary)} {policy.currency}/月",
            f"至少 {self._format_number(required)} {policy.currency}/月",
            citation,
        )

    def _check_probation(self, policy: Policy, terms: HiringTerms) -> ComplianceCheck:
        citation = self._citation(policy, "probation.notes", policy.probation.notes)
        if terms.probation_months is None:
            return self._unknown("试用期", citation, "用户未提供试用期，后续方案应给出建议值。")
        if policy.probation.max_months is None:
            typical = policy.probation.typical_months
            required = f"法律无强制上限；市场惯例 {typical} 个月。"
            return self._pass("试用期", f"{terms.probation_months:g} 个月", required, citation)

        max_months = policy.probation.max_months
        if terms.probation_months > max_months:
            return ComplianceCheck(
                item="试用期",
                status="fail",
                requested=f"{terms.probation_months:g} 个月",
                required=f"不超过 {max_months:g} 个月",
                citation=citation,
                recommendation=f"将试用期调整为 {max_months:g} 个月以内。",
            )
        return self._pass(
            "试用期",
            f"{terms.probation_months:g} 个月",
            f"不超过 {max_months:g} 个月",
            citation,
        )

    def _check_annual_leave(self, policy: Policy, terms: HiringTerms) -> ComplianceCheck:
        citation = self._citation(policy, "annual_leave.notes", policy.annual_leave.notes)
        if terms.annual_leave_days is None:
            return self._unknown("年假", citation, "用户未提供年假天数，后续方案应给出建议值。")

        required_days = policy.annual_leave.statutory_min_days
        if terms.annual_leave_days < required_days:
            return ComplianceCheck(
                item="年假",
                status="fail",
                requested=f"{terms.annual_leave_days:g} 天",
                required=f"至少 {required_days:g} 天",
                citation=citation,
                recommendation=f"将年假调整为至少 {required_days:g} 天。",
            )
        return self._pass(
            "年假",
            f"{terms.annual_leave_days:g} 天",
            f"至少 {required_days:g} 天",
            citation,
        )

    def _check_working_hours(self, policy: Policy, terms: HiringTerms) -> ComplianceCheck:
        citation = self._citation(
            policy,
            "standard_working_hours_per_week",
            f"标准每周工作时长为 {policy.standard_working_hours_per_week} 小时。",
        )
        if terms.working_hours_per_week is None:
            return self._unknown("工作时长", citation, "用户未提供每周工作时长，后续方案应给出建议值。")

        required_hours = policy.standard_working_hours_per_week
        if terms.working_hours_per_week > required_hours:
            return ComplianceCheck(
                item="工作时长",
                status="fail",
                requested=f"每周 {terms.working_hours_per_week:g} 小时",
                required=f"不超过每周 {required_hours:g} 小时",
                citation=citation,
                recommendation=f"将标准工作时长调整为每周 {required_hours:g} 小时以内。",
            )
        return self._pass(
            "工作时长",
            f"每周 {terms.working_hours_per_week:g} 小时",
            f"不超过每周 {required_hours:g} 小时",
            citation,
        )

    def _check_termination_notice(self, policy: Policy, terms: HiringTerms) -> ComplianceCheck:
        citation = self._citation(policy, "termination_notice.notes", policy.termination_notice.notes)
        if terms.notice_days is None:
            return self._unknown("解雇通知期", citation, "用户未提供解雇通知期，后续方案应给出建议值。")

        required_days = self._default_notice_days(policy)
        if required_days is None:
            return self._unknown("解雇通知期", citation, "本地 fixture 未提供可机器解析的通知期天数。")
        if terms.notice_days < required_days:
            return ComplianceCheck(
                item="解雇通知期",
                status="fail",
                requested=f"{terms.notice_days:g} 天",
                required=f"至少 {required_days:g} 天",
                citation=citation,
                recommendation=f"将解雇通知期调整为至少 {required_days:g} 天。",
            )
        return self._pass(
            "解雇通知期",
            f"{terms.notice_days:g} 天",
            f"至少 {required_days:g} 天",
            citation,
        )

    def _check_thirteenth_month(self, policy: Policy, terms: HiringTerms) -> ComplianceCheck:
        citation = self._citation(policy, "thirteenth_month.notes", policy.thirteenth_month.notes)
        if terms.include_13th_month is None:
            return self._unknown(
                "13 薪/强制奖金",
                citation,
                "用户未说明是否发放 13 薪或强制奖金，后续方案应按当地政策推荐。",
            )

        if policy.thirteenth_month.statutory and not terms.include_13th_month:
            return ComplianceCheck(
                item="13 薪/强制奖金",
                status="fail",
                requested="不发放",
                required="必须发放",
                citation=citation,
                recommendation="将法定 13 薪或强制奖金纳入雇佣方案。",
            )
        required = "必须发放" if policy.thirteenth_month.statutory else "非法定强制"
        requested = "发放" if terms.include_13th_month else "不发放"
        return self._pass("13 薪/强制奖金", requested, required, citation)

    def _citation(self, policy: Policy, json_path: str, quote: str) -> Citation:
        return build_citation(self.policy_repository.data_dir, policy.source_path, json_path, quote)

    def _unknown(self, item: str, citation: Citation, recommendation: str) -> ComplianceCheck:
        return ComplianceCheck(
            item=item,
            status="unknown",
            requested=None,
            required=None,
            citation=citation,
            recommendation=recommendation,
        )

    def _pass(
        self,
        item: str,
        requested: str,
        required: str,
        citation: Citation,
    ) -> ComplianceCheck:
        return ComplianceCheck(
            item=item,
            status="pass",
            requested=requested,
            required=required,
            citation=citation,
            recommendation=None,
        )

    def _default_notice_days(self, policy: Policy) -> int | None:
        parsed_days = [
            days
            for rule in policy.termination_notice.rules
            if (days := self._parse_notice_days(rule.notice)) is not None
        ]
        if not parsed_days:
            return None
        return max(parsed_days)

    def _parse_notice_days(self, notice: str) -> int | None:
        match = re.search(r"(\d+)", notice)
        if match is None:
            return None
        amount = int(match.group(1))
        if "周" in notice:
            return amount * 7
        return amount

    def _format_number(self, value: float) -> str:
        if float(value).is_integer():
            return str(int(value))
        return f"{value:.2f}".rstrip("0").rstrip(".")
