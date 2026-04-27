# Football Edge Intelligence Agent — Agent Scope — 01:34, 27.04.2026 Europe/Oslo

## 1. Purpose

The Football Edge Intelligence Agent shall be developed as a private analytical decision-support system for probability-calibrated football market analysis. It shall support disciplined evaluation of selected football betting markets by comparing model probability against bookmaker-implied probability and applying conservative no-bet controls.

The agent shall not present football outcomes as certain, shall not encourage excessive staking, shall not place bets, and shall not operate as a public gambling service during MVP. Its default posture is **NO BET** unless all data, model, edge, risk, and governance requirements are satisfied.

## 2. Operating Classification

| Classification | Phase 1 Decision | Implementation Position |
|---|---|---|
| Private analytical decision-support tool | Approved | MVP scope |
| Probability education and model-evaluation aid | Approved | Allowed when framed as analysis |
| Commercial betting assistant | Not approved | Requires legal review before activation |
| Public-facing gambling recommendation service | Not approved | Out of scope for MVP |
| Affiliate or bookmaker-routing product | Not approved | Out of scope for MVP |
| Automated betting system | Not approved | Auto-betting remains inactive and hard-locked |

## 3. Core Scope

The agent shall analyze selected international football competitions and Eliteserien using structured probability methods, current market prices, historical odds, xG-derived indicators, fixture context, team-form inputs, lineups, injuries/suspensions, and timestamped provider records.

The agent may return one of three statuses only:

| Status | Meaning | Default Handling |
|---|---|---|
| **BET** | Positive expected value, sufficient edge, fresh data, acceptable model confidence, and risk controls passed | Permitted only when every control passes |
| **WATCHLIST** | Potential value exists but one or more revalidation items remain open | Recheck before any decision |
| **NO BET** | Insufficient edge, confidence, data quality, freshness, or legal clarity | Default system output |

## 4. Prohibited Functions

The agent must not:

1. Guarantee match outcomes or expected returns.
2. Use certainty-based betting language in recommendations.
3. Recommend loss chasing or stake escalation after losses.
4. Recommend betting an entire bankroll or breaching exposure caps.
5. Place bets automatically.
6. Activate auto-betting functionality during MVP.
7. Route users to betting operators or promote bookmaker offers.
8. Recommend unsupported competitions or unsupported markets.
9. Recommend accumulators/parlays during MVP.
10. Recommend in-play/live markets during MVP.
11. Recommend correct-score, player-prop, cards, corners, or other non-MVP markets during MVP.
12. Produce recommendations from stale odds, incomplete datasets, or missing provider timestamps.
13. Invent lineups, injuries, suspensions, xG values, historical odds, current odds, or fixture data.
14. Treat historical performance as proof of future profitability.
15. Launch publicly or commercially without legal, data-licensing, privacy, and marketing-claims review.

## 5. Mandatory Data Position

A final **BET** status may be issued only when the following data basis exists and is auditable:

| Data Element | Requirement | BET Eligibility Impact |
|---|---|---|
| Current odds | Mandatory | Missing/stale odds force NO BET |
| Historical odds | Mandatory | Missing historical odds force NO BET |
| xG data | Mandatory | Missing xG force NO BET |
| Fixtures and results | Mandatory | Missing fixture/result context force NO BET |
| Lineups | Mandatory near kickoff where available | Missing confirmed lineup may force WATCHLIST or NO BET |
| Injuries/suspensions | Mandatory | Missing material injury data force WATCHLIST or NO BET |
| Provider timestamps | Mandatory | Missing timestamps force NO BET |
| Provider audit trail | Mandatory | Missing audit trail invalidates recommendation |

Historical odds and xG are non-negotiable MVP requirements. Any competition, market, or fixture without sufficient historical odds and xG support shall be disabled or downgraded to **NO BET**.

## 6. Required Recommendation Output Standard

Every recommendation output shall include:

1. Match and competition summary.
2. Market analyzed.
3. Odds, bookmaker timestamp, and data freshness statement.
4. Model probability.
5. Bookmaker raw implied probability.
6. Bookmaker no-vig probability.
7. Comparison chart showing model probability versus bookmaker probability.
8. Expected value calculation.
9. Edge calculation.
10. Model confidence and uncertainty factors.
11. Risk-control status.
12. Recommendation status: **BET**, **WATCHLIST**, or **NO BET**.
13. Stake guidance only if every BET control passes and only within maximum bankroll limits.
14. Audit trail including model version, provider identifiers, timestamps, and data-quality status.
15. Responsible-gambling note where relevant.

## 7. Required Probability Comparison Chart

Every analyzed market shall include this minimum comparison chart or an equivalent rendered visualization:

| Market | Selection | Model Probability | Bookmaker Raw Implied Probability | Bookmaker No-Vig Probability | Edge | Status |
|---|---|---:|---:|---:|---:|---|
| Example | Example | To be calculated | To be calculated | To be calculated | To be calculated | BET / WATCHLIST / NO BET |

The agent shall clearly distinguish between a likely sporting outcome and a value-positive market price. A likely outcome is not automatically a bet.

## 8. Auto-Betting Lock

Auto-betting may be referenced in later architecture only as an inactive, hard-locked module. Phase 1 approval does not permit automated execution, transaction routing, deposit workflows, bookmaker login handling, or operator integration.

## 9. Approved Phase 1 Baseline

| Governance Item | Approved Baseline |
|---|---|
| Project | Football Edge Intelligence Agent |
| Purpose | Probability-calibrated international football betting intelligence agent |
| Operating posture | Private analytical decision-support only unless later legally approved |
| Default recommendation | **NO BET** unless data quality, positive expected value, edge, risk controls, and governance checks are satisfied |
| MVP competitions | Premier League; La Liga; Bundesliga; Serie A; Ligue 1; UEFA Champions League; UEFA Europa League; Eliteserien |
| MVP markets | 1X2; Over/Under 2.5 Goals; Both Teams To Score |
| Mandatory data | Current odds; historical odds; xG; fixtures; results; lineups; injuries/suspensions; timestamps; provider audit trail |
| Auto-betting | May exist as a later architectural concept only; inactive and hard-locked during MVP |
| Recommendation statuses | BET; WATCHLIST; NO BET |

## 10. Phase 1 Scope Approval

Phase 1 is approved only for governance design, feasibility control, and specification of the operating boundary. No backend coding, API integration, auto-betting activation, public launch, or commercial deployment is approved under this document.
