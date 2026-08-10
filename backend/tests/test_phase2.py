from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["data"]["default_recommendation"] == "NO BET"


def test_auto_betting_status_hard_locked():
    response = client.get("/auto-betting/status")
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["enabled"] is False
    assert payload["hard_locked"] is True


def test_auto_betting_execute_blocked():
    response = client.post("/auto-betting/execute")
    assert response.status_code == 403
    assert "inactive and hard-locked" in response.json()["detail"]


def test_data_quality_requires_historical_odds_and_xg():
    response = client.get("/data-quality/7K4M2QF")
    assert response.status_code == 200
    payload = response.json()["data"]
    fields = {item["field"] for item in payload["checks"]}
    assert "historical_odds" in fields
    assert "xg" in fields
    assert payload["overall_status"] == "NO_BET_UNTIL_PROVIDER_DATA_VALIDATED"


def test_fixture_routes_reject_numeric_or_ambiguous_public_codes():
    for fixture_code in ("1234567", "ABCDEFG", "12O4ABC"):
        response = client.get(f"/fixtures/{fixture_code}")
        assert response.status_code == 422


def test_supported_competitions_include_eliteserien_only_code():
    response = client.get("/fixtures/upcoming")
    assert response.status_code == 200
    supported = response.json()["metadata"]["supported_competitions"]
    assert "NOR_ELITESERIEN" in supported


def test_provider_catalog_includes_requested_candidates_without_sportmonks():
    response = client.get("/providers/status")
    assert response.status_code == 200
    providers = response.json()["data"]
    assert {
        "api_football",
        "odds_api",
        "sportsdata_io",
        "soccerdata_api",
        "sports_game_odds",
        "sharpapi",
        "statsbomb",
    } <= set(providers)
    assert "sportmonks" not in providers
    assert providers["api_football"]["capabilities"]["current_odds"] is True
    assert all(providers[name]["status"] == "missing_api_key" for name in (
        "sportsdata_io",
        "soccerdata_api",
        "sports_game_odds",
        "sharpapi",
    ))
