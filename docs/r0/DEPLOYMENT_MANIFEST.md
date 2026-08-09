# Deployment Manifest — R0 Post-Merge Baseline

This file records the reconciliation baseline. It does not authorize deployment.

| Component | Value |
|---|---|
| FEA canonical main SHA at R0 start | `26bea513ad3596d06d11c49bbb41919284b00b20` |
| PIP canonical main SHA at R0 start | `830be691647a7640964b58fc0da65204866ac9ea` |
| FEA canonical main SHA after R0 merge | `d66a8da77187f661c5b98f8b4f06c902a9b63462` |
| PIP canonical main SHA after R0 merge | `4983fafb6e5c56a1127ca7288fa5783b4c02cdcf` |
| FEA current main SHA after post-merge evidence updates | `f5c5978a989f7fb1c40b4eed3f9ea33ba2d50bd8` |
| PIP current main SHA after rollout hardening | `86b40f50d807809854c9a3cb45fecae1b2a70b0a` |
| R0 source branches | Merged through FEA PR #10 and PIP PR #2 |
| Runtime release SHA | `TBD_RECONCILIATION` |
| Runtime release artifact hash | `TBD_RECONCILIATION` |
| Shared contract | `contracts/fea_pip_shadow_contract_v2.schema.json` v2.0.0; canonical in both repositories, not verified as deployed |
| Deployment state | `NOT_AUTHORIZED_BY_R0` |
| Recommendation release | `DISABLED` |
| Execution | `DISABLED` |
| Bookmaker execution | `DISABLED` |
| Real-money betting automation | `DISABLED` |

## Closure requirement
Before any later deployment gate, replace all `TBD_RECONCILIATION` fields with evidence-backed values derived from a reviewed Git commit/tag and archived build manifest.

## Post-merge verification — 09.08.2026

- Both R0 pull requests are merged and their merge commits are the canonical source references above.
- The public PIP root returns HTTP `403`; directory contents are no longer exposed.
- Protected PIP endpoints return HTTP `401` without credentials, while authenticated `health.php` returns HTTP `200` in GitHub Actions run `31328315903`.
- Runtime files observed on the host predate the R0 merge, so source merge does not establish deployment identity.
- Cross-repository remediation and evidence tracking: `nanotech-solutions-norway/Probability_Intelligence_Platform#3`.
- No credential value was read, printed, or archived; the protected workflow captured no response body and did not follow redirects.
