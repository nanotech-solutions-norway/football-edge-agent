"""R0 validator for the FEA/PIP read-only shadow probability contract v2.

This module is not wired into live routes during R0. It provides a deterministic
consumer-side safety/contract gate so later integration cannot relax FEA's
execution posture or silently accept incompatible market payloads.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import isclose
from typing import Any

CONTRACT_VERSION = "2.0.0"
PLATFORM = "atlas_probability_intelligence_platform"
MARKET_SELECTIONS: dict[str, tuple[str, ...]] = {
    "1X2": ("home", "draw", "away"),
    "OVER_UNDER_2_5": ("over_2_5", "under_2_5"),
    "BTTS": ("yes", "no"),
}
ALLOWED_STATUS = {"ok", "degraded", "insufficient_data"}
ALLOWED_CONSENSUS_STATUS = {"comparable_consensus", "market_only", "insufficient_consensus"}
ALLOWED_AUDIT_SOURCE = {"shadow", "internal_live", "backtest", "mock"}


@dataclass(frozen=True)
class ShadowContractValidation:
    valid: bool
    errors: tuple[str, ...]


def _parse_timestamp(value: Any, field: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str):
        errors.append(f"{field}_must_be_string")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{field}_invalid_datetime")
        return None
    if parsed.tzinfo is None:
        errors.append(f"{field}_must_be_timezone_aware")
        return None
    return parsed.astimezone(timezone.utc)


def validate_shadow_payload(
    payload: Any,
    *,
    now: datetime | None = None,
    max_payload_age_seconds: int | None = None,
) -> ShadowContractValidation:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ShadowContractValidation(False, ("payload_must_be_object",))

    required = {
        "status", "contract_version", "platform", "fixture_id", "sport", "market",
        "generated_at", "probabilities", "data_quality", "safety", "audit",
    }
    missing = sorted(required - set(payload))
    if missing:
        errors.extend(f"missing_{name}" for name in missing)

    if payload.get("contract_version") != CONTRACT_VERSION:
        errors.append("contract_version_mismatch")
    if payload.get("platform") != PLATFORM:
        errors.append("platform_mismatch")
    if payload.get("sport") != "football":
        errors.append("sport_mismatch")
    if payload.get("status") not in ALLOWED_STATUS:
        errors.append("invalid_status")
    fixture_id = payload.get("fixture_id")
    if not isinstance(fixture_id, int) or isinstance(fixture_id, bool) or fixture_id < 1:
        errors.append("invalid_fixture_id")

    market = payload.get("market")
    if market not in MARKET_SELECTIONS:
        errors.append("invalid_market")
        expected_selections: set[str] = set()
    else:
        expected_selections = set(MARKET_SELECTIONS[market])

    generated_at = _parse_timestamp(payload.get("generated_at"), "generated_at", errors)
    if max_payload_age_seconds is not None:
        if max_payload_age_seconds < 0:
            errors.append("invalid_max_payload_age_seconds")
        elif generated_at is not None:
            now = now or datetime.now(timezone.utc)
            if now.tzinfo is None:
                errors.append("now_must_be_timezone_aware")
            else:
                age = (now.astimezone(timezone.utc) - generated_at).total_seconds()
                if age < 0:
                    errors.append("generated_at_in_future")
                elif age > max_payload_age_seconds:
                    errors.append("payload_stale")

    probabilities = payload.get("probabilities")
    observed_selections: set[str] = set()
    probability_values: list[float] = []
    if not isinstance(probabilities, list):
        errors.append("probabilities_must_be_array")
    else:
        for index, row in enumerate(probabilities):
            if not isinstance(row, dict):
                errors.append(f"probability_{index}_must_be_object")
                continue
            selection = row.get("selection")
            probability = row.get("probability")
            if not isinstance(selection, str):
                errors.append(f"probability_{index}_invalid_selection")
            elif selection in observed_selections:
                errors.append(f"probability_{index}_duplicate_selection")
            else:
                observed_selections.add(selection)
            if not isinstance(probability, (int, float)) or isinstance(probability, bool) or not 0 <= float(probability) <= 1:
                errors.append(f"probability_{index}_invalid_probability")
            else:
                probability_values.append(float(probability))
            fair_odds = row.get("fair_odds")
            if fair_odds is not None and (
                not isinstance(fair_odds, (int, float))
                or isinstance(fair_odds, bool)
                or float(fair_odds) <= 1
            ):
                errors.append(f"probability_{index}_invalid_fair_odds")

    data_quality = payload.get("data_quality")
    consensus_status = None
    provider_count = None
    source_count = None
    if not isinstance(data_quality, dict):
        errors.append("data_quality_must_be_object")
    else:
        score = data_quality.get("score")
        if not isinstance(score, (int, float)) or isinstance(score, bool) or not 0 <= float(score) <= 1:
            errors.append("invalid_data_quality_score")
        freshness = data_quality.get("freshness_seconds")
        if not isinstance(freshness, int) or isinstance(freshness, bool) or freshness < 0:
            errors.append("invalid_freshness_seconds")
        provider_count = data_quality.get("provider_count")
        source_count = data_quality.get("source_count")
        if not isinstance(provider_count, int) or isinstance(provider_count, bool) or provider_count < 0:
            errors.append("invalid_provider_count")
        if not isinstance(source_count, int) or isinstance(source_count, bool) or source_count < 0:
            errors.append("invalid_source_count")
        consensus_status = data_quality.get("consensus_status")
        if consensus_status not in ALLOWED_CONSENSUS_STATUS:
            errors.append("invalid_consensus_status")
        dispersion = data_quality.get("consensus_dispersion")
        if dispersion is not None and (
            not isinstance(dispersion, (int, float))
            or isinstance(dispersion, bool)
            or float(dispersion) < 0
        ):
            errors.append("invalid_consensus_dispersion")

    safety = payload.get("safety")
    if not isinstance(safety, dict):
        errors.append("safety_must_be_object")
    else:
        required_safety = {
            "manual_review_required": True,
            "execution_allowed": False,
            "recommendation_release_allowed": False,
            "bookmaker_execution_enabled": False,
        }
        for key, expected in required_safety.items():
            if safety.get(key) is not expected:
                errors.append(f"safety_violation_{key}")

    audit = payload.get("audit")
    if not isinstance(audit, dict):
        errors.append("audit_must_be_object")
    else:
        for field in ("model_version", "calibration_version", "evidence_id"):
            if not isinstance(audit.get(field), str) or not audit.get(field, "").strip():
                errors.append(f"invalid_audit_{field}")
        if audit.get("source") not in ALLOWED_AUDIT_SOURCE:
            errors.append("invalid_audit_source")

    if consensus_status == "comparable_consensus":
        if not isinstance(provider_count, int) or provider_count < 2:
            errors.append("comparable_consensus_requires_two_providers")
        if observed_selections != expected_selections:
            errors.append("comparable_consensus_requires_complete_market")
        if probability_values and not isclose(sum(probability_values), 1.0, rel_tol=0.0, abs_tol=1e-6):
            errors.append("probabilities_must_sum_to_one")
    else:
        if probabilities not in ([], None):
            errors.append("non_consensus_payload_must_not_publish_probabilities")

    return ShadowContractValidation(not errors, tuple(errors))


def quarantine_shadow_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return reporting-only enrichment while preserving FEA execution locks."""
    validation = validate_shadow_payload(payload)
    return {
        "pip_shadow_validation": {"valid": validation.valid, "errors": list(validation.errors)},
        "pip_shadow_payload": payload if validation.valid else None,
        "manual_review_required": True,
        "recommendation_release_allowed": False,
        "auto_betting_enabled": False,
        "real_money_betting_enabled": False,
        "bookmaker_execution_enabled": False,
    }
