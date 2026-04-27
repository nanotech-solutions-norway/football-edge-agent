# Football Edge Agent — Database Schema — 08:33, 27.04.2026 Europe/Oslo

## Scope

The Phase 2 PostgreSQL schema supports the MVP backend foundation for fixtures, results, current odds, historical odds, xG, lineups, injuries/suspensions, provider coverage checks, data-quality scoring, and audit logging.

## Core Tables

| Table | Purpose |
|---|---|
| `competitions` | Approved MVP competitions, including `NOR_ELITESERIEN` for Eliteserien |
| `providers` | Candidate data providers and provider types |
| `provider_competition_mappings` | Provider coverage by competition and capability |
| `teams` | Team records and provider-key mappings |
| `fixtures` | Fixture schedule and match metadata |
| `fixture_results` | Final or pending match result records |
| `odds_snapshots` | Current and time-series odds observations |
| `historical_odds_imports` | Historical odds import tracking |
| `xg_observations` | Fixture/team xG observations |
| `lineups` | Lineup payloads and confirmation status |
| `injuries_suspensions` | Player availability records |
| `provider_health_checks` | Provider connectivity and status audit |
| `data_quality_scores` | Mandatory data coverage and fixture quality status |
| `audit_logs` | System and governance audit trail |

## Mandatory Data Governance

A fixture cannot become eligible for a future `BET` status unless the database can evidence:

- current odds;
- historical odds;
- xG;
- fixtures/results;
- lineups where relevant;
- injuries/suspensions;
- provider timestamps;
- provider audit trail.

Missing historical odds or xG must force `NO BET` under the Phase 1 governance baseline.

## Seeded Competitions

The seed file `backend/app/db/init/002_seed_competitions.sql` inserts:

- `EPL` — Premier League
- `LALIGA` — La Liga
- `BUNDESLIGA` — Bundesliga
- `SERIE_A` — Serie A
- `LIGUE_1` — Ligue 1
- `UCL` — UEFA Champions League
- `UEL` — UEFA Europa League
- `NOR_ELITESERIEN` — Eliteserien

## Schema Bootstrap

The schema is loaded automatically by Docker Compose when the PostgreSQL volume is first created:

```bash
docker compose down -v
docker compose up --build
```

The SQL files are mounted at:

```text
/docker-entrypoint-initdb.d
```
