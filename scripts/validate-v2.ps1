$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$python = Join-Path $Root "venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw "Virtual environment not found: $python" }
if (-not (Test-Path "models\artifacts\categorical_encoders.json")) {
    throw "categorical_encoders.json is missing. Build it before validation."
}

& $python -c "from models.inference.scorer import FraudScorer; s=FraudScorer(); x=s._preprocess({'amount':12345}); assert float(x[0,0])==12345.0, x[0,0]; assert s.encoding_mode=='training_compatible', s.encoding_mode; print('MODEL_PREPROCESSING_OK amount=',x[0,0],'encoding=',s.encoding_mode)"
if ($LASTEXITCODE -ne 0) { throw "Model preprocessing validation failed." }

$health = Invoke-RestMethod "http://127.0.0.1:8000/api/models/health"
$monitoring = Invoke-RestMethod "http://127.0.0.1:8000/api/monitoring"

if ($health.models_active -ne 3) { throw "Expected 3 active runtime models." }
if ($health.encoding_mode -ne "training_compatible") { throw "Backend is not using training-compatible encoders." }
if ($monitoring.avg_score -lt 0 -or $monitoring.avg_score -gt 100) { throw "Average score is invalid." }

Write-Host "V2 validation passed." -ForegroundColor Green
$health | Format-List
$monitoring | Format-List
