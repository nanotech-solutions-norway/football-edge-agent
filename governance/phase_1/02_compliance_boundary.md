# Football Edge Intelligence Agent — Compliance Boundary — 01:34, 27.04.2026 Europe/Oslo

## 1. Compliance Position

The Football Edge Intelligence Agent shall operate as a private analytical decision-support tool during MVP. It shall not be marketed, published, monetized, distributed to customers, connected to bookmaker transaction flows, or used as a public gambling recommendation service without separate legal, data-licensing, privacy, consumer-protection, and marketing-claims review.

Norway shall be treated as the primary compliance baseline. Any wider European or international use requires jurisdiction-specific review before commercial activation.

## 2. Allowed MVP Activity

| Activity | Status | Control |
|---|---|---|
| Private probability modelling | Allowed | Internal analytical use only |
| Paper-trading validation | Allowed in later phase | No real-money execution |
| Historical backtesting | Allowed | Requires historical odds and xG |
| Provider feasibility review | Allowed | Must preserve provider audit trail |
| Governance documentation | Allowed | Phase 1 scope |

## 3. Prohibited MVP Activity

| Activity | Status | Rationale |
|---|---|---|
| Public betting tips | Prohibited | Requires legal and marketing review |
| Guaranteed-pick language | Prohibited | Misleading and non-compliant posture |
| Affiliate routing to bookmakers | Prohibited | Commercial gambling linkage |
| Auto-betting activation | Prohibited | Hard-locked during MVP |
| Bookmaker login handling | Prohibited | Transaction and privacy risk |
| Reckless staking or loss chasing | Prohibited | Risk-control violation |
| Unsupported competitions or markets | Prohibited | Outside approved scope |

## 4. Legal Review Trigger

A formal legal review is mandatory before any of the following:

1. Public website launch presenting recommendations.
2. Commercial sale, subscription, or customer-facing deployment.
3. Affiliate, referral, or bookmaker partnership activity.
4. Real-money testing outside strictly controlled personal/private review.
5. Automated or semi-automated bet placement.
6. Collection of user profiles, betting histories, financial data, or bookmaker account credentials.
7. Expansion beyond the approved MVP competitions or markets.

## 5. Responsible-Gambling Boundary

The agent shall not encourage excessive gambling, loss chasing, urgency-based betting, or certainty-based decisions. Recommended language must remain analytical, probabilistic, and risk-aware. The default status is **NO BET**.

## 6. Auto-Betting Lock

Auto-betting may be included only as a future architectural placeholder. It shall remain inactive, disabled by default, unavailable through user interface controls, and protected by configuration gates. No API key, wallet, payment, bookmaker login, or transaction-execution logic may activate auto-betting during MVP.

## 7. Data and Privacy Boundary

Data providers must supply auditable timestamps and usage rights compatible with the project scope. Historical odds and xG are mandatory. Personal data processing must be minimized; any personal data or account-level gambling data requires privacy review before use.

## 8. Approved Scope Statement

The approved Phase 1 compliance boundary is: private analytical decision-support only, Norway as the primary compliance baseline, no guarantees, no auto-betting, no commercial/public launch, no unsupported markets, no unsupported competitions, and no loss-chasing behavior.
