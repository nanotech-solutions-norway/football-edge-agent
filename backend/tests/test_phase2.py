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
    response = client.get("/data-quality/1")
    assert response.status_code == 200
    payload = response.json()["data"]
    fields = {item["field"] for item in payload["checks"]}
    assert "historical_odds" in fields
    assert "xg" in fields
    assert payload["overall_status"] == "NO_BET_UNTIL_PROVIDER_DATA_VALIDATED"


def test_supported_competitions_include_eliteserien_only_code():
    response = client.get("/fixtures/upcoming")
    assert response.status_code == 200
    supported = response.json()["metadata"]["supported_competitions"]
    assert "NOR_ELITESERIEN" in supported
