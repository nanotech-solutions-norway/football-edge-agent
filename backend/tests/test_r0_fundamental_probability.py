from datetime import datetime, timezone

import pytest

from backend.app.models.r0_fundamental_probability import (
    assert_chronological_split,
    compare_fundamental_to_market,
    derive_expected_goals,
    exponential_decay_weights,
    fundamental_market_probabilities,
    multiclass_brier_score,
    multiclass_log_loss,
    no_vig_market_probabilities,
    time_decayed_average,
)


def test_decay_weights_prioritize_recent_match():
    weights = exponential_decay_weights(4, half_life_matches=2.0)
    assert sum(weights) == pytest.approx(1.0)
    assert weights[-1] > weights[0]


def test_time_decayed_xg_responds_more_to_recent_values():
    older_high = time_decayed_average([3.0, 0.5, 0.5, 0.5], half_life_matches=2.0)
    recent_high = time_decayed_average([0.5, 0.5, 0.5, 3.0], half_life_matches=2.0)
    assert recent_high > older_high


def test_expected_goals_uses_only_xg_histories():
    home, away = derive_expected_goals(
        home_xg_for=[1.2, 1.4, 1.6],
        home_xg_against=[0.8, 1.0, 0.9],
        away_xg_for=[1.0, 1.1, 1.3],
        away_xg_against=[1.3, 1.4, 1.2],
    )
    assert home > 0
    assert away > 0


@pytest.mark.parametrize("market", ["1X2", "OVER_UNDER_2_5", "BTTS"])
def test_fundamental_probabilities_sum_to_one(market):
    result = fundamental_market_probabilities(
        market,
        home_expected_goals=1.7,
        away_expected_goals=1.1,
    )
    assert sum(result.values()) == pytest.approx(1.0, abs=1e-12)


def test_market_probability_is_separate_comparison_baseline():
    model = fundamental_market_probabilities("1X2", home_expected_goals=1.7, away_expected_goals=1.1)
    market = no_vig_market_probabilities({"home": 2.05, "draw": 3.5, "away": 4.0})
    comparison = compare_fundamental_to_market(model, market)
    assert comparison["home"]["model_probability"] == pytest.approx(model["home"])
    assert comparison["home"]["market_probability"] == pytest.approx(market["home"])
    assert comparison["home"]["probability_delta"] == pytest.approx(model["home"] - market["home"])


def test_multiclass_scores_reward_correct_high_probability():
    good = {"home": 0.8, "draw": 0.1, "away": 0.1}
    poor = {"home": 0.2, "draw": 0.4, "away": 0.4}
    assert multiclass_brier_score(good, "home") < multiclass_brier_score(poor, "home")
    assert multiclass_log_loss(good, "home") < multiclass_log_loss(poor, "home")


def test_chronological_split_accepts_strict_order():
    utc = timezone.utc
    assert_chronological_split(
        [datetime(2025, 1, 1, tzinfo=utc), datetime(2025, 6, 1, tzinfo=utc)],
        [datetime(2025, 7, 1, tzinfo=utc), datetime(2025, 8, 1, tzinfo=utc)],
        [datetime(2025, 9, 1, tzinfo=utc), datetime(2025, 10, 1, tzinfo=utc)],
    )


def test_chronological_split_rejects_temporal_overlap():
    utc = timezone.utc
    with pytest.raises(ValueError):
        assert_chronological_split(
            [datetime(2025, 1, 1, tzinfo=utc), datetime(2025, 8, 1, tzinfo=utc)],
            [datetime(2025, 7, 1, tzinfo=utc)],
            [datetime(2025, 9, 1, tzinfo=utc)],
        )


def test_research_module_contains_no_recommendation_function():
    import backend.app.models.r0_fundamental_probability as model

    names = set(dir(model))
    assert "recommendation_decision" not in names
    assert "build_recommendation_payload" not in names
