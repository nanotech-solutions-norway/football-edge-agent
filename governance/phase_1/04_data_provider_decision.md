# Football Edge Intelligence Agent — Data Provider Decision — 01:34, 27.04.2026 Europe/Oslo

## 1. Provider Decision Principle

The Football Edge Intelligence Agent shall use only data providers or provider stacks capable of supporting probability-calibrated football market analysis with auditable data lineage. Provider selection must prioritize data completeness, timestamp integrity, historical odds coverage, xG coverage, licensing clarity, and operational reliability.

## 2. Mandatory Provider Requirements

| Requirement | Status | Governance Effect |
|---|---|---|
| Current odds | Mandatory | Missing or stale odds force NO BET |
| Historical odds | Mandatory | Missing historical odds force NO BET and blocks backtesting |
| xG data | Mandatory | Missing xG force NO BET and blocks model validation |
| Fixtures | Mandatory | Missing fixture data force NO BET |
| Results | Mandatory | Missing result data blocks validation |
| Lineups | Mandatory near kickoff where available | Missing lineup data may force WATCHLIST or NO BET |
| Injuries/suspensions | Mandatory | Missing material team-news data may force WATCHLIST or NO BET |
| Timestamps | Mandatory | Missing timestamps force NO BET |
| Provider audit trail | Mandatory | Missing audit trail invalidates recommendation |
| Competition coverage | Mandatory | Must cover all approved MVP competitions or define controlled gaps |
| Market coverage | Mandatory | Must support 1X2, Over/Under 2.5 Goals, and Both Teams To Score |

## 3. Approved MVP Competitions Requiring Coverage

Provider feasibility shall be assessed against these competitions only:

1. Premier League
2. La Liga
3. Bundesliga
4. Serie A
5. Ligue 1
6. UEFA Champions League
7. UEFA Europa League
8. Eliteserien

## 4. Approved MVP Markets Requiring Coverage

Provider feasibility shall be assessed against these markets only:

1. 1X2
2. Over/Under 2.5 Goals
3. Both Teams To Score

## 5. Historical Odds Requirement

Historical odds are mandatory because the model requires market benchmarking, closing-line-value analysis, margin adjustment, no-vig probability conversion, and backtesting against realistic available prices. A provider stack without historical odds is not sufficient for BET recommendations.

## 6. xG Requirement

xG data are mandatory because xG-derived team and match indicators are core model inputs for goal expectation, attacking quality, defensive quality, trend analysis, and model calibration. A provider stack without xG is not sufficient for BET recommendations.

## 7. Provider Stack Model

A single provider may be used only if it satisfies all mandatory requirements. If no single provider satisfies all requirements, a combined provider stack may be used, provided that:

1. Entity mapping is controlled across teams, competitions, fixtures, and markets.
2. Timestamp integrity is preserved.
3. Historical odds and xG remain auditable.
4. Provider licensing permits the intended use.
5. Gaps are logged and routed to NO BET where material.

## 8. Data Freshness Controls

| Data Type | Freshness Requirement | Recommendation Impact |
|---|---|---|
| Current odds | Must be current for the decision window | Stale odds force NO BET |
| Lineups | Must be refreshed near kickoff where relevant | Missing confirmed lineup may force WATCHLIST/NO BET |
| Injuries/suspensions | Must be refreshed before recommendation | Missing material team news may force WATCHLIST/NO BET |
| Fixtures/results | Must match provider timestamp and competition schedule | Inconsistency forces NO BET |
| Historical odds | Must be traceable to source and timestamp | Missing history blocks validation |
| xG | Must be traceable to source, season, team, and fixture basis | Missing xG blocks BET |

## 9. Provider Approval Gate

A provider or provider stack is approved for MVP only when it can support:

- all approved MVP competitions including Eliteserien;
- all approved MVP markets;
- current odds;
- historical odds;
- xG;
- fixtures and results;
- lineups and injuries/suspensions where available;
- timestamps;
- provider audit trail;
- licensing review for the intended use.

## 10. Default Failure Handling

If provider data are incomplete, stale, conflicting, unlicensed, unavailable, or not auditable, the agent shall return **NO BET** unless the issue is minor and explicitly suitable for **WATCHLIST** revalidation.
