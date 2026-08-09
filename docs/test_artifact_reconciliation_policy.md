# Football Edge / Atlas — Test-Artifact Reconciliation Policy

Generated: 12:44, 29.04.2026 Europe/Oslo

## Policy decision

The controlled test artifact below must be retained as an audit artifact unless a future explicit cleanup decision is approved:

```text
paper_trade_id = 1
classification = wrong_token_test_artifact
status = OPEN
notes = manual insomnia negative test with wrong token
```

## Rationale

The artifact should remain in the database because it preserves the security-test audit trail from the Step 3 wrong-token anomaly and subsequent re-test. The reporting layer correctly identifies this record as a test artifact, and it does not affect settled performance metrics because it is not settled.

## Operational handling

The reporting layer must continue to classify this record separately from normal settled paper-trading performance.

Required treatment:

```text
Include in audit/reporting visibility: yes
Include in total recommendation count: yes
Include in test artifact count: yes
Include in settled performance metrics: no
Include in ROI/yield/Brier/log-loss calculations: no unless settled through an approved reconciliation process
Delete automatically: no
```

## Current known artifact

```text
paper_trade_id = 1
created_at / recommendation_timestamp = 2026-04-29 11:53:36
model_version = football-edge-v0.3.0
competition_key = EPL
market = 1X2
selection = Home
recommendation = PAPER_BET
auto_betting_enabled = 0
status = OPEN
notes = manual insomnia negative test with wrong token
```

## Valid settled control record

The valid positive-token test record remains:

```text
paper_trade_id = 2
status = SETTLED
settlement_id = 1
profit_loss = 1.1000
closing_line_value = 0.050000
```

## Reconciliation rule

Do not remove or modify `paper_trade_id = 1` unless all of the following are true:

1. A specific cleanup decision is documented.
2. A backup/export exists before mutation.
3. SQL safety check has passed immediately before cleanup.
4. Cleanup SQL is reviewed before execution.
5. Cleanup is logged in project documentation.
6. SQL safety check passes after cleanup.

## Approved default state

No database mutation is required.

Step 4 reporting should continue with:

```env
FOOTBALL_EDGE_REPORTING_ENDPOINTS_ENABLED=true
FOOTBALL_EDGE_PAPER_TRADING_ENDPOINTS_ENABLED=false
```

## Continued exclusions

The following remain disabled / not implemented:

- Real-money execution.
- Auto-betting.
- Provider execution integration.
- Public write forms.
- Frontend-held write tokens.
- Direct frontend database access.

## Review cadence

Review this policy during weekly paper-trading validation reports or whenever a new test artifact is created.
