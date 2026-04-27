# Football Edge Intelligence Agent — Supported Competitions and Markets — 01:34, 27.04.2026 Europe/Oslo

## 1. MVP Competition Scope

MVP competition scope shall include the following competitions only:

| Priority | Competition | MVP Status | Notes |
|---:|---|---|---|
| 1 | Premier League | Included | Core high-liquidity benchmark league |
| 2 | La Liga | Included | Core high-liquidity benchmark league |
| 3 | Bundesliga | Included | Core high-liquidity benchmark league |
| 4 | Serie A | Included | Core high-liquidity benchmark league |
| 5 | Ligue 1 | Included | Core high-liquidity benchmark league |
| 6 | UEFA Champions League | Included | Core European club competition |
| 7 | UEFA Europa League | Included | Core European club competition |
| 8 | Eliteserien | Included | Norwegian elite-league coverage; enhanced data-quality checks required |

## 2. Excluded Competitions During MVP

| Competition Type | MVP Status | Reason |
|---|---|---|
| Lower divisions | Excluded | Lower data quality and lower market liquidity |
| Youth/reserve leagues | Excluded | Insufficient reliable data coverage |
| Friendlies | Excluded | Lower predictability and weaker market benchmark value |
| Most national-team fixtures | Excluded | Inconsistent squad and motivation context |
| Women’s competitions | Excluded for MVP | Deferred pending dedicated data-quality review |
| Domestic cups | Excluded for MVP | Rotation and motivation volatility |

## 3. Competition-Scope Clause

MVP competition scope shall include **Premier League, La Liga, Bundesliga, Serie A, Ligue 1, UEFA Champions League, UEFA Europa League, and Eliteserien**. No other competition shall be recommended unless added through a controlled governance revision.

Eliteserien is included because Norwegian elite-league coverage is strategically relevant to the primary compliance and operating context. Because data depth and market liquidity may differ from larger European competitions, Eliteserien recommendations shall require enhanced data-quality checks, historical odds coverage, and xG validation.

## 4. MVP Betting Markets

MVP markets shall be limited to:

| Market | MVP Status | Reason |
|---|---|---|
| 1X2 | Included | Core market; strong benchmark and broad data availability |
| Over/Under 2.5 Goals | Included | Compatible with goal models, xG, and total-goals probability models |
| Both Teams To Score | Included | Compatible with scoreline probability matrix and xG-derived attack/defense estimates |

## 5. Excluded Markets During MVP

| Market | MVP Status | Reason |
|---|---|---|
| Asian Handicap | Later phase | Requires more complex pricing, push handling, and liquidity checks |
| Double Chance | Later phase | Often low edge after margin; defer until benchmark validation |
| Draw No Bet | Later phase | Requires dedicated market calibration |
| Correct Score | Excluded | High variance and weaker MVP suitability |
| Accumulators/parlays | Excluded | Correlation risk and higher margin exposure |
| Player props | Excluded | Requires deeper player-level data and availability modeling |
| Cards/corners | Excluded | Requires referee, tactical, and event-specific datasets |
| In-play/live markets | Excluded | Requires low-latency infrastructure and separate operational controls |

## 6. Market-Scope Clause

The agent shall analyze and recommend only **1X2, Over/Under 2.5 Goals, and Both Teams To Score** during MVP. Unsupported markets shall return **NO BET** or an out-of-scope response.

## 7. Recommendation Statuses

| Status | Meaning | Required Treatment |
|---|---|---|
| BET | Positive expected value, sufficient edge, fresh data, acceptable risk | Allowed only if all mandatory controls pass |
| WATCHLIST | Potential value but revalidation required | Recheck data, odds, lineups, and market movement before any decision |
| NO BET | Insufficient edge, confidence, data quality, market scope, or legal clarity | Default output |

## 8. Scope Enforcement Rule

If a fixture, competition, or market is outside MVP scope, the system shall not produce a **BET** recommendation. The output shall be **NO BET** or a scope-control explanation.

## 9. Required Probability Comparison Chart

Every supported market analysis shall include a model-probability versus bookmaker-probability comparison chart:

| Market | Selection | Model Probability | Bookmaker Raw Implied Probability | Bookmaker No-Vig Probability | Edge | Recommendation |
|---|---|---:|---:|---:|---:|---|
| 1X2 / O-U 2.5 / BTTS | To be specified | To be calculated | To be calculated | To be calculated | To be calculated | BET / WATCHLIST / NO BET |

## 10. Approved Phase 1 Baseline

| Governance Item | Approved Baseline |
|---|---|
| MVP competitions | Premier League; La Liga; Bundesliga; Serie A; Ligue 1; UEFA Champions League; UEFA Europa League; Eliteserien |
| MVP markets | 1X2; Over/Under 2.5 Goals; Both Teams To Score |
| Recommendation statuses | BET; WATCHLIST; NO BET |
| Default recommendation | NO BET |
| Mandatory data | Current odds; historical odds; xG; fixtures; results; lineups; injuries/suspensions; timestamps; provider audit trail |
