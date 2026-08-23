"""Static Phase 3 validation guardrail.

This script is intentionally simple and CI-friendly. It verifies that the
Phase 3 package preserves mandatory governance constraints.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "backend/app/models/phase3_probability_engine.py",
    "backend/app/api/phase3.py",
    "backend/app/db/migrations/003_model_probability_engine.sql",
    "backend/tests/test_phase3_probability_engine.py",
    "backend/tests/test_phase3_api.py",
    "docs/phase3_model_probability_engine.md",
]

REQUIRED_TERMS = [
    "NO BET",
    "historical odds",
    "xG",
    "auto_betting_hard_locked",
    "BET",
    "WATCHLIST",
]


def main() -> int:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        raise SystemExit(f"Missing Phase 3 files: {missing}")

    combined = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in REQUIRED_FILES)
    missing_terms = [term for term in REQUIRED_TERMS if term not in combined]
    if missing_terms:
        raise SystemExit(f"Missing mandatory Phase 3 governance terms: {missing_terms}")

    forbidden = ["sure-win", "banker", "guaranteed pick", "loss chasing"]
    forbidden_found = [term for term in forbidden if term in combined.lower()]
    if forbidden_found:
        raise SystemExit(f"Forbidden betting language found: {forbidden_found}")

    print("Phase 3 static validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
