# Football Edge / Atlas — Step 4 Admin Reporting Page Validation Pass Checkpoint

Generated: 12:39, 29.04.2026 Europe/Oslo

## Validation summary

The Step 4 admin reporting page was deployed and validated successfully.

Validated page:

```text
https://www.atlas-ai.no/admin/paper-trading-report.html
```

## Confirmed dashboard output

The page displayed:

```text
Report loaded. Real-money execution remains disabled.
```

## Summary panel

Confirmed values:

```text
Date range = 2026-04-23 to 2026-04-29
Total recommendations = 2
Paper bets = 2
Watchlist = 0
No-bet count = 0
No-bet rate = 0
Open records = 1
Test artifacts = 1
```

## Metrics panel

Confirmed values:

```text
Settled count = 1
Total stake = 1
Profit / loss = 1.1
ROI = 1.1
Yield = 1.1
Average CLV = 0.05
Win rate = 1
Brier score = 0.2401
Log loss = 0.673345
```

## Safety state panel

Confirmed values:

```text
Required safe state = true
Real-money status = disabled_locked_dry_run
Auto-betting enabled = false
Dry run = true
Provider = none
Legal review = false
Compliance review = false
Risk review = false
```

## Artifact / review items

Confirmed known artifact:

```text
paper_trade_id = 1
classification = wrong_token_test_artifact
status = OPEN
```

## Recent records

Confirmed records:

```text
paper_trade_id = 2
status = SETTLED
profit_loss = 1.1000
closing_line_value = 0.050000

paper_trade_id = 1
status = OPEN
notes = manual insomnia negative test with wrong token
```

## Audit events

Confirmed events:

```text
audit_event_id = 3, paper_trade_id = 2, event = paper_trade_settled
audit_event_id = 2, paper_trade_id = 2, event = paper_recommendation_created
audit_event_id = 1, paper_trade_id = 1, event = paper_recommendation_created
```

## Gate decision

Step 4 admin reporting page validation: PASSED.

## Notes

The artifacts table shows horizontal overflow due to narrow display width. This is a UI polish item only and does not affect operational validation.

## Continued exclusions

The following remain disabled / not implemented:

- Real-money execution.
- Auto-betting.
- Provider execution integration.
- Public write forms.
- Frontend-held write tokens.
- Direct frontend database access.

## Next recommended action

Proceed with test-artifact reconciliation policy. Preferred default is to keep `paper_trade_id = 1` as an audit artifact unless a controlled cleanup script is explicitly approved.
