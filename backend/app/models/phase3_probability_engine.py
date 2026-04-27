"""Phase 3 baseline probability engine.

This module is intentionally deterministic and provider-agnostic. It implements
the model scaffold required before live provider ingestion is enabled. All
incomplete mandatory-data cases must resolve to NO BET.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import exp, factorial, log
from typing import Iterable, Mapping

MODEL_NAME = "football_edge_baseline_probability_engine"
MODEL_VERSION = "0.3.0-phase3"

SUPPORTED_MARKETS: dict[str, tuple[str, ...]] = {
    "1X2": ("home", "draw", "away"),
    "OVER_UNDER_2_5": ("over_2_5", "under_2_5"),
    "BTTS": ("yes", "no"),
}
ALLOWED_RECOMMENDATIONS = {"BET", "WATCHLIST", "NO BET"}


@dataclass(frozen=True)
class RecommendationThresholds:
    min_edge_bet: float = 0.050
    min_edge_watchlist: float = 0.020
    min_ev_bet: float = 0.030
    min_ev_watchlist: float = 0.010
    min_data_quality_bet: int = 85
    min_data_quality_watchlist: int = 75
    max_model_market_disagreement: float = 0.120


def decimal_odds_to_implied_probability(decimal_odds: float) -> float:
    if decimal_odds <= 1.0:
        raise ValueError("Decimal odds must be greater than 1.0.")
    return 1.0 / decimal_odds


def market_implied_probabilities(odds_by_selection: Mapping[str, float]) -> dict[str, float]:
    if not odds_by_selection:
        raise ValueError("At least one selection price is required.")
    return {selection: decimal_odds_to_implied_probability(odds) for selection, odds in odds_by_selection.items()}


def bookmaker_margin(raw_probabilities: Mapping[str, float]) -> float:
    total = sum(raw_probabilities.values())
    if total <= 0:
        raise ValueError("Raw implied probabilities must sum above zero.")
    return total - 1.0


def no_vig_probabilities(raw_probabilities: Mapping[str, float]) -> dict[str, float]:
    total = sum(raw_probabilities.values())
    if total <= 0:
        raise ValueError("Raw implied probabilities must sum above zero.")
    return {selection: probability / total for selection, probability in raw_probabilities.items()}


def expected_score(rating_a: float, rating_b: float) -> float:
    return 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0))


def update_elo_rating(rating: float, expected: float, actual: float, k_factor: float = 20.0) -> float:
    if not 0 <= expected <= 1 or not 0 <= actual <= 1:
        raise ValueError("Expected and actual scores must be in [0, 1].")
    return rating + k_factor * (actual - expected)


def elo_three_way_proxy(home_elo: float, away_elo: float, draw_rate: float = 0.26) -> dict[str, float]:
    if not 0 <= draw_rate < 1:
        raise ValueError("Draw rate must be in [0, 1).")
    home_binary = expected_score(home_elo, away_elo)
    non_draw = 1.0 - draw_rate
    return {
        "home": home_binary * non_draw,
        "draw": draw_rate,
        "away": (1.0 - home_binary) * non_draw,
    }


def glicko_placeholder_rating(rating: float = 1500.0, rating_deviation: float = 350.0, volatility: float = 0.06) -> dict[str, float]:
    """Return a Phase 3 scaffold object for future Glicko-2 integration."""
    return {"rating": rating, "rating_deviation": rating_deviation, "volatility": volatility}


def rolling_average(values: Iterable[float], window: int = 5) -> float:
    values = list(values)[-window:]
    if not values:
        raise ValueError("xG history is mandatory and cannot be empty.")
    if any(value < 0 for value in values):
        raise ValueError("xG values cannot be negative.")
    return sum(values) / len(values)


def derive_expected_goals(home_xg_for: Iterable[float], home_xg_against: Iterable[float], away_xg_for: Iterable[float], away_xg_against: Iterable[float]) -> tuple[float, float]:
    """Derive simple expected-goals inputs from rolling xG for/against histories."""
    home_attack = rolling_average(home_xg_for)
    away_defence_allowed = rolling_average(away_xg_against)
    away_attack = rolling_average(away_xg_for)
    home_defence_allowed = rolling_average(home_xg_against)
    return ((home_attack + away_defence_allowed) / 2.0, (away_attack + home_defence_allowed) / 2.0)


def _poisson_pmf(lam: float, goals: int) -> float:
    if lam < 0:
        raise ValueError("Expected goals cannot be negative.")
    return (exp(-lam) * lam**goals) / factorial(goals)


def poisson_scoreline_matrix(home_expected_goals: float, away_expected_goals: float, max_goals: int = 10) -> dict[tuple[int, int], float]:
    if home_expected_goals < 0 or away_expected_goals < 0:
        raise ValueError("Expected goals cannot be negative.")
    matrix: dict[tuple[int, int], float] = {}
    for home_goals in range(max_goals + 1):
        for away_goals in range(max_goals + 1):
            matrix[(home_goals, away_goals)] = _poisson_pmf(home_expected_goals, home_goals) * _poisson_pmf(away_expected_goals, away_goals)
    total = sum(matrix.values())
    if total <= 0:
        raise ValueError("Poisson scoreline matrix failed to normalize.")
    return {score: probability / total for score, probability in matrix.items()}


def poisson_market_probabilities(market: str, home_expected_goals: float, away_expected_goals: float) -> dict[str, float]:
    if market not in SUPPORTED_MARKETS:
        raise ValueError(f"Unsupported market: {market}")
    matrix = poisson_scoreline_matrix(home_expected_goals, away_expected_goals)

    if market == "1X2":
        raw = {
            "home": sum(prob for (home, away), prob in matrix.items() if home > away),
            "draw": sum(prob for (home, away), prob in matrix.items() if home == away),
            "away": sum(prob for (home, away), prob in matrix.items() if home < away),
        }
    elif market == "OVER_UNDER_2_5":
        raw = {
            "over_2_5": sum(prob for (home, away), prob in matrix.items() if home + away > 2.5),
            "under_2_5": sum(prob for (home, away), prob in matrix.items() if home + away < 2.5),
        }
    else:
        raw = {
            "yes": sum(prob for (home, away), prob in matrix.items() if home > 0 and away > 0),
            "no": sum(prob for (home, away), prob in matrix.items() if home == 0 or away == 0),
        }

    return no_vig_probabilities(raw)


def weighted_probability_blend(probability_sets: list[Mapping[str, float]], weights: list[float]) -> dict[str, float]:
    if len(probability_sets) != len(weights) or not probability_sets:
        raise ValueError("Probability sets and weights must be non-empty and aligned.")
    if any(weight < 0 for weight in weights) or sum(weights) <= 0:
        raise ValueError("Weights must be non-negative and sum above zero.")
    normalized_weights = [weight / sum(weights) for weight in weights]
    selections = set(probability_sets[0].keys())
    if any(set(probability_set.keys()) != selections for probability_set in probability_sets):
        raise ValueError("All probability sets must contain identical selections.")
    blended = {
        selection: sum(probability_set[selection] * weight for probability_set, weight in zip(probability_sets, normalized_weights))
        for selection in selections
    }
    return no_vig_probabilities(blended)


def calculate_expected_value(model_probability: float, decimal_odds: float) -> float:
    if not 0 <= model_probability <= 1:
        raise ValueError("Model probability must be in [0, 1].")
    if decimal_odds <= 1:
        raise ValueError("Decimal odds must be greater than 1.0.")
    return (model_probability * decimal_odds) - 1.0


def calculate_edge(model_probability: float, bookie_probability: float) -> float:
    if not 0 <= model_probability <= 1 or not 0 <= bookie_probability <= 1:
        raise ValueError("Probabilities must be in [0, 1].")
    return model_probability - bookie_probability


def fair_odds(model_probability: float) -> float:
    if model_probability <= 0:
        return float("inf")
    if model_probability > 1:
        raise ValueError("Model probability cannot exceed 1.")
    return 1.0 / model_probability


def minimum_acceptable_odds(model_probability: float, required_ev: float = 0.0) -> float:
    if model_probability <= 0:
        return float("inf")
    if required_ev < -1:
        raise ValueError("Required expected value cannot be lower than -1.")
    return (1.0 + required_ev) / model_probability


def brier_score(predicted_probability: float, actual_outcome: int) -> float:
    if not 0 <= predicted_probability <= 1 or actual_outcome not in {0, 1}:
        raise ValueError("Brier score expects probability in [0, 1] and binary actual outcome.")
    return (predicted_probability - actual_outcome) ** 2


def log_loss(predicted_probability: float, actual_outcome: int, epsilon: float = 1e-15) -> float:
    if actual_outcome not in {0, 1}:
        raise ValueError("Log loss expects binary actual outcome.")
    p = min(max(predicted_probability, epsilon), 1.0 - epsilon)
    return -(actual_outcome * log(p) + (1 - actual_outcome) * log(1 - p))


def calibration_summary(rows: Iterable[Mapping[str, float]]) -> dict[str, float | int]:
    rows = list(rows)
    if not rows:
        return {"count": 0, "mean_brier_score": 0.0, "mean_log_loss": 0.0}
    return {
        "count": len(rows),
        "mean_brier_score": sum(brier_score(float(row["predicted_probability"]), int(row["actual_outcome"])) for row in rows) / len(rows),
        "mean_log_loss": sum(log_loss(float(row["predicted_probability"]), int(row["actual_outcome"])) for row in rows) / len(rows),
    }


def _validate_market_input(market: str, odds_by_selection: Mapping[str, float]) -> None:
    if market not in SUPPORTED_MARKETS:
        raise ValueError(f"Unsupported market: {market}")
    expected = set(SUPPORTED_MARKETS[market])
    actual = set(odds_by_selection)
    if actual != expected:
        raise ValueError(f"Market {market} requires selections {sorted(expected)}; got {sorted(actual)}.")


def generate_market_probabilities(
    *,
    market: str,
    odds_by_selection: Mapping[str, float],
    home_expected_goals: float,
    away_expected_goals: float,
    home_elo_rating: float = 1500.0,
    away_elo_rating: float = 1500.0,
    xg_available: bool = True,
    historical_odds_available: bool = True,
) -> list[dict[str, float | str]]:
    if not xg_available:
        raise ValueError("Mandatory xG data unavailable; probability generation must force NO BET.")
    if not historical_odds_available:
        raise ValueError("Mandatory historical odds unavailable; probability generation must force NO BET.")
    _validate_market_input(market, odds_by_selection)

    raw_market = market_implied_probabilities(odds_by_selection)
    no_vig = no_vig_probabilities(raw_market)
    margin = bookmaker_margin(raw_market)
    poisson = poisson_market_probabilities(market, home_expected_goals, away_expected_goals)

    if market == "1X2":
        elo = elo_three_way_proxy(home_elo_rating, away_elo_rating)
        model = weighted_probability_blend([poisson, no_vig, elo], [0.45, 0.35, 0.20])
    else:
        model = weighted_probability_blend([poisson, no_vig], [0.60, 0.40])

    return [
        {
            "model_version": MODEL_VERSION,
            "market": market,
            "selection": selection,
            "decimal_odds": float(odds_by_selection[selection]),
            "model_probability": model[selection],
            "bookie_probability": no_vig[selection],
            "market_probability_raw": raw_market[selection],
            "market_probability_no_vig": no_vig[selection],
            "bookmaker_margin": margin,
            "edge": calculate_edge(model[selection], no_vig[selection]),
            "expected_value": calculate_expected_value(model[selection], float(odds_by_selection[selection])),
            "fair_odds": fair_odds(model[selection]),
        }
        for selection in SUPPORTED_MARKETS[market]
    ]


def recommendation_decision(
    *,
    edge: float,
    expected_value: float,
    data_quality_score: int,
    xg_available: bool,
    historical_odds_available: bool,
    odds_fresh: bool,
    model_market_disagreement: float,
    auto_betting_enabled: bool = False,
    thresholds: RecommendationThresholds | None = None,
) -> dict[str, str | list[str]]:
    thresholds = thresholds or RecommendationThresholds()
    if auto_betting_enabled:
        raise ValueError("Auto-betting must remain inactive and hard-locked.")

    hard_fail_reasons: list[str] = []
    if not xg_available:
        hard_fail_reasons.append("Mandatory xG data unavailable.")
    if not historical_odds_available:
        hard_fail_reasons.append("Mandatory historical odds unavailable.")
    if not odds_fresh:
        hard_fail_reasons.append("Odds are stale.")
    if data_quality_score < thresholds.min_data_quality_watchlist:
        hard_fail_reasons.append("Data quality score below minimum threshold.")
    if model_market_disagreement > thresholds.max_model_market_disagreement:
        hard_fail_reasons.append("Model-market disagreement exceeds maximum threshold.")

    if hard_fail_reasons:
        return {
            "recommendation": "NO BET",
            "confidence": "LOW",
            "risk": "HIGH",
            "reason": " ".join(hard_fail_reasons),
            "hard_fail_reasons": hard_fail_reasons,
        }

    if edge >= thresholds.min_edge_bet and expected_value >= thresholds.min_ev_bet and data_quality_score >= thresholds.min_data_quality_bet:
        recommendation = "BET"
        confidence = "HIGH"
        risk = "LOW"
        reason = "Positive expected value, sufficient edge, and strong data quality."
    elif edge >= thresholds.min_edge_watchlist and expected_value >= thresholds.min_ev_watchlist:
        recommendation = "WATCHLIST"
        confidence = "LOW"
        risk = "MEDIUM"
        reason = "Potential value detected, but final BET threshold is not met."
    else:
        recommendation = "NO BET"
        confidence = "LOW"
        risk = "MEDIUM"
        reason = "No sufficient betting edge identified."

    if recommendation not in ALLOWED_RECOMMENDATIONS:
        raise ValueError(f"Invalid recommendation output: {recommendation}")
    return {"recommendation": recommendation, "confidence": confidence, "risk": risk, "reason": reason, "hard_fail_reasons": []}


def probability_comparison_chart(market: str, selection: str, model_probability: float, bookie_probability: float) -> dict:
    return {
        "type": "model_vs_bookie_probability_comparison",
        "market": market,
        "selection": selection,
        "unit": "probability",
        "series": [
            {"label": "Model probability", "value": round(model_probability, 6)},
            {"label": "Bookmaker no-vig probability", "value": round(bookie_probability, 6)},
        ],
        "delta": round(model_probability - bookie_probability, 6),
    }


def build_recommendation_payload(
    *,
    fixture_id: int,
    market: str,
    selection: str,
    decimal_odds: float,
    model_probability: float,
    bookie_probability: float,
    data_quality_score: int,
    xg_available: bool,
    historical_odds_available: bool,
    odds_fresh: bool = True,
    auto_betting_enabled: bool = False,
    audit_source: str = "phase3_direct_request",
) -> dict:
    edge = calculate_edge(model_probability, bookie_probability)
    ev = calculate_expected_value(model_probability, decimal_odds)
    decision = recommendation_decision(
        edge=edge,
        expected_value=ev,
        data_quality_score=data_quality_score,
        xg_available=xg_available,
        historical_odds_available=historical_odds_available,
        odds_fresh=odds_fresh,
        model_market_disagreement=abs(edge),
        auto_betting_enabled=auto_betting_enabled,
    )
    chart = probability_comparison_chart(market, selection, model_probability, bookie_probability)
    return {
        "fixture_id": fixture_id,
        "model_version": MODEL_VERSION,
        "market": market,
        "selection": selection,
        "decimal_odds": decimal_odds,
        "model_probability": model_probability,
        "bookie_probability": bookie_probability,
        "edge": edge,
        "expected_value": ev,
        "fair_odds": fair_odds(model_probability),
        "minimum_acceptable_odds": minimum_acceptable_odds(model_probability, required_ev=0.0),
        "recommendation": decision["recommendation"],
        "confidence": decision["confidence"],
        "risk": decision["risk"],
        "reason": decision["reason"],
        "hard_fail_reasons": decision["hard_fail_reasons"],
        "comparison_chart": chart,
        "audit_trail": {
            "audit_source": audit_source,
            "model_version": MODEL_VERSION,
            "mandatory_xg_available": xg_available,
            "mandatory_historical_odds_available": historical_odds_available,
            "odds_fresh": odds_fresh,
            "data_quality_score": data_quality_score,
            "auto_betting_enabled": False,
            "auto_betting_hard_locked": True,
        },
    }
