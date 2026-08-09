# Source Authority — R0

## Canonical authorities
1. **GitHub main / approved release tag** — application source code, schemas, tests, CI, configuration templates, and release definitions.
2. **Google Drive controlled evidence archive** — validation outputs, test archives, manifests, hashes, reports, governance records, and historical transfer material.
3. **Runtime/server configuration** — operational secrets and provider credentials only. Secrets must not be treated as Drive or GitHub source material.

## Conflict resolution
- A Drive code package that is newer than GitHub is not automatically canonical source. It must be reviewed, sanitized, tested, and reconciled into a controlled GitHub branch/PR.
- A technical gate result and an operator acceptance are separate statuses. Operator acceptance does not silently convert BLOCKED/FAIL into PASS.
- Historical rollout instructions remain historical evidence unless explicitly reclassified through current governance.
- When source and evidence disagree, preserve both records, record the conflict, and resolve it through an R0 reconciliation PR rather than silently merging states.

## Required phase status dimensions
Every future phase/gate record should state independently:
- technical_gate: PASS | PARTIAL_PASS | BLOCKED | FAIL
- safety_gate: PASS | FAIL
- artifact_state: CREATED | VALIDATED | ARCHIVED
- operator_decision: ACCEPTED | OVERRIDDEN | HELD | NONE
- deployment_state: NOT_DEPLOYED | SHADOW | INTERNAL_LIVE
