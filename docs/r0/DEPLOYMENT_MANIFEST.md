# Deployment Manifest — R0 Baseline

This file records the reconciliation baseline. It does not authorize deployment.

| Component | Value |
|---|---|
| FEA canonical main SHA at R0 start | `26bea513ad3596d06d11c49bbb41919284b00b20` |
| PIP canonical main SHA at R0 start | `830be691647a7640964b58fc0da65204866ac9ea` |
| R0 branch | `agent/r0-reconciliation-hardening` |
| Runtime release SHA | `TBD_RECONCILIATION` |
| Runtime release artifact hash | `TBD_RECONCILIATION` |
| Shared contract | `contracts/fea_pip_shadow_contract_v2.schema.json` (proposed, non-operative until approved) |
| Deployment state | `NOT_AUTHORIZED_BY_R0` |
| Recommendation release | `DISABLED` |
| Execution | `DISABLED` |
| Bookmaker execution | `DISABLED` |
| Real-money betting automation | `DISABLED` |

## Closure requirement
Before any later deployment gate, replace all `TBD_RECONCILIATION` fields with evidence-backed values derived from a reviewed Git commit/tag and archived build manifest.
