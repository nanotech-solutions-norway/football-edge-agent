# Football Edge Agent — Phase 2 Validation Checklist — 13:59, 27.04.2026 Europe/Oslo

## Static Repository Validation

| Control | Expected Result |
|---|---|
| Required backend files exist | Passed |
| Required documentation files exist | Passed |
| `NOR_ELITESERIEN` present | Passed |
| `Eliteserien` present | Passed |
| Historical odds marked mandatory | Passed |
| xG marked mandatory | Passed |
| `NO BET` default posture present | Passed |
| `AUTO_BETTING_HARD_LOCK=true` present | Passed |
| Legacy Norwegian league naming absent | Passed |

Run:

```bash
python scripts/validate_phase2.py
```

## FastAPI Validation

| Endpoint | Expected Result |
|---|---|
| `GET /` | Service metadata and `/docs` pointer |
| `GET /health` | `status=success`, `default_recommendation=NO BET` |
| `GET /providers/status` | Candidate provider capability payload |
| `GET /fixtures/upcoming` | Placeholder response with supported competitions |
| `GET /odds/current/{fixture_code}` | Placeholder current odds payload |
| `GET /odds/history/{fixture_code}` | Placeholder historical odds payload, mandatory true |
| `GET /xg/{fixture_code}` | Placeholder xG payload, mandatory true |
| `GET /data-quality/{fixture_code}` | Mandatory-data checklist with `NO_BET_UNTIL_PROVIDER_DATA_VALIDATED` |
| `GET /auto-betting/status` | `enabled=false`, `hard_locked=true` |
| `POST /auto-betting/execute` | HTTP 403 while hard-lock is active |

Run:

```bash
pytest
```

## Local Runtime Validation

1. Copy `.env.example` to `.env`.
2. Run `docker compose up --build`.
3. Open `http://localhost:8000/docs`.
4. Confirm all endpoints are listed.
5. Confirm PostgreSQL container starts successfully.
6. Confirm schema and seed SQL execute on first database volume creation.

## Database Validation

Confirm seeded competitions:

```sql
SELECT code, name FROM competitions ORDER BY code;
```

Expected codes:

```text
BUNDESLIGA
EPL
LALIGA
LIGUE_1
NOR_ELITESERIEN
SERIE_A
UCL
UEL
```

## Provider Coverage Validation

Before Phase 3 model work, confirm or assign backup provider coverage for:

- current odds;
- historical odds;
- xG;
- fixtures and results;
- lineups;
- injuries/suspensions;
- provider timestamps;
- provider audit trail.

Missing historical odds or xG must force `NO BET`.

## Completion Gate

Phase 2 is complete only when:

- Backend runs locally and `/docs` loads.
- Database schema creates successfully.
- All MVP competitions are seeded.
- Historical odds and xG provider coverage is confirmed or assigned to backup provider.
- Auto-betting endpoint returns inactive/hard-locked.
- Domeneshop suitability is documented.
