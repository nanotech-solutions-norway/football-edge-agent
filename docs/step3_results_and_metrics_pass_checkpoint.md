# Football Edge / Atlas — Step 3 Results and Metrics Pass Checkpoint

Generated: 12:08, 29.04.2026 Europe/Oslo

## Validation summary

The Step 3 controlled paper-trading result readback and metrics endpoint validation passed.

## 08 GET Results

Returned:

```text
status = ok
count = 1
```

Confirmed settlement row:

```text
settlement_id = 1
paper_trade_id = 2
result_status = SETTLED
selection_won = 1
odds_taken = 2.1000
closing_odds = 2.0000
stake = 1.0000
profit_loss = 1.1000
closing_line_value = 0.050000
settled_at = 2026-04-29 12:02:23
```

## 09 GET Metrics

Returned:

```text
status = ok
settled_count = 1
total_stake = 1
total_profit_loss = 1.1000000000000001
roi = 1.1000000000000001
yield_value = 1.1000000000000001
average_clv = 0.050000000000000003
win_rate = 1
brier_score = 0.24009999999999998
log_loss = 0.67334455326376563
real_money_execution_enabled = false
```

The floating-point precision artifacts are acceptable and correspond operationally to:

```text
profit_loss = 1.1
roi = 1.1
yield_value = 1.1
average_clv = 0.05
brier_score = 0.2401
```

## Gate decision

- Result readback endpoint: PASSED.
- Metrics endpoint: PASSED.
- Real-money execution remained false: PASSED.

## Immediate required post-test action

Disable paper-trading endpoints in the private server `.env`:

```env
FOOTBALL_EDGE_PAPER_TRADING_ENDPOINTS_ENABLED=false
```

Then confirm the following return disabled:

```text
GET /api/paper-trading/recommendations
GET /api/paper-trading/results
GET /api/paper-trading/metrics
```

Finally, re-run SQL safety-state check:

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

Required values:

```text
enabled = 0
provider_name = none
dry_run = 1
legal_review_completed = 0
compliance_review_completed = 0
risk_review_completed = 0
```
