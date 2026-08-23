from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_phase3_model_status_endpoint():
    response = client.get("/model/status")
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["phase"] == 3
    assert payload["default_recommendation"] == "NO BET"
    assert payload["auto_betting_hard_locked"] is True


def test_phase3_probability_endpoint():
    response = client.post(
        "/probabilities/calculate",
        json={
            "market": "1X2",
            "odds_by_selection": {"home": 2.0, "draw": 3.4, "away": 4.0},
            "home_expected_goals": 1.55,
            "away_expected_goals": 1.10,
            "home_elo_rating": 1520,
            "away_elo_rating": 1480,
            "xg_available": True,
            "historical_odds_available": True,
        },
    )
    assert response.status_code == 200
    rows = response.json()["data"]
    assert len(rows) == 3
    assert round(sum(row["model_probability"] for row in rows), 6) == 1.0


def test_phase3_probability_endpoint_blocks_missing_xg():
    response = client.post(
        "/probabilities/calculate",
        json={
            "market": "BTTS",
            "odds_by_selection": {"yes": 1.9, "no": 1.95},
            "home_expected_goals": 1.55,
            "away_expected_goals": 1.10,
            "xg_available": False,
            "historical_odds_available": True,
        },
    )
    assert response.status_code == 422
    assert "xG" in response.json()["detail"]


def test_phase3_recommendation_endpoint_contains_governance_fields():
    response = client.post(
        "/recommendations/fixture/direct",
        json={
            "fixture_id": 1,
            "market": "1X2",
            "selection": "home",
            "decimal_odds": 2.1,
            "model_probability": 0.54,
            "bookie_probability": 0.49,
            "data_quality_score": 90,
            "xg_available": True,
            "historical_odds_available": True,
            "odds_fresh": True,
        },
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["recommendation"] in {"BET", "WATCHLIST", "NO BET"}
    assert payload["comparison_chart"]["delta"] == round(payload["edge"], 6)
    assert payload["audit_trail"]["auto_betting_hard_locked"] is True
