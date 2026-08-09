"""R0 fundamental football probability research module.

Reconciled from the useful mathematical foundations in Phase 3 PR #8 with a
stricter separation between the *fundamental model* and market prices.

Important R0 constraints:
- bookmaker probabilities are never blended into fundamental probabilities;
- no BET/WATCHLIST/recommendation decision is produced here;
- chronological validation helpers are provided to prevent future leakage;
- this module is not wired into live routes during R0.
"""
from __future__ import annotations

from datetime import datetime
from math import exp, factorial, log
from typing import Iterable, Mapping, Sequence

MODEL_NAME = "football_edge_r0_fundamental_probability"
MODEL_VERSION = "0.4.0-r0-research"
MARKET_SELECTIONS: dict[str, tuple[str, ...]] = {
    "1X2": ("home", "draw", "away"),
    "OVER_UNDER_2_5": ("over_2_5", "under_2_5"),
    "BTTS": ("yes", "no"),
}


def exponential_decay_weights(length: int, half_life_matches: float = 5.0) -> list[float]:
    """Return normalized oldest->newest weights with the newest observation largest."""
    if length < 1:
        raise ValueError("length must be positive")
    if half_life_matches <= 0:
        raise ValueError("half_life_matches must be positive")
    raw = [0.5 ** ((length - 1 - index) / half_life_matches) for index in range(length)]
    total = sum(raw)
    return [value / total for value in raw]


def time_decayed_average(values: Sequence[float], half_life_matches: float = 5.0) -> float:
    if not values:
        raise ValueError("at least one historical value is required")
    if any(value < 0 for value in values):
        raise ValueError("historical xG values cannot be negative")
    weights = exponential_decay_weights(len(values), half_life_matches)
    return sum(float(value) * weight for value, weight in zip(values, weights))


def derive_expected_goals(
    *,
    home_xg_for: Sequence[float],
    home_xg_against: Sequence[float],
    away_xg_for: Sequence[float],
    away_xg_against: Sequence[float],
    half_life_matches: float = 5.0,
) -> tuple[float, float]:
    """Derive transparent time-decayed expected goals from xG for/against histories.

    The function is intentionally a baseline research estimator; later model
    work may add opponent/competition adjustment only when it is trained and
    validated chronologically.
    """
    home_attack = time_decayed_average(home_xg_for, half_life_matches)
    home_defence_allowed = time_decayed_average(home_xg_against, half_life_matches)
    away_attack = time_decayed_average(away_xg_for, half_life_matches)
    away_defence_allowed = time_decayed_average(away_xg_against, half_life_matches)
    return ((home_attack + away_defence_allowed) / 2.0, (away_attack + home_defence_allowed) / 2.0)


def _poisson_pmf(lam: float, goals: int) -> float:
    if lam < 0:
        raise ValueError("expected goals cannot be negative")
    if goals < 0:
        raise ValueError("goals cannot be negative")
    return exp(-lam) * (lam ** goals) / factorial(goals)


def poisson_scoreline_matrix(
    home_expected_goals: float,
    away_expected_goals: float,
    *,
    max_goals: int = 10,
) -> dict[tuple[int, int], float]:
    if home_expected_goals < 0 or away_expected_goals < 0:
        raise ValueError("expected goals cannot be negative")
    if max_goals < 1:
        raise ValueError("max_goals must be positive")
    matrix = {
        (home_goals, away_goals): _poisson_pmf(home_expected_goals, home_goals)
        * _poisson_pmf(away_expected_goals, away_goals)
        for home_goals in range(max_goals + 1)
        for away_goals in range(max_goals + 1)
    }
    total = sum(matrix.values())
    if total <= 0:
        raise ValueError("scoreline matrix failed to normalize")
    return {score: probability / total for score, probability in matrix.items()}


