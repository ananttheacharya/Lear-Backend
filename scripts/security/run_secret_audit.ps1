<#
Run Lear's complete local secret audit on Windows/PowerShell.

Prefers the upstream gitleaks binary when installed, then always runs Lear's
bundled redacted fallback scanner so a fresh contributor machine still has a
working guardrail.
#>

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

$Gitleaks = Get-Command gitleaks -ErrorAction SilentlyContinue
if ($Gitleaks) {
    Write-Host "[security] running gitleaks full-history scan"
    & gitleaks detect --source . --config .gitleaks.toml --redact --verbose
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
    Write-Host "[security] gitleaks not found; skipping upstream gitleaks scan"
    Write-Host "[security] install from https://github.com/gitleaks/gitleaks for the full rule set"
}

Write-Host "[security] running Lear fallback working-tree scan"
python scripts/security/secrets_audit.py --working-tree
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "[security] running Lear fallback full-history scan"
python scripts/security/secrets_audit.py --history
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "[security] secret audit completed cleanly"
