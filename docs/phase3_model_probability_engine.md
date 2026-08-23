# Phase 3 — Baseline Model and Probability Engine — 20:16, 27.04.2026 Europe/Oslo

## Executive status

Phase 3 adds the first functional baseline probability engine to the Football Edge Intelligence Agent. The implementation remains analytical decision-support only and is not approved for real-money betting.

Default output remains **NO BET** unless data quality, positive expected value, edge, risk controls, and governance checks are satisfied.

## Scope implemented

- Market-implied probability conversion from decimal odds.
- No-vig bookmaker probability normalization and bookmaker margin calculation.
- Elo foundation and Glicko scaffold.
- xG feature support through rolling xG expected-goals derivation.
- Poisson scoreline matrix with derived market probabilities.
- Ensemble blending of Poisson/xG, no-vig market baseline, and Elo signals.
- Brier score and log loss helpers for calibration.
- Expected value, edge, fair odds, and minimum acceptable odds.
- Recommendation output restricted to `BET`, `WATCHLIST`, and `NO BET`.
- Model-vs-bookie probability comparison chart payload.
- API endpoints for model status, probability calculation, direct recommendations, and backtest summary.
- Database migration `003_model_probability_engine.sql`.

## Governance controls

Mandatory no-bet conditions:

- Missing historical odds.
- Missing xG.
- Stale odds.
- Data-quality score below threshold.
- Excessive model-market disagreement.
- Any attempt to enable auto-betting.

Auto-betting remains inactive and hard-locked.

## API endpoints

```text
GET  /model/status
POST /probabilities/calculate
POST /recommendations/fixture/direct
POST /backtests/summary
```

## Recommendation output contract

Every recommendation payload includes:

- `model_probability`
- `bookie_probability`
- `edge`
- `expected_value`
- `fair_odds`
- `minimum_acceptable_odds`
- `recommendation`
- `confidence`
- `risk`
- `reason`
- `hard_fail_reasons`
- `comparison_chart`
- `audit_trail`

## Test and validation commands

```bash
python scripts/validate_phase3.py
python -m pytest -vv
```

## Completion gate

Phase 3 is complete when:

- Market-implied and no-vig probabilities normalize correctly.
- Poisson-derived probabilities normalize correctly.
- Missing xG or historical odds blocks probability generation and forces NO BET posture.
- Recommendation outputs are restricted to BET, WATCHLIST, and NO BET.
- Comparison chart data is generated for every recommendation.
- Auto-betting remains inactive and hard-locked.
- GitHub Actions passes.
