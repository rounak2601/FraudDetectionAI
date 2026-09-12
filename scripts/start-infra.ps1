param([switch]$Full)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

docker info *> $null
if ($LASTEXITCODE -ne 0) { throw "Docker Desktop is not ready." }

docker compose config --quiet
if ($LASTEXITCODE -ne 0) { throw "docker-compose.yml is invalid." }

if ($Full) {
    docker compose --profile streaming --profile graph --profile monitoring up -d
} else {
    # The API currently requires PostgreSQL. Redis is kept ready for feature services.
    # Kafka, Neo4j, Zookeeper and Grafana remain off to reduce local startup time/RAM.
    docker compose up -d postgres redis
}
if ($LASTEXITCODE -ne 0) { throw "Infrastructure startup failed." }

docker compose ps
Write-Host "Infrastructure started. Use -Full only for end-to-end integration tests." -ForegroundColor Green
