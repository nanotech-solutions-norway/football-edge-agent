# Football Edge Intelligence Agent — No-Bet Policy — 01:34, 27.04.2026 Europe/Oslo

## 1. Policy Principle

The default recommendation of the Football Edge Intelligence Agent is **NO BET**. A **BET** status is permitted only when every approved data, scope, expected-value, model-confidence, risk, and compliance control passes.

The system shall never frame a recommendation as guaranteed, risk-free, certain, a sure win, a banker, a lock, or 100% accurate.

## 2. Approved Recommendation Statuses

| Status | Meaning | Treatment |
|---|---|---|
| BET | All controls pass and positive expected value is present | May provide controlled stake guidance within maximum limits |
| WATCHLIST | Potential value exists but revalidation is required | No final bet recommendation |
| NO BET | Controls fail or edge is insufficient | Default output |

## 3. Mandatory NO BET Conditions

The agent shall return **NO BET** if any of the following apply:

1. Competition is outside approved MVP scope.
2. Market is outside approved MVP scope.
3. Current odds are missing, stale, or not auditable.
4. Historical odds are missing or inadequate.
5. xG data are missing or inadequate.
6. Fixture or result records are missing or inconsistent.
7. Provider timestamps are missing.
8. Provider audit trail is missing.
9. Material injury/suspension data are missing or conflicting.
10. Confirmed lineup uncertainty materially changes the market assessment near kickoff.
11. Model probability does not exceed bookmaker no-vig probability by the required edge threshold.
12. Expected value is non-positive or below threshold.
13. Model confidence is too low.
14. Risk exposure cap would be breached.
15. Drawdown or stop-loss rules are triggered.
16. Legal/compliance status is unclear.
17. Auto-betting activation is requested.
18. The request includes guaranteed, reckless, or loss-chasing language.

## 4. Supported Scope for BET Eligibility

A **BET** status may only be considered for these competitions:

- Premier League
- La Liga
- Bundesliga
- Serie A
- Ligue 1
- UEFA Champions League
- UEFA Europa League
- Eliteserien

A **BET** status may only be considered for these markets:

- 1X2
- Over/Under 2.5 Goals
- Both Teams To Score

## 5. Data Freshness and Audit Requirements

| Control | Requirement | Failure Result |
|---|---|---|
| Current odds | Must be current and timestamped | NO BET |
| Historical odds | Must be available and auditable | NO BET |
| xG | Must be available and auditable | NO BET |
| Lineups | Must be refreshed near kickoff where relevant | WATCHLIST or NO BET |
| Injuries/suspensions | Must be refreshed before recommendation | WATCHLIST or NO BET |
| Provider audit trail | Must identify source and timestamp | NO BET |

## 6. Risk and Bankroll Maximums

Phase 1 implements maximum policy values for controlled validation. These may be reduced later through controlled governance revision.

| Risk Control | Maximum Value |
|---|---:|
| Maximum stake per BET recommendation | 1.00% of bankroll |
| Pilot stake ceiling | 1.00% of bankroll |
| Daily exposure cap | 3.00% of bankroll |
| Weekly exposure cap | 8.00% of bankroll |
| Correlated exposure cap | 2.00% of bankroll |

Loss chasing is prohibited. Stake escalation after losses is prohibited. Any request to override these limits shall return **NO BET** and log a governance exception.

## 7. Required Recommendation Chart

Every recommendation output, including **NO BET**, shall include or reference a model-probability versus bookmaker-probability comparison where market data are available:

| Market | Selection | Model Probability | Bookmaker Raw Implied Probability | Bookmaker No-Vig Probability | Edge | Status |
|---|---|---:|---:|---:|---:|---|
| Example | Example | To be calculated | To be calculated | To be calculated | To be calculated | BET / WATCHLIST / NO BET |

## 8. Auto-Betting Response Rule

Any request to activate, simulate activation of, connect, or execute auto-betting shall be rejected during MVP. Auto-betting remains inactive and hard-locked.

## 9. Governance Logging

Every **BET**, **WATCHLIST**, or **NO BET** output shall log:

1. Match and competition.
2. Market and selection.
3. Recommendation status.
4. Model probability.
5. Bookmaker probability.
6. Edge and expected value.
7. Data-source status.
8. Timestamp status.
9. Risk-control status.
10. Reason for **NO BET** or **WATCHLIST** where applicable.
