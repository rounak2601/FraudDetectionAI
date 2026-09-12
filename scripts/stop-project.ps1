$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
$Runtime = Join-Path $Root ".runtime"
Set-Location $Root

foreach ($name in @("frontend", "backend", "ollama")) {
    $pidFile = Join-Path $Runtime "$name.pid"
    if (Test-Path $pidFile) {
        $processId = Get-Content $pidFile -ErrorAction SilentlyContinue
        if ($processId) { Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue }
        Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
    }
}

docker compose stop
Write-Host "Project stopped. Database volumes were preserved." -ForegroundColor Green
