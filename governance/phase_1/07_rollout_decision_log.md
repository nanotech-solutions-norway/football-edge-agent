# Football Edge Intelligence Agent — Rollout Decision Log — 01:34, 27.04.2026 Europe/Oslo

## 1. Phase 1 Approved Baseline

The following decisions are approved for Phase 1 and shall be used as the baseline for Phase 2.

| No. | Decision | Status |
|---:|---|---|
| 1 | The agent shall be developed initially as a private analytical decision-support system. | Approved |
| 2 | The agent shall not place bets automatically. | Approved |
| 3 | Auto-betting may be included as later architecture only, but it must remain inactive and hard-locked. | Approved |
| 4 | The agent shall not guarantee outcomes or present football predictions as certain. | Approved |
| 5 | The agent shall not promote betting operators or bookmaker offers during MVP. | Approved |
| 6 | MVP competitions shall include Premier League, La Liga, Bundesliga, Serie A, Ligue 1, UEFA Champions League, UEFA Europa League, and Eliteserien. | Approved |
| 7 | MVP markets shall include 1X2, Over/Under 2.5 Goals, and Both Teams To Score. | Approved |
| 8 | The default recommendation shall be NO BET unless data quality, model confidence, positive expected value, and risk controls are satisfied. | Approved |
| 9 | Recommendation statuses shall be BET, WATCHLIST, and NO BET only. | Approved |
| 10 | Required recommendation output shall include model probability, bookmaker probability, probability comparison chart, expected value, confidence, risk, recommendation, and audit trail. | Approved |
| 11 | Simple hit rate shall not be the primary success metric. | Approved |
| 12 | Brier score, log loss, calibration curve, CLV, ROI, yield, maximum drawdown, no-bet rate, and data quality shall be tracked. | Approved |
| 13 | Historical odds are mandatory. | Approved |
| 14 | xG data are mandatory. | Approved |
| 15 | Provider approval requires historical odds and xG coverage through either one provider or a combined provider stack. | Approved |
| 16 | Commercial/public launch shall require separate legal, privacy, data-licensing, and marketing-claims review. | Approved |
| 17 | Maximum bankroll values shall be implemented at 1.00% per bet, 1.00% pilot stake ceiling, 3.00% daily exposure, 8.00% weekly exposure, and 2.00% correlated exposure. | Approved |
| 18 | Loss chasing and reckless staking are prohibited. | Approved |

## 2. Repository Implementation Decision

| Item | Decision |
|---|---|
| Repository | nanotech-solutions-norway/football-edge-agent |
| Phase 1 folder | governance/phase_1/ |
| File format | Markdown |
| Governance status | Baseline approved for Phase 2 planning |
| Norwegian elite-league naming | Eliteserien only |

## 3. Phase 1 Completion Checklist

| Control | Result |
|---|---|
| Seven Markdown governance files created | Passed |
| Agent defined as private analytical decision-support | Passed |
| Norway set as primary compliance baseline | Passed |
| Public/commercial use blocked pending legal review | Passed |
| MVP competitions defined exactly | Passed |
| Eliteserien used consistently | Passed |
| MVP markets defined exactly | Passed |
| Historical odds marked mandatory | Passed |
| xG marked mandatory | Passed |
| BET / WATCHLIST / NO BET statuses defined | Passed |
| NO BET policy explicit and conservative | Passed |
| Probability comparison chart requirement included | Passed |
| Success metrics defined | Passed |
| Risk and bankroll maximums included | Passed |
| Auto-betting inactive and hard-locked | Passed |

## 4. Required Phase 2 Prompt

Proceed to Phase 2: MVP data architecture and backend foundation. Provide detailed step-by-step implementation instructions, including GitHub repository structure, database schema, API endpoints, environment variables, provider setup, Domeneshop hosting/DNS assessment, inactive auto-betting controls, historical odds ingestion, xG data ingestion, recommendation output schema, model-probability vs bookmaker-probability comparison-chart logic, governance-policy enforcement, and validation checklist. Do not activate auto-betting. Preserve NO BET as the default recommendation. Use Eliteserien only for Norwegian elite-league coverage.

## 5. Change-Control Rule

Any change to competitions, markets, data requirements, compliance posture, bankroll maximums, provider requirements, recommendation statuses, or auto-betting controls shall require a controlled governance revision. Changes shall be logged before implementation.
