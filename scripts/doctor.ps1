$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "FraudDetectionAI preflight" -ForegroundColor Cyan
$failed = $false

function Check-Command($Name) {
    if (Get-Command $Name -ErrorAction SilentlyContinue) {
        Write-Host "[OK] $Name" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] $Name not found" -ForegroundColor Red
        $script:failed = $true
    }
}

Check-Command docker
Check-Command node
Check-Command npm

if (-not (Test-Path ".\venv\Scripts\python.exe")) {
    Write-Host "[FAIL] venv Python not found" -ForegroundColor Red
    $failed = $true
} else {
    Write-Host "[OK] venv Python: $(& .\venv\Scripts\python.exe --version)" -ForegroundColor Green
}

if (-not (Test-Path ".\.env")) {
    Write-Host "[WARN] .env missing. Run: Copy-Item .env.example .env" -ForegroundColor Yellow
}

@(
    "models\artifacts\xgboost_model.onnx",
    "models\artifacts\xgboost_model.pkl",
    "models\artifacts\isolation_forest_model.pkl",
    "models\artifacts\meta_learner.pkl",
    "models\artifacts\feature_names.pkl"
) | ForEach-Object {
    if (Test-Path $_) { Write-Host "[OK] $_" -ForegroundColor Green }
    else { Write-Host "[FAIL] Missing $_" -ForegroundColor Red; $failed = $true }
}

$port = if ($env:POSTGRES_HOST_PORT) { $env:POSTGRES_HOST_PORT } else { 5433 }
$listeners = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
if ($listeners) { Write-Host "[INFO] Port $port is currently in use" -ForegroundColor Yellow }
else { Write-Host "[OK] Port $port is available" -ForegroundColor Green }

if ($failed) { exit 1 }
Write-Host "Preflight passed." -ForegroundColor Green
