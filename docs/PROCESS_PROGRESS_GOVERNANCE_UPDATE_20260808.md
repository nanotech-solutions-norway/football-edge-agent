# Football Edge Agent Process Progress Governance Update — 21:29, 08.08.2026

**Classification:** APPROVED  
**Decision type:** Operator governance instruction  
**Scope:** Football Edge Agent, all current and future workstreams

## Decision

The operator requires a cumulative process status bar, expressed as a percentage, after every discrete process or major work step.

Canonical display format:

```text
Process status: [██████░░░░] 60% — <brief status>
```

The percentage remains evidence-weighted against the approved completion target. Failed, blocked, or unverified work does not increase progress. Scope changes require explicit recalculation. A progress percentage does not authorize betting, execution, deployment, write enablement, or any safety-sensitive action.

## Supersession

Any prior Football Edge Agent instruction that limits visible progress bars to a standalone `Status` command is superseded for this project. The standalone `Status` command remains available for an expanded completed/ongoing/remaining report.

## Repository implementation

- Root `AGENTS.md` added as the mandatory agent instruction surface.
- `docs/PROCESS_PROGRESS_REPORTING_STANDARD.md` added as the canonical reporting standard.
- `README.md` and current implementation/continuation surfaces must reference the standard.
- Historical evidence and archived rollout artifacts remain unchanged unless they are reactivated as current canonical instructions.

## Validation criteria

PASS when:

1. repository instructions require the compact progress bar after each major process;
2. current canonical documentation references the reporting standard;
3. continuation/handoff instructions carry the same rule;
4. existing safety posture remains unchanged;
5. historical evidence remains distinguishable from current governance.

## Safety state

No betting, execution, bookmaker, deployment, provider, credential, or production-write authorization is created by this governance change.
