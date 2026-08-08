# Phase 3 PR #8 Reconciliation Plan

## Disposition
PR #8 is a migration source, not a direct merge candidate. It remains draft during R0.

## Preserve and revalidate
- decimal-odds implied-probability helpers
- bookmaker no-vig normalization and margin calculation
- Poisson scoreline/market helpers
- xG input helpers
- Elo/Glicko foundations where independently justified
- Brier score and log-loss utilities
- expected value, edge, fair-odds helpers
- deterministic unit tests and model-version audit fields

## Required changes before canonical integration
- keep fundamental model probability analytically separate from bookmaker probability;
- do not use a fixed bookmaker-probability blend as a production edge signal unless shrinkage weights are learned out-of-sample;
- replace fixed draw-rate assumptions with model/league evidence;
- use chronological walk-forward validation and explicit leakage checks;
- calibrate by market/competition with a hierarchical fallback rather than assuming one global calibration;
- report uncertainty/calibration metadata separately from recommendation policy;
- align market identifiers with the shared contract: `1X2`, `OVER_UNDER_2_5`, `BTTS`;
- keep PIP probability intelligence separate from FEA recommendation policy;
- preserve `NO BET`/quarantine behavior when mandatory data, freshness, or quality gates fail.

## Required validation evidence
- chronological train/validation/test boundaries
- Brier score and log loss
- calibration/reliability evaluation
- leakage audit
- coverage and missing-data behavior
- benchmark against market/no-vig probability without circularly defining model edge
- fail-soft PIP-disabled and PIP-unavailable tests
- execution-lock invariant tests

## Merge strategy
Extract reviewed components into the R0 branch or a child branch, add fresh tests against the current shared contract, and close PR #8 as superseded only after equivalent or improved functionality is represented in the canonical reconciliation PR.
