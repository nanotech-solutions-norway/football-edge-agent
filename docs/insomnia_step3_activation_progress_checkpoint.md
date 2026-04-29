# Football Edge / Atlas — Insomnia Step 3 Activation Progress Checkpoint

Generated: 11:38, 29.04.2026 Europe/Oslo

## Confirmed setup

Insomnia v12.5.0 is operational for Step 3 controlled paper-trading testing.

Confirmed:

- Request 01 URL correction passed.
- Base Environment variable structure passed.
- Direct URL health test passed.
- Bearer token placement using Insomnia Auth option A passed.

## Confirmed requests

### 01 GET Health

Returned:

```json
{
  "status": "ok",
  "service": "football-edge-api",
  "database": "ok",
  "timestamp_utc": "2026-04-29T09:37:44+00:00"
}
```

Status: PASSED.

### 02 GET Safety State

Returned required locked state:

```text
required_safe_state_ok = true
real_betting_status = disabled_locked_dry_run
enabled = false
provider_name = none
dry_run = true
legal_review_completed = false
compliance_review_completed = false
risk_review_completed = false
```

Status: PASSED.

### 03 POST Recommendation — No Token

Returned:

```json
{
  "status": "error",
  "message": "Unauthorized"
}
```

Status: PASSED. Unauthenticated writes are blocked.

## Next requests

Continue with:

```text
04 POST Recommendation — Wrong Token
05 POST Recommendation — Correct Token
06 GET Recommendations
07 POST Settlement — Correct Token
08 GET Results
09 GET Metrics
```

## Security boundary

- API_WRITE_TOKEN must not be placed in URLs.
- API_WRITE_TOKEN must not be pasted into chat, screenshots, GitHub, frontend files, or browser-visible files.
- POST write requests must use Authorization Bearer token only.
- Real-money execution remains disabled.
- Auto-betting remains disabled.
- Re-run SQL safety state check after testing.
- Disable FOOTBALL_EDGE_PAPER_TRADING_ENDPOINTS_ENABLED after the limited activation test.
