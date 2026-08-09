# Reconciliation & Hardening R0

## Objective
Restore a single reproducible source of truth for Football Edge Agent (FEA) before any further capability expansion.

## R0 boundaries
- GitHub is canonical for source code, schemas, tests, configuration templates, and release manifests.
- Google Drive is canonical for validation evidence, archived test outputs, governance records, and historical handoff material.
- Drive code packages are migration evidence until reviewed and reconciled into GitHub.
- No live endpoint overwrite, deployment, provider mutation, execution enablement, recommendation release, bookmaker execution, or real-money betting is authorized by R0.
- FEA must remain independently operable when PIP is disabled or unavailable.

## Required gates
1. Reconcile current GitHub state against later Drive Phase 5/16 evidence.
2. Repair the Phase 16H secret-scan validator and rerun against preserved evidence.
3. Inventory environment/configuration artifacts without exposing secret values.
4. Adopt a shared FEA/PIP v2 shadow contract.
5. Reconcile the open Phase 3 model PR; do not merge it as-is.
6. Add cross-repository contract, fail-soft, safety-invariant, and release-manifest CI.
7. Prove non-zero comparable multi-provider shadow consensus before advancing Phase 16I.

## Acceptance posture
R0 is complete only when source, contracts, tests, deployment manifest, and archived validation evidence can be traced to explicit Git commits and no unresolved safety or source-authority conflict remains.
