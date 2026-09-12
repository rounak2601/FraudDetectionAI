param([Parameter(Mandatory=$true)][string]$BackupFile)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
if (-not (Test-Path $BackupFile)) { throw "Backup not found: $BackupFile" }

docker compose up -d postgres
for ($i = 1; $i -le 30; $i++) {
    docker compose exec -T postgres sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"' *> $null
    if ($LASTEXITCODE -eq 0) { break }
    Start-Sleep -Seconds 2
}
if ($LASTEXITCODE -ne 0) { throw "PostgreSQL did not become ready." }

docker cp $BackupFile "postgres:/tmp/fraud-db.dump"
docker exec postgres sh -c 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists /tmp/fraud-db.dump'
if ($LASTEXITCODE -ne 0) { throw "Database restore failed." }
Write-Host "Database restored from: $BackupFile" -ForegroundColor Green
