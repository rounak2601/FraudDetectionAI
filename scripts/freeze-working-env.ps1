$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
if (-not (Test-Path ".\venv\Scripts\python.exe")) { throw "venv not found" }
& .\venv\Scripts\python.exe -m pip freeze | Set-Content requirements.lock.txt
Write-Host "Created requirements.lock.txt from the working environment." -ForegroundColor Green
