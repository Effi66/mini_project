import json
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter

from app.core.errors import UnsupportedCountryError
from app.domain.citations import build_citation
from app.models.policy import CountryMetadata, Policy, PolicySummary


COUNTRY_ALIASES = {
    "singapore": "SG",
    "sg": "SG",
    "新加坡": "SG",
    "vietnam": "VN",
    "viet nam": "VN",
    "vn": "VN",
    "越南": "VN",
    "indonesia": "ID",
    "id": "ID",
    "印尼": "ID",
    "印度尼西亚": "ID",
    "philippines": "PH",
    "ph": "PH",
    "菲律宾": "PH",
    "japan": "JP",
    "jp": "JP",
    "日本": "JP",
}


class PolicyRepository:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self._policies = self._load_policies(data_dir)

    def list_countries(self) -> list[CountryMetadata]:
        countries = [
            CountryMetadata(
                country=policy.country,
                country_code=policy.country_code,
                currency=policy.currency,
            )
            for policy in self._policies.values()
        ]
        return sorted(countries, key=lambda country: country.country_code)

    def get_policy(self, country: str) -> Policy:
        country_code = self._resolve_country_code(country)
        return self._policies[country_code]

    def get_policy_summary(self, country: str) -> PolicySummary:
        policy = self.get_policy(country)
        citations = [
            build_citation(self.data_dir, policy.source_path, "probation.notes", policy.probation.notes),
            build_citation(
                self.data_dir,
                policy.source_path,
                "annual_leave.notes",
                policy.annual_leave.notes,
            ),
            build_citation(
                self.data_dir,
                policy.source_path,
                "termination_notice.notes",
                policy.termination_notice.notes,
            ),
            build_citation(
                self.data_dir,
                policy.source_path,
                "minimum_wage.notes",
                policy.minimum_wage.notes,
            ),
            build_citation(
                self.data_dir,
                policy.source_path,
                "thirteenth_month.notes",
                policy.thirteenth_month.notes,
            ),
        ]
        return PolicySummary(
            country=policy.country,
            country_code=policy.country_code,
            currency=policy.currency,
            employer_contributions=[item.name for item in policy.employer_contributions],
            annual_leave_min_days=policy.annual_leave.statutory_min_days,
            probation_notes=policy.probation.notes,
            termination_notice_notes=policy.termination_notice.notes,
            citations=citations,
        )

    def _resolve_country_code(self, country: str) -> str:
        normalized = country.strip().casefold()
        country_code = COUNTRY_ALIASES.get(normalized)
        if country_code and country_code in self._policies:
            return country_code

        supported = ", ".join(policy.country for policy in self._policies.values())
        raise UnsupportedCountryError(f"Unsupported country '{country}'. Supported countries: {supported}")

    def _load_policies(self, data_dir: Path) -> dict[str, Policy]:
        adapter = TypeAdapter(dict[str, Any])
        policies: dict[str, Policy] = {}
        for file_path in sorted(data_dir.glob("*.json")):
            raw = adapter.validate_python(json.loads(file_path.read_text(encoding="utf-8")))
            policy = Policy.model_validate({**raw, "source_path": file_path})
            policies[policy.country_code] = policy
        return policies

