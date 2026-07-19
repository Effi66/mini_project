from pathlib import Path

import pytest

from fastapi.testclient import TestClient

from app.domain.policy_repository import PolicyRepository
from app.main import create_app


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def test_resolves_singapore_by_code_english_name_and_chinese_name():
    repository = PolicyRepository(DATA_DIR)

    by_code = repository.get_policy("SG")
    by_name = repository.get_policy("Singapore")
    by_chinese = repository.get_policy("新加坡")

    assert by_code.country == "Singapore"
    assert by_name.country_code == "SG"
    assert by_chinese.currency == "SGD"


def test_lists_supported_countries_with_metadata():
    repository = PolicyRepository(DATA_DIR)

    countries = repository.list_countries()

    assert {country.country_code for country in countries} == {
        "ID",
        "JP",
        "PH",
        "SG",
        "VN",
    }
    assert any(country.country == "Vietnam" and country.currency == "VND" for country in countries)


def test_unsupported_country_fails_closed_with_supported_country_list():
    repository = PolicyRepository(DATA_DIR)

    with pytest.raises(ValueError) as exc_info:
        repository.get_policy("Thailand")

    message = str(exc_info.value)
    assert "Unsupported country" in message
    assert "Singapore" in message
    assert "Vietnam" in message


def test_policy_summary_contains_source_backed_citations():
    repository = PolicyRepository(DATA_DIR)

    summary = repository.get_policy_summary("Vietnam")

    probation_citation = next(
        citation for citation in summary.citations if citation.json_path == "probation.notes"
    )
    assert summary.country == "Vietnam"
    assert summary.currency == "VND"
    assert "试用期上限" in probation_citation.quote
    assert probation_citation.source_file == "data/vietnam.json"


def test_countries_api_returns_supported_country_metadata():
    app = create_app(data_dir=DATA_DIR)
    client = TestClient(app)

    response = client.get("/api/countries")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["countries"]) == 5
    assert {"country": "Singapore", "country_code": "SG", "currency": "SGD"} in payload[
        "countries"
    ]


def test_policy_api_returns_structured_policy_summary():
    app = create_app(data_dir=DATA_DIR)
    client = TestClient(app)

    response = client.get("/api/policies/SG")

    assert response.status_code == 200
    payload = response.json()
    assert payload["country"] == "Singapore"
    assert payload["country_code"] == "SG"
    assert any(citation["json_path"] == "probation.notes" for citation in payload["citations"])

