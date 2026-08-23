from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_protected_discovery_workflow_is_sanitized_and_ephemeral():
    workflow = (ROOT / ".github/workflows/pip-protected-fixture-discovery.yml").read_text(encoding="utf-8")
    assert "pip-authenticated-readonly-validation" in workflow
    assert "secrets.ODDS_API_KEY" in workflow
    assert "PIP_SINGLE_PROVIDER_MODE: true" in workflow
    assert "secrets.SOCCERDATA_API_KEY" not in workflow
    assert "SPORTS_GAME_ODDS_ENABLED: false" in workflow
    assert "secrets.SPORTS_GAME_ODDS_KEY" not in workflow
    assert "secrets.SPORTSDATA_IO_KEY" not in workflow
    assert "secrets.API_SPORTS_KEY" not in workflow
    assert "secrets.PIP_VALIDATION_FIXTURE_CODE" in workflow
    assert "retention-days: 1" in workflow
    assert "rm -f --" in workflow
    assert "workflow_dispatch" in workflow


def test_powershell_dispatcher_never_requests_provider_credentials():
    script = (ROOT / "scripts/Invoke-PipProtectedFixtureDiscovery.ps1").read_text(encoding="utf-8")
    assert "ghExecutable workflow run" in script
    assert "ghExecutable run download" in script
    assert "Read-Host" not in script
    assert "ODDS_API_KEY" not in script
    assert "SOCCERDATA_API_KEY" not in script


def test_runner_context_is_not_used_in_job_level_environment():
    workflow_paths = (
        ".github/workflows/pip-protected-fixture-discovery.yml",
        ".github/workflows/pip-authenticated-fixture-validation.yml",
    )
    for workflow_path in workflow_paths:
        workflow = (ROOT / workflow_path).read_text(encoding="utf-8")
        job_preamble = workflow.split("    steps:", maxsplit=1)[0]
        assert "${{ runner.temp }}" not in job_preamble
        assert "RUNNER_TEMP" in workflow


def test_automatic_database_write_is_protected_and_sanitized():
    workflow = (ROOT / ".github/workflows/pip-protected-fixture-discovery.yml").read_text(encoding="utf-8")
    assert "name: pip-automatic-database-write" in workflow
    assert "secrets.PIP_DB_HOST" in workflow
    assert "secrets.PIP_DB_NAME" in workflow
    assert "secrets.PIP_DB_USER" in workflow
    assert "secrets.PIP_DB_PASSWORD" in workflow
    assert "scripts/apply_pip_fixture_registration.py" in workflow
    assert "mysql-connector-python==9.7.0" in workflow
    assert "persist-credentials: false" in workflow
    assert "database_values_logged=false" in workflow
    assert "MYSQL_PWD" not in workflow
