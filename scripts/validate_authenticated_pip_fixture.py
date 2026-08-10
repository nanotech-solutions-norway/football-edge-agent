#!/usr/bin/env python3
"""Validate an ephemeral authenticated PIP fixture without exposing its payload."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.app.services.pip_shadow_contract import validate_shadow_payload


def sanitized_validation_summary(
    payload: Any,
    *,
    now: datetime | None = None,
    max_payload_age_seconds: int = 900,
) -> tuple[dict[str, Any], int]:
    result = validate_shadow_payload(
        payload,
        now=now or datetime.now(timezone.utc),
        max_payload_age_seconds=max_payload_age_seconds,
    )
    data_quality = payload.get("data_quality", {}) if isinstance(payload, dict) else {}
    probabilities = payload.get("probabilities", []) if isinstance(payload, dict) else []
    consensus_status = data_quality.get("consensus_status") if isinstance(data_quality, dict) else None
    provider_count = data_quality.get("provider_count") if isinstance(data_quality, dict) else None
    comparable = consensus_status == "comparable_consensus"
    provider_gate = isinstance(provider_count, int) and not isinstance(provider_count, bool) and provider_count >= 2
    probability_count = len(probabilities) if isinstance(probabilities, list) else 0
    passed = result.valid and comparable and provider_gate and probability_count > 0
    summary = {
        "validation_status": "pass" if passed else "review",
        "contract_valid": result.valid,
        "validation_error_count": len(result.errors),
        "comparable_consensus": comparable,
        "provider_gate_passed": provider_gate,
        "provider_count": provider_count if isinstance(provider_count, int) and not isinstance(provider_count, bool) else 0,
        "probability_count": probability_count,
        "manual_review_required": True,
        "recommendation_release_allowed": False,
        "execution_allowed": False,
        "auto_betting_enabled": False,
        "real_money_betting_enabled": False,
        "bookmaker_execution_enabled": False,
        "payload_included": False,
        "fixture_id_included": False,
        "provider_names_included": False,
    }
    return summary, 0 if passed else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", type=Path, help="ephemeral PIP v2 fixture JSON")
    parser.add_argument("--max-age-seconds", type=int, default=900)
    args = parser.parse_args()
    try:
        payload = json.loads(args.payload.read_text(encoding="utf-8-sig"))
        summary, exit_code = sanitized_validation_summary(
            payload,
            max_payload_age_seconds=args.max_age_seconds,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        summary = {
            "validation_status": "review",
            "contract_valid": False,
            "validation_error_count": 1,
            "comparable_consensus": False,
            "provider_gate_passed": False,
            "provider_count": 0,
            "probability_count": 0,
            "manual_review_required": True,
            "recommendation_release_allowed": False,
            "execution_allowed": False,
            "auto_betting_enabled": False,
            "real_money_betting_enabled": False,
            "bookmaker_execution_enabled": False,
            "payload_included": False,
            "fixture_id_included": False,
            "provider_names_included": False,
        }
        exit_code = 2
    print(json.dumps(summary, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
