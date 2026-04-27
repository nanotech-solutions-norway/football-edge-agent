from backend.app.models.phase3_probability_engine import (
    ALLOWED_RECOMMENDATIONS,
    brier_score,
    bookmaker_margin,
    build_recommendation_payload,
    calculate_expected_value,
    decimal_odds_to_implied_probability,
    elo_three_way_proxy,
    generate_market_probabilities,
    no_vig_probabilities,
    poisson_market_probabilities,
    recommendation_decision,
)


def test_market_implied_and_no_vig_probabilities_sum_to_one():
    raw = {
        "home": decimal_odds_to_implied_probability(2.0),
        "draw": decimal_odds_to_implied_probability(3.4),
        "away": decimal_odds_to_implied_probability(4.0),
    }
    assert bookmaker_margin(raw) > 0
    no_vig = no_vig_probabilities(raw)
    assert round(sum(no_vig.values()), 6) == 1.0


def test_poisson_probabilities_are_normalized_for_supported_markets():
    for market in ["1X2", "OVER_UNDER_2_5", "BTTS"]:
        probs = poisson_market_probabilities(market, 1.55, 1.10)
        assert round(sum(probs.values()), 6) == 1.0


def test_elo_proxy_is_normalized():
    probs = elo_three_way_proxy(1520, 1480)
    assert round(sum(probs.values()), 6) == 1.0


def test_probability_generation_requires_xg_and_historical_odds():
    try:
        generate_market_probabilities(
            market="1X2",
            odds_by_selection={"home": 2.0, "draw": 3.4, "away": 4.0},
            home_expected_goals=1.55,
            away_expected_goals=1.10,
            xg_available=False,
            historical_odds_available=True,
        )
    except ValueError as exc:
        assert "xG" in str(exc)
    else:
        raise AssertionError("Missing xG must block probability generation.")

    try:
        generate_market_probabilities(
            market="BTTS",
            odds_by_selection={"yes": 1.90, "no": 1.95},
            home_expected_goals=1.55,
            away_expected_goals=1.10,
            xg_available=True,
            historical_odds_available=False,
        )
    except ValueError as exc:
        assert "historical odds" in str(exc)
    else:
        raise AssertionError("Missing historical odds must block probability generation.")


def test_probability_generation_outputs_all_required_fields():
    rows = generate_market_probabilities(
        market="1X2",
        odds_by_selection={"home": 2.0, "draw": 3.4, "away": 4.0},
        home_expected_goals=1.55,
        away_expected_goals=1.10,
        home_elo_rating=1520,
        away_elo_rating=1480,
    )
    assert [row["selection"] for row in rows] == ["home", "draw", "away"]
    assert round(sum(row["model_probability"] for row in rows), 6) == 1.0
    assert round(sum(row["bookie_probability"] for row in rows), 6) == 1.0
    for row in rows:
        for key in [
            "model_probability",
            "bookie_probability",
            "edge",
            "expected_value",
            "fair_odds",
            "bookmaker_margin",
        ]:
            assert key in row


def test_recommendation_outputs_are_governed():
    decision = recommendation_decision(
        edge=0.08,
        expected_value=0.05,
        data_quality_score=95,
        xg_available=True,
        historical_odds_available=True,
        odds_fresh=True,
        model_market_disagreement=0.08,
    )
    assert decision["recommendation"] in ALLOWED_RECOMMENDATIONS

    no_bet = recommendation_decision(
        edge=0.08,
        expected_value=0.05,
        data_quality_score=95,
        xg_available=False,
        historical_odds_available=True,
        odds_fresh=True,
        model_market_disagreement=0.08,
    )
    assert no_bet["recommendation"] == "NO BET"


def test_recommendation_payload_contains_chart_risk_and_audit_trail():
    payload = build_recommendation_payload(
        fixture_id=1,
        market="1X2",
        selection="home",
        decimal_odds=2.10,
        model_probability=0.54,
        bookie_probability=0.49,
        data_quality_score=90,
        xg_available=True,
        historical_odds_available=True,
    )
    assert payload["recommendation"] in {"BET", "WATCHLIST", "NO BET"}
    assert payload["comparison_chart"]["type"] == "model_vs_bookie_probability_comparison"
    assert payload["risk"] in {"LOW", "MEDIUM", "HIGH"}
    assert payload["audit_trail"]["auto_betting_hard_locked"] is True
    assert payload["audit_trail"]["auto_betting_enabled"] is False


def test_auto_betting_cannot_be_enabled():
    try:
        recommendation_decision(
            edge=0.08,
            expected_value=0.05,
            data_quality_score=95,
            xg_available=True,
            historical_odds_available=True,
            odds_fresh=True,
            model_market_disagreement=0.08,
            auto_betting_enabled=True,
        )
    except ValueError as exc:
        assert "Auto-betting" in str(exc)
    else:
        raise AssertionError("Auto-betting must remain hard-locked.")


def test_metrics_helpers():
    assert calculate_expected_value(0.55, 2.0) > 0
    assert brier_score(0.7, 1) < brier_score(0.2, 1)
