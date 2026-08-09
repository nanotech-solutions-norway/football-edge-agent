#!/usr/bin/env python3
"""Offline FEA R0 validator for a local PIP v2 shadow payload.

The script performs no network calls and exposes no execution path. It is the
consumer-side handoff tool for the external-data closure gate.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from backend.app.services.pip_shadow_contract import validate_shadow_payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", type=Path, help="local PIP v2 shadow payload JSON")
    parser.add_argument("--max-age-seconds", type=int, default=None)
    parser.add_argument("--require-consensus", action="store_true")
    args = parser.parse_args()

    payload = json.loads(args.payload.read_text(encoding="utf-8-sig"))
    result = validate_shadow_payload(
        payload,
        now=datetime.now(timezone.utc),
        max_payload_age_seconds=args.max_age_seconds,
    )
    summary = {
        "valid": result.valid,
        "errors": list(result.errors),
        "consensus_status": payload.get("data_quality", {}).get("consensus_status") if isinstance(payload, dict) else None,
        "manual_review_required": True,
        "recommendation_release_allowed": False,
        "execution_allowed": False,
        "bookmaker_execution_enabled": False,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not result.valid:
        return 2
    if args.require_consensus and summary["consensus_status"] != "comparable_consensus":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
