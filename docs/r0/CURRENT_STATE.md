# Current State — R0 Baseline

## GitHub main
- FEA main baseline SHA: `26bea513ad3596d06d11c49bbb41919284b00b20`.
- Core application code remains primarily Phase 2; several provider/data routes are placeholders.
- Auto-betting remains disabled and hard-locked.
- Open PR #8 contains a Phase 3 probability-engine scaffold and successful historical CI runs, but it is stale relative to later Drive evidence and MUST NOT be merged as-is.

## Later validated/tested evidence outside GitHub main
Google Drive contains later PIP/FEA integration evidence including PIP Phase 5 completion and Phase 16 provider-consensus/shadow-integration work through Phase 16H. Those artifacts are evidence and migration inputs, not canonical GitHub source until reconciled.

## Current technical blockers
- GitHub/runtime/evidence drift.
- Phase 16H outer acceptance validator has a keyword-based secret-scan false-positive defect.
- Non-zero comparable multi-provider shadow consensus has not yet been proven in the preserved Phase 16G/16H evidence reviewed for R0.
- FEA/PIP market/schema identifiers have drifted.
- Phase 16I may be prepared historically, but is not accepted by R0 without technical validation evidence.

## Safety posture
- Manual review required.
- Execution disabled.
- Recommendation release disabled for shadow integration.
- No public write endpoint authorized.
- No bookmaker execution authorized.
