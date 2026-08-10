import json
from datetime import datetime, timezone

from scripts.validate_authenticated_pip_fixture import sanitized_validation_summary


NOW = datetime(2026, 8, 10, 0, 0, tzinfo=timezone.utc)


def valid_payload():
    return {
        "status": "ok",
        "contract_version": "2.0.0",
        "platform": "atlas_probability_intelligence_platform",
        "fixture_code": "7K4M2QF",
        "sport": "football",
        "market": "1X2",
        "generated_at": "2026-08-10T00:00:00Z",
        "probabilities": [
            {"selection": "home", "probability": 0.5, "fair_odds": 2.0},
            {"selection": "draw", "probability": 0.25, "fair_odds": 4.0},
            {"selection": "away", "probability": 0.25, "fair_odds": 4.0},
        ],
        "data_quality": {
            "score": 0.9,
            "freshness_seconds": 0,
            "provider_count": 2,
            "source_count": 2,
            "consensus_status": "comparable_consensus",
            "consensus_dispersion": 0.01,
        },
        "safety": {
            "manual_review_required": True,
            "execution_allowed": False,
            "recommendation_release_allowed": False,
            "bookmaker_execution_enabled": False,
        },
        "audit": {
            "model_version": "shadow",
            "calibration_version": "shadow",
            "evidence_id": "ephemeral",
            "source": "shadow",
        },
    }


def test_valid_consensus_returns_only_sanitized_summary():
    payload = valid_payload()
    summary, exit_code = sanitized_validation_summary(payload, now=NOW)
    rendered = json.dumps(summary)
    assert exit_code == 0
    assert summary["validation_status"] == "pass"
    assert summary["provider_count"] == 2
    assert summary["probability_count"] == 3
    assert summary["payload_included"] is False
    assert payload["fixture_code"] not in rendered
    assert payload["audit"]["evidence_id"] not in rendered


def test_single_provider_fails_closed_without_error_details():
    payload = valid_payload()
    payload["data_quality"]["provider_count"] = 1
    summary, exit_code = sanitized_validation_summary(payload, now=NOW)
    assert exit_code == 2
    assert summary["validation_status"] == "review"
    assert summary["contract_valid"] is False
    assert summary["validation_error_count"] > 0
    assert "errors" not in summary
    assert summary["execution_allowed"] is False


def test_execution_enabled_payload_fails_closed():
    payload = valid_payload()
    payload["safety"]["execution_allowed"] = True
    summary, exit_code = sanitized_validation_summary(payload, now=NOW)
    assert exit_code == 2
    assert summary["contract_valid"] is False
    assert summary["execution_allowed"] is False
