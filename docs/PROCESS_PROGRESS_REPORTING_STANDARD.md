# Football Edge Agent Process Progress Reporting Standard

**Status:** APPROVED  
**Effective:** 21:29, 08.08.2026 Europe/Oslo

## Scope

This standard applies to every current and future Football Edge Agent process, including planning, implementation, testing, validation, deployment, reporting, remediation, transfer, continuation, and closure.

## Mandatory operator-facing progress bar

After each discrete process or major work step, display a cumulative process status bar:

```text
Process status: [██████░░░░] 60% — <brief status>
```

Use a 10-character bar. The numeric percentage is authoritative.

## Calculation rules

1. State or resolve the applicable completion target before calculating progress.
2. Use the approved project plan and verified evidence gates as the denominator.
3. Approved project-specific milestone weights supersede any generic weighting.
4. If no approved weighting exists, define evidence-based milestone weights totaling 100% before using the percentage operationally.
5. Count a milestone as complete only when its evidence and acceptance marker are verified.
6. Partial progress is allowed only for independently defined, verifiable substeps.
7. Failed, blocked, or unverified work does not increase the percentage.
8. Rework increases progress only when it closes a previously incomplete evidence gate.
9. Do not calculate progress from elapsed time, number of messages, tool calls, files, or subjective effort.
10. When scope changes, record the old target and new target and recalculate explicitly.
11. Round the displayed percentage to the nearest whole number.
12. Do not report 100% until closure evidence, validation, rollback/recovery evidence where relevant, documentation, and operator handoff are complete for the stated target.

## Reporting cadence

The compact status bar is mandatory after each discrete process or major work step. It is not restricted to a standalone status command.

A standalone `Status` command may return an expanded block containing:

```text
STATUS — Football Edge Agent
Target: <completion target>
Progress: [████████░░] 80%
Completed: <short description>
Ongoing: <short description>
Remaining: <short description>
Next gate: <next evidence gate>
Safety: <preserved safety state>
```

## Safety boundary

Progress is informational only. A percentage never authorizes real-money betting, auto-betting, bookmaker execution, deployment, provider mutation, write enablement, or any other action requiring a separate approval or safety gate. Existing Football Edge Agent safety controls remain authoritative.

## Continuity requirements

Carry the current target, percentage, last completed process, ongoing process, remaining process, and next evidence gate into:

- canonical status records;
- transfer packs;
- continuation prompts;
- rollout instructions that govern current/future work;
- validation records;
- session-close or handoff records.

Historical evidence documents should not be rewritten solely to retrofit the rule. Current canonical records must identify this standard as the superseding reporting rule.
