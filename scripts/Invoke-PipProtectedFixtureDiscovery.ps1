[CmdletBinding()]
param(
    [string]$Repository = 'nanotech-solutions-norway/football-edge-agent',
    [string]$Ref = 'main',
    [string]$OutputDirectory
)

$ErrorActionPreference = 'Stop'
$workflow = 'pip-protected-fixture-discovery.yml'
$artifactName = 'pip-fixture-registration-sql'
$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$repositoryRoot = Split-Path -Parent $scriptDirectory
if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $OutputDirectory = Join-Path $repositoryRoot 'data\pip-fixture-discovery'
}
$OutputDirectory = [System.IO.Path]::GetFullPath($OutputDirectory)

$ghCommand = Get-Command gh -ErrorAction SilentlyContinue
if ($null -eq $ghCommand) {
    $knownGh = 'C:\Users\meyer\AppData\Local\Microsoft\WinGet\Packages\GitHub.cli_Microsoft.Winget.Source_8wekyb3d8bbwe\bin\gh.exe'
    if (-not (Test-Path -LiteralPath $knownGh)) {
        throw 'GitHub CLI was not found. Install or add gh.exe to PATH.'
    }
    $ghExecutable = $knownGh
}
else {
    $ghExecutable = $ghCommand.Source
}

& $ghExecutable auth status
if ($LASTEXITCODE -ne 0) {
    throw 'GitHub CLI authentication is unavailable.'
}

$dispatchStarted = [DateTimeOffset]::UtcNow.AddSeconds(-5)
& $ghExecutable workflow run $workflow --repo $Repository --ref $Ref
if ($LASTEXITCODE -ne 0) {
    throw 'Protected fixture-discovery workflow dispatch failed. Confirm the workflow is merged on the selected ref.'
}

$runId = $null
for ($attempt = 0; $attempt -lt 20 -and $null -eq $runId; $attempt++) {
    Start-Sleep -Seconds 2
    $runsJson = & $ghExecutable run list `
        --repo $Repository `
        --workflow $workflow `
        --branch $Ref `
        --event workflow_dispatch `
        --limit 5 `
        --json databaseId,createdAt,status
    if ($LASTEXITCODE -ne 0) {
        continue
    }
    $runs = $runsJson | ConvertFrom-Json
    $candidate = $runs | Where-Object {
        [DateTimeOffset]::Parse($_.createdAt) -ge $dispatchStarted
    } | Sort-Object { [DateTimeOffset]::Parse($_.createdAt) } -Descending | Select-Object -First 1
    if ($null -ne $candidate) {
        $runId = [string]$candidate.databaseId
    }
}
if ($null -eq $runId) {
    throw 'The dispatched workflow run could not be identified.'
}

Write-Host "Protected discovery run: $runId"
& $ghExecutable run watch $runId --repo $Repository --exit-status
if ($LASTEXITCODE -ne 0) {
    throw "Protected discovery run $runId did not pass. Review sanitized Actions logs."
}

New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
& $ghExecutable run download $runId `
    --repo $Repository `
    --name $artifactName `
    --dir $OutputDirectory
if ($LASTEXITCODE -ne 0) {
    throw 'Protected SQL artifact download failed.'
}

$sqlPath = Join-Path $OutputDirectory 'pip-fixture-registration.sql'
if (-not (Test-Path -LiteralPath $sqlPath)) {
    throw 'Downloaded artifact did not contain pip-fixture-registration.sql.'
}

Write-Host 'Automatic provider discovery completed without exposing credentials.'
Write-Host "Review and import: $sqlPath"
