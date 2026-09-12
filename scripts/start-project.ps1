param(
    [switch]$SkipFrontend,
    [switch]$SkipOllama,
    [switch]$FullInfrastructure
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Runtime = Join-Path $Root ".runtime"
$Logs = Join-Path $Runtime "logs"
Set-Location $Root
New-Item -ItemType Directory -Force $Logs | Out-Null

& "$PSScriptRoot\doctor.ps1"
if ($LASTEXITCODE -ne 0) { throw "Preflight failed." }

if ($FullInfrastructure) {
    & "$PSScriptRoot\start-infra.ps1" -Full
} else {
    & "$PSScriptRoot\start-infra.ps1"
}
if ($LASTEXITCODE -ne 0) { throw "Infrastructure failed." }

Write-Host "Waiting for PostgreSQL health..." -ForegroundColor Cyan
$ready = $false
for ($i = 1; $i -le 30; $i++) {
    docker compose exec -T postgres sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"' *> $null
    if ($LASTEXITCODE -eq 0) { $ready = $true; break }
    Start-Sleep -Seconds 2
}
if (-not $ready) { throw "PostgreSQL did not become ready. Run: docker compose logs postgres" }

if (-not $SkipOllama) {
    try {
        Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 2 | Out-Null
        Write-Host "[OK] Ollama already running" -ForegroundColor Green
    } catch {
        if (Get-Command ollama -ErrorAction SilentlyContinue) {
            $ollama = Start-Process ollama -ArgumentList "serve" -PassThru -WindowStyle Hidden -RedirectStandardOutput "$Logs\ollama.out.log" -RedirectStandardError "$Logs\ollama.err.log"
            $ollama.Id | Set-Content "$Runtime\ollama.pid"
            Write-Host "[OK] Ollama started (optional)" -ForegroundColor Green
        } else {
            Write-Host "[WARN] Ollama not installed; fallback explanations will be used" -ForegroundColor Yellow
        }
    }
}

$backend = Start-Process ".\venv\Scripts\python.exe" -ArgumentList @("-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000") -WorkingDirectory $Root -PassThru -RedirectStandardOutput "$Logs\backend.out.log" -RedirectStandardError "$Logs\backend.err.log"
$backend.Id | Set-Content "$Runtime\backend.pid"

Write-Host "Waiting for backend..." -ForegroundColor Cyan
$apiReady = $false
for ($i = 1; $i -le 60; $i++) {
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 2
        $apiReady = $true
        break
    } catch { Start-Sleep -Seconds 2 }
}
if (-not $apiReady) {
    Get-Content "$Logs\backend.err.log" -Tail 80 -ErrorAction SilentlyContinue
    throw "Backend did not become ready."
}
Write-Host "[OK] Backend: http://localhost:8000/docs" -ForegroundColor Green

if (-not $SkipFrontend) {
    $frontendDir = Join-Path $Root "frontend"
    if (-not (Test-Path "$frontendDir\node_modules")) {
        Push-Location $frontendDir
        npm ci
        Pop-Location
    }
    $env:BROWSER = "none"
    if (-not $env:REACT_APP_API_URL) { $env:REACT_APP_API_URL = "http://localhost:8000" }
    $frontend = Start-Process "npm.cmd" -ArgumentList "start" -WorkingDirectory $frontendDir -PassThru -RedirectStandardOutput "$Logs\frontend.out.log" -RedirectStandardError "$Logs\frontend.err.log"
    $frontend.Id | Set-Content "$Runtime\frontend.pid"

    Write-Host "Waiting for frontend compilation..." -ForegroundColor Cyan
    $frontendReady = $false
    for ($i = 1; $i -le 150; $i++) {
        try {
            $response = Invoke-WebRequest "http://127.0.0.1:3000" -UseBasicParsing -TimeoutSec 2
            if ($response.StatusCode -eq 200) { $frontendReady = $true; break }
        } catch { Start-Sleep -Seconds 2 }
    }
    if (-not $frontendReady) {
        Get-Content "$Logs\frontend.out.log" -Tail 120 -ErrorAction SilentlyContinue
        Get-Content "$Logs\frontend.err.log" -Tail 80 -ErrorAction SilentlyContinue
        throw "Frontend did not become ready within 5 minutes."
    }
    Write-Host "[OK] Frontend: http://localhost:3000" -ForegroundColor Green
}

Write-Host "Project startup complete. Logs: $Logs" -ForegroundColor Green
