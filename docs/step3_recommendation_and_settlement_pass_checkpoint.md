# Football Edge / Atlas — Step 3 Recommendation and Settlement Pass Checkpoint

Generated: 12:03, 29.04.2026 Europe/Oslo

## Validation summary

The Step 3 controlled paper-trading recommendation and settlement tests passed.

## 06 GET Recommendations

Returned:

```text
status = ok
count = 2
```

Confirmed active positive-token test record:

```text
paper_trade_id = 2
model_version = football-edge-v0.3.0
competition_key = EPL
market = 1X2
selection = Home
recommendation = PAPER_BET
auto_betting_enabled = 0
status = OPEN
```

A prior test artifact remains present:

```text
paper_trade_id = 1
notes = manual insomnia negative test with wrong token
status = OPEN
```

This row should be treated as an audit/test artifact unless manually cleaned or reconciled later.

## 07 POST Settlement — Correct Token

Request settled the intended positive-token test record:

```text
paper_trade_id = 2
result_status = SETTLED
selection_won = true
odds_taken = 2.1
closing_odds = 2.0
stake = 1.0
```

Returned:

```json
{
  "status": "ok",
  "message": "Paper-trading result logged. No real-money execution occurred.",
  "settlement_id": 1,
  "profit_loss": 1.1000000000000001,
  "closing_line_value": 0.050000000000000044,
  "real_money_execution_enabled": false
}
```

## Gate decision

- Readback of paper recommendations: PASSED.
- Settlement write with valid token: PASSED.
- Real-money execution flag remained false: PASSED.
- Auto-betting flag remained disabled in recommendation row: PASSED.

## Next steps

Proceed to:

```text
08 GET Results
09 GET Metrics
```

After metrics validation, immediately disable:

```env
FOOTBALL_EDGE_PAPER_TRADING_ENDPOINTS_ENABLED=false
```

Then re-run SQL safety-state check.
