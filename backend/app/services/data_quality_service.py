MANDATORY_DATA_FIELDS = (
    "fixtures",
    "results",
    "current_odds",
    "historical_odds",
    "xg",
    "lineups",
    "injuries_suspensions",
    "provider_timestamps",
    "provider_audit_trail",
)


def build_fixture_quality_placeholder(fixture_code: str) -> dict:
    checks = [
        {"field": field, "mandatory": True, "status": "pending_provider_integration"}
        for field in MANDATORY_DATA_FIELDS
    ]
    return {
        "fixture_code": fixture_code,
        "overall_status": "NO_BET_UNTIL_PROVIDER_DATA_VALIDATED",
        "score": 0,
        "checks": checks,
        "policy": "Historical odds and xG are mandatory. Missing mandatory data forces NO BET.",
    }
