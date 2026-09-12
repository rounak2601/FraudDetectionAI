$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$BackupDir = Join-Path $Root "backups"
Set-Location $Root
New-Item -ItemType Directory -Force $BackupDir | Out-Null

$container = docker ps -a --filter "name=^/postgres$" --format "{{.Names}}"
if ($container -ne "postgres") {
    Write-Host "No existing postgres container found; no database backup was required." -ForegroundColor Yellow
    exit 0
}

docker start postgres | Out-Null
for ($i = 1; $i -le 30; $i++) {
    docker exec postgres sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"' *> $null
    if ($LASTEXITCODE -eq 0) { break }
    Start-Sleep -Seconds 2
}
if ($LASTEXITCODE -ne 0) { throw "Existing PostgreSQL container did not become ready." }

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$file = Join-Path $BackupDir "fraud-db-$stamp.dump"
docker exec postgres sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc -f /tmp/fraud-db.dump'
if ($LASTEXITCODE -ne 0) { throw "pg_dump failed." }
docker cp "postgres:/tmp/fraud-db.dump" $file
if ($LASTEXITCODE -ne 0) { throw "Could not copy database backup." }
Write-Host "Database backup created: $file" -ForegroundColor Green
