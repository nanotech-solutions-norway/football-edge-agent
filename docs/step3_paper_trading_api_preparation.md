# Football Edge / Atlas — Step 3 Paper-Trading API Preparation

Generated: 21:27, 28.04.2026 Europe/Oslo

## Objective

Prepare a controlled paper-trading API layer for simulated recommendation logging, result settlement, and validation metrics. The implementation remains non-execution and must preserve the locked dry-run safety state.

## Mandatory constraints

- Real-money execution remains disabled.
- Automation remains disabled.
- Provider execution integration remains disabled.
- All write endpoints must require a server-side write token.
- Frontend pages must not expose write tokens.
- Public unauthenticated forms must not submit paper-trading entries.
- API must re-check `auto_betting_control` before every write operation.
- Writes must fail closed if the safety state is not locked.

## Environment additions for private `.env`

Add only on the private Domeneshop backend server, not in GitHub:

```env
FOOTBALL_EDGE_PAPER_TRADING_ENDPOINTS_ENABLED=false
API_WRITE_TOKEN=GENERATE_SERVER_SIDE_SECRET
```

Initial production posture:

```env
FOOTBALL_EDGE_PAPER_TRADING_ENDPOINTS_ENABLED=false
```

Enable only after local/manual validation:

```env
FOOTBALL_EDGE_PAPER_TRADING_ENDPOINTS_ENABLED=true
```

## Proposed endpoints

### Read/report endpoints

```text
GET /api/paper-trading/recommendations
GET /api/paper-trading/results
GET /api/paper-trading/metrics
```

### Controlled write endpoints

```text
POST /api/paper-trading/recommendations
POST /api/paper-trading/results
```

Write endpoints must require:

```http
Authorization: Bearer <server-side write token>
Content-Type: application/json
```

## Recommendation payload

```json
{
  "recommendation_id": null,
  "fixture_id": null,
  "model_version": "football-edge-v0.3.0",
  "competition_key": "EPL",
  "market": "1X2",
  "selection": "Home",
  "recommendation": "PAPER_BET",
  "confidence": "medium",
  "decimal_odds": 2.1000,
  "model_probability": 0.510000,
  "bookie_probability": 0.476190,
  "edge": 0.033810,
  "expected_value": 0.071000,
  "simulated_stake": 1.0000,
  "minimum_acceptable_odds": 2.0000,
  "notes": "manual paper-trading validation"
}
```

## Settlement payload

```json
{
  "paper_trade_id": 1,
  "fixture_id": null,
  "result_status": "SETTLED",
  "selection_won": true,
  "odds_taken": 2.1000,
  "closing_odds": 2.0000,
  "stake": 1.0000
}
```

## Metric calculations

### Brier score

```text
mean((predicted_probability - actual_outcome)^2)
```

### Log loss

```text
-mean(actual_outcome * ln(p) + (1 - actual_outcome) * ln(1 - p))
```

Use probability clamp:

```text
p = min(max(p, 0.000001), 0.999999)
```

### ROI

```text
sum(profit_loss) / sum(stake)
```

### Yield

For this paper-trading pilot, yield is equivalent to ROI unless later separated by turnover methodology.

### Closing-line value

```text
(decimal_odds / closing_odds) - 1
```

### No-execution rate

```text
total_no_execution_decisions / total_fixtures_reviewed
```

## Validation sequence

1. Keep paper-trading disabled and confirm `/api/paper-trading/recommendations` still returns disabled.
2. Deploy Step 3 code privately.
3. Add private `API_WRITE_TOKEN` to `.env`.
4. Keep `FOOTBALL_EDGE_PAPER_TRADING_ENDPOINTS_ENABLED=false`.
5. Confirm disabled behavior remains.
6. Enable paper-trading only for test window.
7. Submit one controlled paper recommendation using a non-browser tool.
8. Submit one settlement for that recommendation.
9. Validate metrics endpoint.
10. Disable the endpoint again unless active testing is required.
11. Re-run SQL safety state check.

## Go/no-go criteria

Proceed only if:

- API writes require a valid token.
- No credentials are exposed in frontend or GitHub.
- Safety state remains locked.
- All records are clearly marked as simulated paper-trading.
- No provider execution exists.

Stop if:

- Any write works without token.
- Any frontend file contains token or credentials.
- Safety state changes.
- Any route can trigger real-money execution.
