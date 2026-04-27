# Football Edge Agent — Phase 2 API Contract — 08:33, 27.04.2026 Europe/Oslo

## Purpose

This document defines the Phase 2 API contract for the MVP backend foundation. The contract supports future GPT Actions integration while preserving the Phase 1 governance posture: analytical decision-support only, **NO BET** by default, no guarantees, no loss chasing, supported competitions/markets only, and auto-betting inactive/hard-locked.

## Base URL

Local development:

```text
http://localhost:8000
```

Production target placeholder:

```text
https://api.your-domain.no
```

## Endpoints

| Method | Path | Purpose | Phase 2 Status |
|---|---|---|---|
| GET | `/health` | Service health and governance posture | Implemented |
| GET | `/providers/status` | Provider configuration and capability status | Implemented placeholder |
| GET | `/fixtures/upcoming` | Upcoming fixtures filtered by competition/date | Implemented placeholder |
| GET | `/fixtures/{fixture_id}` | Fixture detail | Implemented placeholder |
| GET | `/odds/current/{fixture_id}` | Current odds snapshots | Implemented placeholder |
| GET | `/odds/history/{fixture_id}` | Historical odds snapshots/imports | Implemented placeholder |
| GET | `/xg/{fixture_id}` | xG observations | Implemented placeholder |
| GET | `/lineups/{fixture_id}` | Lineup data | Implemented placeholder |
| GET | `/injuries/{fixture_id}` | Injuries and suspensions | Implemented placeholder |
| GET | `/data-quality/{fixture_id}` | Data-quality score and mandatory-data checks | Implemented placeholder |
| GET | `/audit/fixture/{fixture_id}` | Fixture audit trail | Implemented placeholder |
| GET | `/auto-betting/status` | Auto-betting status | Implemented |
| POST | `/auto-betting/execute` | Execution endpoint placeholder | Blocked with 403 |

## Recommendation-Critical Requirements

Future recommendation endpoints must include:

- model probability;
- bookmaker raw implied probability;
- bookmaker no-vig probability;
- edge;
- expected value;
- data-quality score;
- provider timestamps;
- audit trail;
- recommendation status: `BET`, `WATCHLIST`, or `NO BET`.

No future endpoint may issue a `BET` status without historical odds and xG support.

## Auto-Betting Contract

`GET /auto-betting/status` must return:

```json
{
  "enabled": false,
  "hard_locked": true,
  "provider": "none",
  "dry_run": true,
  "message": "Auto-betting is inactive and hard-locked. Phase 2 permits architecture only, not execution."
}
```

`POST /auto-betting/execute` must return HTTP 403 while `AUTO_BETTING_HARD_LOCK=true`.