def fundamental_market_probabilities(
    market: str,
    *,
    home_expected_goals: float,
    away_expected_goals: float,
) -> dict[str, float]:
    """Generate market probabilities using only the fundamental score model."""
    if market not in MARKET_SELECTIONS:
        raise ValueError(f"unsupported market: {market}")
    matrix = poisson_scoreline_matrix(home_expected_goals, away_expected_goals)
    if market == "1X2":
        probabilities = {
            "home": sum(p for (home, away), p in matrix.items() if home > away),
            "draw": sum(p for (home, away), p in matrix.items() if home == away),
            "away": sum(p for (home, away), p in matrix.items() if home < away),
        }
    elif market == "OVER_UNDER_2_5":
        probabilities = {
            "over_2_5": sum(p for (home, away), p in matrix.items() if home + away >= 3),
            "under_2_5": sum(p for (home, away), p in matrix.items() if home + away <= 2),
        }
    else:
        probabilities = {
            "yes": sum(p for (home, away), p in matrix.items() if home > 0 and away > 0),
            "no": sum(p for (home, away), p in matrix.items() if home == 0 or away == 0),
        }
    total = sum(probabilities.values())
    return {selection: value / total for selection, value in probabilities.items()}


def no_vig_market_probabilities(odds_by_selection: Mapping[str, float]) -> dict[str, float]:
    """Convert market prices to a separate no-vig comparison baseline."""
    if not odds_by_selection:
        raise ValueError("odds_by_selection cannot be empty")
    implied: dict[str, float] = {}
    for selection, odds in odds_by_selection.items():
        if odds <= 1.0:
            raise ValueError("decimal odds must be greater than 1.0")
        implied[selection] = 1.0 / float(odds)
    total = sum(implied.values())
    return {selection: value / total for selection, value in implied.items()}


def compare_fundamental_to_market(
    model_probabilities: Mapping[str, float],
    market_probabilities: Mapping[str, float],
) -> dict[str, dict[str, float]]:
    """Compare independent probabilities; never feed market values back into the model."""
    if set(model_probabilities) != set(market_probabilities):
        raise ValueError("model and market selections must match")
    return {
        selection: {
            "model_probability": float(model_probabilities[selection]),
            "market_probability": float(market_probabilities[selection]),
            "probability_delta": float(model_probabilities[selection]) - float(market_probabilities[selection]),
            "model_fair_odds": (1.0 / float(model_probabilities[selection])) if model_probabilities[selection] > 0 else float("inf"),
        }
        for selection in model_probabilities
    }


def multiclass_brier_score(probabilities: Mapping[str, float], actual_selection: str) -> float:
    if actual_selection not in probabilities:
        raise ValueError("actual_selection must be present in probabilities")
    if not probabilities or any(value < 0 or value > 1 for value in probabilities.values()):
        raise ValueError("probabilities must be in [0, 1]")
    if abs(sum(probabilities.values()) - 1.0) > 1e-6:
        raise ValueError("probabilities must sum to 1")
    return sum((probability - (1.0 if selection == actual_selection else 0.0)) ** 2 for selection, probability in probabilities.items())


def multiclass_log_loss(probabilities: Mapping[str, float], actual_selection: str, epsilon: float = 1e-15) -> float:
    if actual_selection not in probabilities:
        raise ValueError("actual_selection must be present in probabilities")
    probability = float(probabilities[actual_selection])
    if not 0 <= probability <= 1:
        raise ValueError("probability must be in [0, 1]")
    probability = min(max(probability, epsilon), 1.0 - epsilon)
    return -log(probability)


def assert_chronological_split(
    train_timestamps: Iterable[datetime],
    validation_timestamps: Iterable[datetime],
    test_timestamps: Iterable[datetime],
) -> None:
    """Fail when temporal partitions overlap or are not strictly ordered."""
    train = list(train_timestamps)
    validation = list(validation_timestamps)
    test = list(test_timestamps)
    if not train or not validation or not test:
        raise ValueError("train, validation, and test partitions must all be non-empty")
    all_timestamps = train + validation + test
    if any(value.tzinfo is None for value in all_timestamps):
        raise ValueError("all timestamps must be timezone-aware")
    if not max(train) < min(validation):
        raise ValueError("training data must end before validation data begins")
    if not max(validation) < min(test):
        raise ValueError("validation data must end before test data begins")
