# Football Edge Agent — Provider Setup — 08:33, 27.04.2026 Europe/Oslo

## Purpose

This document defines the Phase 2 provider setup plan for fixtures, results, current odds, historical odds, xG, lineups, injuries/suspensions, provider coverage checks, data-quality scoring, and audit logging.

## Mandatory Coverage

| Data Domain | Mandatory | Governance Effect if Missing |
|---|---:|---|
| Current odds | Yes | NO BET |
| Historical odds | Yes | NO BET and no valid backtest |
| xG | Yes | NO BET and no valid model foundation |
| Fixtures/results | Yes | NO BET |
| Lineups | Yes where available | WATCHLIST or NO BET |
| Injuries/suspensions | Yes | WATCHLIST or NO BET |
| Provider timestamps | Yes | NO BET |
| Provider audit trail | Yes | NO BET |

## Candidate Provider Roles

| Provider | Candidate Role | Notes |
|---|---|---|
| API Sports — API-FOOTBALL | Fixtures, results, current odds, lineups, injuries candidate | Existing `api_football` integration; validate competition IDs and coverage depth |
| The Odds API | Current odds and historical odds candidate | Validate market coverage and historical depth |
| SportsDataIO Soccer API | Fixtures, results, odds, lineups, injuries candidate | Validate licensed feeds, historical warehouse access, and competition coverage |
| Soccerdata API | Fixtures, results, current odds, lineups, injuries candidate | Validate market, league, timestamp, and data-depth coverage |
| SportsGameOdds | Disabled by policy | Do not call at this point; dormant support requires an explicit future re-enable |
| SharpAPI | Current-odds candidate | Validate major-soccer coverage, event identity, market mapping, and timestamps |
| StatsBomb | xG candidate | Validate access, licensing, and competition coverage |

Every entry is candidate-only. Configuration or fixture-ID extraction support does not establish an active subscription, legal entitlement, competition coverage, live ingestion, or suitability for the comparable-consensus gate.

Temporary PIP fixture registration may use Odds API alone when the protected workflow explicitly sets `PIP_SINGLE_PROVIDER_MODE=true`. This exception supports registration and market-only observation only; it does not establish consensus or authorize probabilities, recommendations, betting, or execution.

## Approved MVP Competitions

- EPL
- LALIGA
- BUNDESLIGA
- SERIE_A
- LIGUE_1
- UCL
- UEL
- NOR_ELITESERIEN

## Approved MVP Markets

- `1X2`
- `OVER_UNDER_2_5`
- `BTTS`

## Environment Variables

Add provider credentials to `.env`:

```text
API_FOOTBALL_KEY=...
ODDS_API_KEY=...
SPORTSDATA_IO_KEY=...
SOCCERDATA_API_KEY=...
SPORTS_GAME_ODDS_KEY=...
SPORTS_GAME_ODDS_ENABLED=false
SHARPAPI_KEY=...
STATSBOMB_KEY=...
```

Do not commit `.env` to GitHub.

`SPORTS_GAME_ODDS_ENABLED` must remain `false` until an explicit provider-policy change approves renewed use.

Use server-side secret storage only. API Sports' soccer product is represented by the existing `API_FOOTBALL_*` settings; do not create a second duplicate API Sports credential.

## Provider Validation Procedure

1. Verify each provider's legal/licensing terms for private MVP use.
2. Confirm coverage for all eight MVP competitions.
3. Confirm odds market availability for 1X2, Over/Under 2.5 Goals, and BTTS.
4. Confirm historical odds availability.
5. Confirm xG availability.
6. Confirm team/fixture entity mappings.
7. Confirm timestamps and provider audit fields.
8. Record provider gaps in `provider_competition_mappings`.
9. Mark fixtures with material gaps as `NO BET` through `data_quality_scores`.

## Provider Coverage Gate

No future recommendation may be eligible for `BET` until provider coverage confirms historical odds and xG. Missing provider coverage shall not be inferred, substituted, or manually invented.
