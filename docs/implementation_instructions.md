# Football Edge Agent — Phase 2 Implementation Instructions — 13:58, 27.04.2026 Europe/Oslo

## Objective

Implement the Phase 2 FastAPI + PostgreSQL backend foundation for the Football Edge Intelligence Agent. This phase creates the data and API infrastructure only. It does not create a betting model and does not activate auto-betting.

## Governance Baseline

- Analytical decision-support only unless later legally approved.
- Default recommendation posture: **NO BET**.
- Historical odds are mandatory.
- xG is mandatory.
- Auto-betting is inactive and hard-locked.
- Use Eliteserien only for Norwegian elite-league coverage.
- Supported competitions: `EPL`, `LALIGA`, `BUNDESLIGA`, `SERIE_A`, `LIGUE_1`, `UCL`, `UEL`, `NOR_ELITESERIEN`.
- Supported markets: `1X2`, `OVER_UNDER_2_5`, `BTTS`.

## Repository Structure

```text
football-edge-agent/
├── backend/
│   ├── Dockerfile
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/routes.py
│   │   ├── db/init/001_schema.sql
│   │   ├── db/init/002_seed_competitions.sql
│   │   ├── providers/clients.py
│   │   └── services/
│   │       ├── auto_betting_service.py
│   │       └── data_quality_service.py
│   └── tests/test_phase2.py
├── docs/
├── scripts/validate_phase2.py
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
├── .env.example
└── .github/workflows/phase2-ci.yml
```

## Local Setup

```bash
git clone https://github.com/nanotech-solutions-norway/football-edge-agent.git
cd football-edge-agent
cp .env.example .env
docker compose up --build
```

Open:

```text
http://localhost:8000/docs
```

## Validation

Run static repository validation:

```bash
python scripts/validate_phase2.py
```

Run backend tests:

```bash
pip install -r requirements.txt
pytest
```

## Database Bootstrap

For a clean PostgreSQL reload:

```bash
docker compose down -v
docker compose up --build
```

The schema and seed files are loaded by PostgreSQL on first volume creation from:

```text
backend/app/db/init/
```

## Provider Setup

1. Copy `.env.example` to `.env`.
2. Add provider API keys.
3. Validate fixture, odds, historical odds, xG, lineup, injury/suspension, timestamp, and audit-trail coverage.
4. Record provider gaps in the database and documentation.
5. Force `NO BET` where historical odds or xG are missing.

## Hosting Setup

Use Domeneshop for domain/DNS. Use an external backend host unless the purchased Domeneshop plan explicitly confirms support for a long-running FastAPI process, PostgreSQL, scheduled jobs, HTTPS/TLS, environment variables, and restart/log management.

Recommended fallback order:

1. Render
2. Railway
3. Fly.io
4. Hetzner VPS
5. DigitalOcean
6. Major cloud providers only if required later

## Phase 2 Completion Criteria

- Backend runs locally.
- `/docs` loads.
- Database schema creates successfully.
- All eight MVP competitions are seeded.
- Historical odds and xG provider coverage is confirmed or assigned to a backup provider.
- `/auto-betting/status` returns inactive/hard-locked.
- Domeneshop suitability is documented.
