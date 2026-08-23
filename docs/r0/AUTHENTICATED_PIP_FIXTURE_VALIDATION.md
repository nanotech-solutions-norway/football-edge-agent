# Authenticated PIP Fixture Validation — R0

This workflow supplies the protected consumer-side technical gate for an authenticated PIP v2 fixture response. It is read-only and does not authorize deployment, recommendation release, betting, or bookmaker execution.

## Protected environment

Repository environment: `pip-authenticated-readonly-validation`.

The environment permits deployment jobs only from `main`. Configure these environment secrets manually in GitHub:

- `PIP_API_KEY`
- `PIP_VALIDATION_FIXTURE_CODE`

Never place their values in source, workflow inputs, issue comments, Actions logs, or chat.

## Automatic protected fixture discovery

`pip-protected-fixture-discovery.yml` reads `ODDS_API_KEY`, `SOCCERDATA_API_KEY`, and `PIP_VALIDATION_FIXTURE_CODE` only inside this protected environment. SportsGameOdds, SportsData.io, and API-Sports are disabled by policy and are not called. The workflow selects the earliest upcoming Norwegian Eliteserien event with available head-to-head odds and requires an unambiguous same-home/same-away match from Soccerdata API. It normalizes provider metadata and creates a one-day registration-SQL artifact. Raw responses, credentials, fixture codes, provider event IDs, team names, and SQL content are not logged. A missing or ambiguous required second-provider match fails closed and creates no artifact; disabled providers are never fabricated as evidence.

After the workflow is merged to `main`, the office PC can dispatch, watch, and download the protected artifact without handling provider secrets by running `scripts/Invoke-PipProtectedFixtureDiscovery.ps1`. The SQL is downloaded under the local ignored `data/pip-fixture-discovery` directory for operator review and manual phpMyAdmin import.

## Validation behavior

The workflow sends one authenticated `GET` request to the PIP fixture endpoint without following redirects. The response body is bounded to 1 MB, stored with restricted permissions only in the GitHub-hosted runner temporary directory, validated through FEA's v2 shadow contract gate, and deleted in an unconditional cleanup step.

Actions output is limited to HTTP/content-type status, byte and aggregate counts, pass/review state, fixed safety locks, and `payload_included=false`. Fixture codes, internal keys, provider names, probabilities, audit IDs, validation error details, and response bodies are not logged or uploaded.

## Acceptance boundary

A passing run proves one authenticated non-zero comparable-consensus fixture traversed the FEA contract validator while all execution controls remained disabled. Broader Phase 16I technical acceptance still requires the shadow-period coverage, calibration, degradation, and audit evidence defined in the R0 acceptance record.
