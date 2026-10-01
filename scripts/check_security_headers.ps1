<#
Validate S-06 secure headers against a running Lear/FastAPI server.
Usage: ./scripts/check_security_headers.ps1 http://localhost:8000
#>

param(
    [string]$BaseUrl = "http://localhost:8000"
)

$ErrorActionPreference = "Stop"
$Target = ($BaseUrl.TrimEnd('/')) + "/api/system/version"
$RequiredHeaders = @(
    "X-Content-Type-Options",
    "X-Frame-Options",
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "Referrer-Policy",
    "Permissions-Policy"
)

Write-Host "Checking security headers on $Target"

try {
    $Response = Invoke-WebRequest -Uri $Target -Method Head -SkipHttpErrorCheck
    if ($Response.StatusCode -eq 405) {
        $Response = Invoke-WebRequest -Uri $Target -Method Get -SkipHttpErrorCheck
    }
} catch {
    # Older PowerShell versions do not support -SkipHttpErrorCheck.
    $Response = Invoke-WebRequest -Uri $Target -Method Get
}

$Failed = $false
foreach ($Header in $RequiredHeaders) {
    if ($Response.Headers.ContainsKey($Header)) {
        Write-Host "  OK $Header"
    } else {
        Write-Error "  MISSING $Header"
        $Failed = $true
    }
}

if ($Failed) {
    Write-Error "FAILED: one or more security headers are missing."
    exit 1
}

Write-Host "All required security headers are present."
