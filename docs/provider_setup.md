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
| API-FOOTBALL | Fixtures, results, lineups, injuries candidate | Validate competition IDs and coverage depth |
| The Odds API | Current odds and historical odds candidate | Validate market coverage and historical depth |
| Sportmonks | Combined football data candidate | Validate xG, odds, lineups, injuries, Eliteserien coverage |
| StatsBomb | xG candidate | Validate access, licensing, and competition coverage |

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
SPORTMONKS_KEY=...
STATSBOMB_KEY=...
```

Do not commit `.env` to GitHub.

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
