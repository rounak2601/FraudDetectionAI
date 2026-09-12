# FraudDetectionAI runbook

## One-time preparation

```powershell
cd C:\Projects\FraudDetectionAI
Copy-Item .env.example .env
.\scripts\freeze-working-env.ps1
```

Review `.env`; local Docker PostgreSQL intentionally uses host port `5433`, avoiding Windows PostgreSQL on `5432`.

## Normal local startup

```powershell
cd C:\Projects\FraudDetectionAI
.\scripts\start-project.ps1
```

The normal command starts only PostgreSQL, Redis, Ollama, the API and frontend. For the heavier Kafka, Zookeeper, Neo4j and Grafana integration test:

```powershell
.\scripts\start-project.ps1 -FullInfrastructure
```

Skip optional components when needed:

```powershell
.\scripts\start-project.ps1 -SkipFrontend -SkipOllama
```

## Status and logs

```powershell
.\scripts\status.ps1
Get-Content .\.runtime\logs\backend.err.log -Tail 100
Get-Content .\.runtime\logs\backend.out.log -Tail 100
```

## Safe shutdown

```powershell
.\scripts\stop-project.ps1
```

The shutdown script uses `docker compose stop`, not `down -v`, so data volumes remain intact.

## Production-style local build

Create strong secrets in `.env`, then:

```powershell
docker compose -f docker-compose.yml -f docker-compose.production.yml config
docker compose -f docker-compose.yml -f docker-compose.production.yml build
docker compose -f docker-compose.yml -f docker-compose.production.yml up -d
```

Do not expose the development credentials publicly. Use a managed secret store and managed PostgreSQL for a real public deployment.
