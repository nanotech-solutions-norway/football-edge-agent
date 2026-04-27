# Football Edge Intelligence Agent — Success Metrics — 01:34, 27.04.2026 Europe/Oslo

## 1. Measurement Philosophy

The Football Edge Intelligence Agent shall be evaluated as a probability-calibrated decision-support system, not as a certainty engine. Success shall be measured through calibration, market-price quality, data quality, expected value discipline, risk control, and conservative no-bet behavior.

Simple hit rate shall not be the primary success metric.

## 2. Mandatory Metrics

| Metric | Definition | Governance Use |
|---|---|---|
| Brier score | Mean squared error between predicted probability and actual binary outcome | Calibration and probability-quality assessment |
| Log loss | Penalizes confident wrong probabilities | Calibration and overconfidence control |
| Calibration curve | Plots predicted probability against observed frequency | Probability trustworthiness |
| Closing-line value (CLV) | Difference between recommended odds and closing market odds | Market-price quality signal |
| ROI | Profit divided by total stake | Financial simulation indicator |
| Yield | Profit per unit staked | Efficiency indicator during paper trading |
| Maximum drawdown | Largest peak-to-trough decline in simulated bankroll | Risk-control indicator |
| No-bet rate | Percentage of analyzed markets returning NO BET | Conservative discipline indicator |
| Data-quality pass rate | Percentage of analyses meeting mandatory data requirements | Provider and pipeline quality control |
| Recommendation distribution | BET / WATCHLIST / NO BET counts | Governance posture audit |

## 3. Required Data Inputs for Metrics

Success metrics require auditable data:

1. Current odds.
2. Historical odds.
3. Closing odds.
4. xG data.
5. Fixture and result records.
6. Competition and market identifiers.
7. Provider timestamps.
8. Recommendation timestamp.
9. Model version.
10. Recommendation status.
11. Stake simulation where applicable.

Historical odds and xG are mandatory for model validation and must not be treated as optional enrichment.

## 4. Probability Comparison Requirement

Each recommendation report shall include a probability comparison chart showing:

| Market | Selection | Model Probability | Bookmaker Raw Implied Probability | Bookmaker No-Vig Probability | Edge | Recommendation |
|---|---|---:|---:|---:|---:|---|
| Example | Example | To be calculated | To be calculated | To be calculated | To be calculated | BET / WATCHLIST / NO BET |

## 5. MVP Validation Requirements

Before any real-money readiness review, the project must complete:

1. Historical backtest using historical odds.
2. Historical backtest using xG-derived features.
3. Train/test split by season.
4. Competition-level performance breakdown.
5. Market-level performance breakdown.
6. Calibration analysis.
7. Closing-line-value analysis.
8. Drawdown analysis.
9. No-bet policy audit.
10. Data-quality audit.
11. Provider-timestamp audit.
12. Recommendation-status distribution analysis.

## 6. Reporting Standard

Weekly validation reporting in later phases shall include:

| Report Section | Required Content |
|---|---|
| Recommendation distribution | BET / WATCHLIST / NO BET counts |
| Market breakdown | 1X2, Over/Under 2.5 Goals, Both Teams To Score |
| Competition breakdown | Premier League, La Liga, Bundesliga, Serie A, Ligue 1, UEFA Champions League, UEFA Europa League, Eliteserien |
| Calibration | Brier score, log loss, calibration chart |
| Market-quality analysis | CLV and odds movement |
| Financial simulation | ROI, yield, drawdown, exposure |
| Governance exceptions | Missing data, stale data, provider conflicts, unsupported requests |

## 7. Phase 1 Target Position

| Metric | Phase 1 Target Definition |
|---|---|
| Brier score | Must be tracked from first model version |
| Log loss | Must be tracked from first model version |
| Calibration curve | Must be generated during validation |
| CLV | Must be tracked during paper trading |
| ROI | Informational only during early phase |
| Yield | Informational only during early phase |
| Maximum drawdown | Must be tracked before any live-money review |
| No-bet rate | Expected to be high |
| Historical odds coverage | Mandatory |
| xG coverage | Mandatory |
| Data freshness compliance | Mandatory |

## 8. Success Metric Clause

The agent shall not be promoted, expanded, used commercially, or used for real-money testing unless probability calibration, historical odds coverage, xG coverage, data quality, expected-value analysis, CLV, and drawdown controls are validated and documented.
