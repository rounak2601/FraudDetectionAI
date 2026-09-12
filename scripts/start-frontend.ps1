$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location "$Root\frontend"

if (-not (Test-Path ".\node_modules")) { npm ci }
npm start
