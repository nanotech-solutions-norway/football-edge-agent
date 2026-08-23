# Authenticated PIP Fixture Validation — R0

This workflow supplies the protected consumer-side technical gate for an authenticated PIP v2 fixture response. It is read-only and does not authorize deployment, recommendation release, betting, or bookmaker execution.

## Protected environment

Repository environment: `pip-authenticated-readonly-validation`.

The environment permits deployment jobs only from `main`. Configure these environment secrets manually in GitHub:

- `PIP_API_KEY`
- `PIP_VALIDATION_FIXTURE_CODE`

Never place their values in source, workflow inputs, issue comments, Actions logs, or chat.

## Automatic protected fixture discovery

`pip-protected-fixture-discovery.yml` currently runs under an explicit temporary single-provider exception. It reads only `ODDS_API_KEY` and `PIP_VALIDATION_FIXTURE_CODE`, calls only Odds API, and creates a one-day registration-SQL artifact for the earliest upcoming Norwegian Eliteserien event with head-to-head odds. Soccerdata, SportsGameOdds, SportsData.io, and API-Sports credentials are not bound to the job and those providers are not called. Raw responses, credentials, fixture codes, provider event IDs, team names, and SQL content are not logged.

Single-provider registration is not comparable consensus. Any resulting PIP payload must remain `market_only` or `insufficient_consensus`, must not publish a probability array, and cannot pass the comparable-consensus acceptance gate. Manual review, recommendation-release, betting, and execution locks remain mandatory. Restore the default two-provider registration gate by removing `PIP_SINGLE_PROVIDER_MODE: true` from the workflow.

After the workflow is merged to `main`, the office PC can dispatch, watch, and download the protected artifact without handling provider secrets by running `scripts/Invoke-PipProtectedFixtureDiscovery.ps1`. The SQL is downloaded under the local ignored `data/pip-fixture-discovery` directory for operator review and manual phpMyAdmin import.

## Validation behavior

The workflow sends one authenticated `GET` request to the PIP fixture endpoint without following redirects. The response body is bounded to 1 MB, stored with restricted permissions only in the GitHub-hosted runner temporary directory, validated through FEA's v2 shadow contract gate, and deleted in an unconditional cleanup step.

Actions output is limited to HTTP/content-type status, byte and aggregate counts, pass/review state, fixed safety locks, and `payload_included=false`. Fixture codes, internal keys, provider names, probabilities, audit IDs, validation error details, and response bodies are not logged or uploaded.

## Acceptance boundary

A passing run proves one authenticated non-zero comparable-consensus fixture traversed the FEA contract validator while all execution controls remained disabled. Broader Phase 16I technical acceptance still requires the shadow-period coverage, calibration, degradation, and audit evidence defined in the R0 acceptance record.
