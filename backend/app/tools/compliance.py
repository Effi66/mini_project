from pathlib import Path

from app.domain.compliance_checker import ComplianceChecker
from app.domain.policy_repository import PolicyRepository
from app.models.request import HiringTerms


def check_compliance(data_dir: Path, country: str, terms: dict) -> dict:
    checker = ComplianceChecker(PolicyRepository(data_dir))
    return checker.check(country, HiringTerms.model_validate(terms)).model_dump()

