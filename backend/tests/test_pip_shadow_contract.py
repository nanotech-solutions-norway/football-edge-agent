from datetime import datetime, timedelta, timezone

from backend.app.services.pip_shadow_contract import quarantine_shadow_payload, validate_shadow_payload


NOW = datetime(2026, 8, 8, 20, 0, tzinfo=timezone.utc)


def valid_payload():
    return {
        "status": "ok",
        "contract_version": "2.0.0",
        "platform": "atlas_probability_intelligence_platform",
        "fixture_code": "7K4M2QF",
        "sport": "football",
        "market": "1X2",
        "generated_at": (NOW - timedelta(seconds=15)).isoformat(),
        "probabilities": [
            {"selection": "home", "probability": 0.50, "fair_odds": 2.0},
            {"selection": "draw", "probability": 0.25, "fair_odds": 4.0},
            {"selection": "away", "probability": 0.25, "fair_odds": 4.0},
        ],
        "data_quality": {
            "score": 0.91,
            "freshness_seconds": 15,
            "provider_count": 2,
            "source_count": 2,
            "consensus_status": "comparable_consensus",
            "consensus_dispersion": 0.02,
        },
        "safety": {
            "manual_review_required": True,
            "execution_allowed": False,
            "recommendation_release_allowed": False,
            "bookmaker_execution_enabled": False,
        },
        "audit": {
            "model_version": "r0-shadow-model",
            "calibration_version": "r0-calibration",
            "source": "shadow",
            "evidence_id": "r0-test-123",
        },
    }


def test_valid_comparable_payload_passes():
    result = validate_shadow_payload(valid_payload(), now=NOW, max_payload_age_seconds=60)
    assert result.valid is True
    assert result.errors == ()


def test_execution_true_is_hard_contract_failure():
    payload = valid_payload()
    payload["safety"]["execution_allowed"] = True
    result = validate_shadow_payload(payload)
    assert result.valid is False
    assert "safety_violation_execution_allowed" in result.errors


def test_numeric_or_ambiguous_fixture_code_is_rejected():
    for fixture_code in (1234567, "1234567", "ABCDEFG", "12O4ABC"):
        payload = valid_payload()
        payload["fixture_code"] = fixture_code
        result = validate_shadow_payload(payload)
        assert result.valid is False
        assert "invalid_fixture_code" in result.errors


def test_recommendation_release_true_is_hard_contract_failure():
    payload = valid_payload()
    payload["safety"]["recommendation_release_allowed"] = True
    result = validate_shadow_payload(payload)
    assert result.valid is False
    assert "safety_violation_recommendation_release_allowed" in result.errors


def test_single_provider_cannot_claim_comparable_consensus():
    payload = valid_payload()
    payload["data_quality"]["provider_count"] = 1
    result = validate_shadow_payload(payload)
    assert result.valid is False
    assert "comparable_consensus_requires_two_providers" in result.errors


def test_non_consensus_must_not_publish_probability_array():
    payload = valid_payload()
    payload["status"] = "degraded"
    payload["data_quality"]["provider_count"] = 1
    payload["data_quality"]["consensus_status"] = "market_only"
    result = validate_shadow_payload(payload)
    assert result.valid is False
    assert "non_consensus_payload_must_not_publish_probabilities" in result.errors


def test_non_consensus_with_empty_probabilities_is_valid_reporting_object():
    payload = valid_payload()
    payload["status"] = "insufficient_data"
    payload["probabilities"] = []
    payload["data_quality"]["provider_count"] = 1
    payload["data_quality"]["source_count"] = 1
    payload["data_quality"]["consensus_status"] = "market_only"
    payload["data_quality"]["consensus_dispersion"] = None
    result = validate_shadow_payload(payload)
    assert result.valid is True


def test_stale_payload_is_rejected_when_age_gate_enabled():
    payload = valid_payload()
    payload["generated_at"] = (NOW - timedelta(minutes=30)).isoformat()
    result = validate_shadow_payload(payload, now=NOW, max_payload_age_seconds=60)
    assert result.valid is False
    assert "payload_stale" in result.errors


def test_wrong_market_selection_taxonomy_is_rejected():
    payload = valid_payload()
    payload["probabilities"][1]["selection"] = "over"
    result = validate_shadow_payload(payload)
    assert result.valid is False
    assert "comparable_consensus_requires_complete_market" in result.errors


def test_probability_sum_must_be_one_for_consensus():
    payload = valid_payload()
    payload["probabilities"][0]["probability"] = 0.60
    result = validate_shadow_payload(payload)
    assert result.valid is False
    assert "probabilities_must_sum_to_one" in result.errors


def test_quarantine_never_enables_execution_or_release():
    enriched = quarantine_shadow_payload(valid_payload())
    assert enriched["pip_shadow_validation"]["valid"] is True
    assert enriched["manual_review_required"] is True
    assert enriched["recommendation_release_allowed"] is False
    assert enriched["auto_betting_enabled"] is False
    assert enriched["real_money_betting_enabled"] is False
    assert enriched["bookmaker_execution_enabled"] is False
