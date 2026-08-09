# Current State — R0 Post-Merge

## GitHub main
- FEA R0 merge SHA: `d66a8da77187f661c5b98f8b4f06c902a9b63462`.
- PIP R0 merge SHA: `4983fafb6e5c56a1127ca7288fa5783b4c02cdcf`.
- FEA current main SHA after post-merge evidence updates: `f5c5978a989f7fb1c40b4eed3f9ea33ba2d50bd8`.
- PIP current main SHA after rollout hardening: `86b40f50d807809854c9a3cb45fecae1b2a70b0a`.
- The shared v2 contract, consumer-side validation/quarantine, reconciled research-only probability module, and R0 tests are canonical source on `main`.
- Auto-betting remains disabled and hard-locked.
- PR #8 remains a draft migration source and MUST NOT be merged as-is.

## Evidence boundary
Selected non-secret Phase 3 and Phase 16 implementation material has been reconciled and merged through R0. Google Drive remains canonical for archived validation evidence and historical transfer material. Drive recency does not establish deployed runtime identity.

## Current technical blockers
- Deployed runtime Git SHA and release artifact hash remain `TBD_RECONCILIATION`.
- Non-zero comparable multi-provider shadow consensus has not yet been proven in the preserved Phase 16G/16H evidence reviewed for R0.
- PIP authenticated health is verified, but authenticated fixture output and the complete FEA/PIP shadow path are not yet validated.
- Observed PIP runtime PHP files predate the R0 source merge and are not mapped to a reviewed Git release artifact.
- Phase 16I may be prepared historically, but is not accepted by R0 without technical validation evidence.

## Closed R0 source gates
- The Phase 16H keyword-based secret-scan false positive is remediated by value-aware scanning; the original failed evidence remains preserved.
- FEA/PIP market and selection identifiers are synchronized through the byte-identical shared v2 contract.
- Offline contract, quarantine, execution-lock, probability-module, and cross-repository regression checks passed on the merged R0 heads.
- PIP directory indexing is disabled and protected authenticated health validation passed with HTTP `200` in GitHub Actions run `31328315903` without capturing a response body.

## Safety posture
- Manual review required.
- Execution disabled.
- Recommendation release disabled for shadow integration.
- No public write endpoint authorized.
- No bookmaker execution authorized.
