# Football Edge Agent — Phase 2 Backend Foundation — 08:33, 27.04.2026 Europe/Oslo

This repository contains the Phase 2 backend/data foundation for the Football Edge Intelligence Agent.

## Governance posture

- Private analytical decision-support only unless later legally approved.
- Default recommendation posture: **NO BET**.
- No guaranteed picks, loss chasing, reckless staking, unsupported markets, or unsupported competitions.
- Auto-betting is represented only as an inactive, hard-locked architecture placeholder.
- Eliteserien is the only approved Norwegian elite-league name.

## MVP competitions

- Premier League (`EPL`)
- La Liga (`LALIGA`)
- Bundesliga (`BUNDESLIGA`)
- Serie A (`SERIE_A`)
- Ligue 1 (`LIGUE_1`)
- UEFA Champions League (`UCL`)
- UEFA Europa League (`UEL`)
- Eliteserien (`NOR_ELITESERIEN`)

## MVP markets

- 1X2
- Over/Under 2.5 Goals
- Both Teams To Score

## Mandatory data domains

- Fixtures and results
- Current odds
- Historical odds
- xG
- Lineups
- Injuries/suspensions
- Provider timestamps
- Provider audit trail
- Data-quality scoring
- Audit logging

## Local startup

```bash
cp .env.example .env
docker compose up --build
```

Then open:

```text
http://localhost:8000/docs
```

## Key endpoints

```text
GET  /health
GET  /providers/status
GET  /fixtures/upcoming
GET  /fixtures/{fixture_id}
GET  /odds/current/{fixture_id}
GET  /odds/history/{fixture_id}
GET  /xg/{fixture_id}
GET  /lineups/{fixture_id}
GET  /injuries/{fixture_id}
GET  /data-quality/{fixture_id}
GET  /audit/fixture/{fixture_id}
GET  /auto-betting/status
POST /auto-betting/execute
```

## Documentation

- `docs/implementation_instructions.md`
- `docs/domain_and_hosting_domeneshop.md`
- `docs/provider_setup.md`
- `docs/api_contract.md`
- `docs/database_schema.md`
- `docs/validation_checklist.md`
- `docs/phase2_completion_report_template.md`
