# Football Edge / Atlas — Weekly Validation Workflow — 12:52, 29.04.2026 Europe/Oslo

## Purpose

This workflow defines the weekly paper-trading validation process for Football Edge / Atlas. It is designed to produce a repeatable, auditable weekly report from the read-only reporting layer while keeping all real-money and provider-execution functions disabled.

## Operating posture

Required `.env` posture during weekly reporting:

```env
FOOTBALL_EDGE_REPORTING_ENDPOINTS_ENABLED=true
FOOTBALL_EDGE_PAPER_TRADING_ENDPOINTS_ENABLED=false
FOOTBALL_EDGE_REAL_BETTING_ENABLED=false
FOOTBALL_EDGE_DRY_RUN=true
FOOTBALL_EDGE_AUTO_BETTING_ENABLED=false
```

## Weekly cadence

Recommended execution window:

```text
Every Monday morning for the previous Monday–Sunday period.
```

Example date range:

```text
from = 2026-04-23
to   = 2026-04-29
```

## Required endpoint checks

Run these first:

```text
GET https://www.atlas-ai.no/api/health
GET https://www.atlas-ai.no/api/system/safety-state
GET https://www.atlas-ai.no/api/reporting/paper-trading/weekly?from=YYYY-MM-DD&to=YYYY-MM-DD
GET https://www.atlas-ai.no/api/reporting/paper-trading/artifacts
GET https://www.atlas-ai.no/api/reporting/paper-trading/audit
GET https://www.atlas-ai.no/api/reporting/paper-trading/export.csv?from=YYYY-MM-DD&to=YYYY-MM-DD
```

## Required SQL safety check

Run in phpMyAdmin before finalizing the weekly report:

```sql
SELECT 
    `enabled`,
    `provider_name`,
    `dry_run`,
    `legal_review_completed`,
    `compliance_review_completed`,
    `risk_review_completed`
FROM `auto_betting_control`
ORDER BY `control_id` DESC
LIMIT 1;
```

Required result:

```text
enabled = 0
provider_name = none
dry_run = 1
legal_review_completed = 0
compliance_review_completed = 0
risk_review_completed = 0
```

## Metrics to record

Record the following from the weekly endpoint:

```text
Date range
Total recommendations
Paper bet count
Watchlist count
No-bet count
No-bet rate
Open count
Settled recommendation count
Test artifact count
Settled count
Total stake
Total profit/loss
ROI
Yield
Average CLV
Win rate
Brier score
Log loss
Safety-state status
Real-money execution status
```

## Acceptance criteria

The weekly report may be accepted only if:

- reporting endpoint returns `status = ok`;
- safety state returns `required_safe_state_ok = true`;
- real-money execution remains `false`;
- auto-betting remains disabled;
- provider remains `none`;
- SQL safety check returns the required locked values;
- all known test artifacts are explicitly identified;
- CSV export is archived locally or in approved non-public storage.

## Stop conditions

Stop the validation process and escalate if:

- `required_safe_state_ok` is false;
- real-money execution is true;
- any review flag is unexpectedly true;
- provider is not `none`;
- Step 3 paper-trading write endpoints are unexpectedly active;
- export contains unexpected sensitive data;
- public frontend exposes write controls or tokens.

## Output artifacts

Each weekly cycle should produce:

```text
1. Weekly validation report markdown/PDF/DOCX
2. CSV export from /api/reporting/paper-trading/export.csv
3. Screenshot of admin reporting page
4. SQL safety-check result note
5. Artifact/reconciliation note if applicable
```

Do not commit generated operational exports to GitHub.
