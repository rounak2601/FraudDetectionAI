# Technical audit summary

## Startup blockers fixed

- Docker PostgreSQL now defaults to host port `5433`, avoiding the Windows PostgreSQL listener on `5432`.
- Backend database default matches port `5433` and retries readiness instead of failing during a startup race.
- Ollama is optional: when unavailable, scoring starts normally and rule-based narratives are used.
- Model paths are resolved from the project directory, not the terminal's current directory.
- SHAP/XGBoost explanation resources are loaded once rather than twice.
- Normal startup excludes Kafka, Zookeeper, Neo4j and Grafana; use `-FullInfrastructure` only for integration testing.

## Application defects fixed

- Removed synchronous high-risk LLM work from the scoring request by default.
- Prevented background explanation work when the explainer failed to initialize.
- Reused the application explainer for on-demand requests instead of reloading models per request.
- Corrected explanation error handling that could reference an undefined transaction.
- Made frontend API origin configurable and URL-encoded route identifiers.
- Made Kafka, Redis and graph worker endpoints environment-driven.

## Deployment preparation added

- Persistent service volumes and health checks.
- Dual Kafka internal/external listeners.
- Backend and frontend Dockerfiles.
- Nginx SPA routing and `/api` reverse proxy.
- Production Compose overlay.
- Python dependency manifest, `.dockerignore`, `.env.example`, operational scripts and runbook.

## Validation completed

- All Python files parse and compile successfully.
- Compose YAML and required service/profile structure validated.
- Frontend package and lock files parse successfully.
- Hardcoded PostgreSQL `localhost:5432`, Redis, Kafka and frontend API definitions removed from runtime source.

## Environment-dependent validation still required on the Windows workstation

- Deserialize and score with the existing working Python environment.
- Run `npm run build` using the workstation's installed dependencies.
- Start Docker and verify real service health.
- Execute one API transaction and frontend workflow.

These runtime checks could not be performed in the isolated packaging environment because it does not have the project's ML packages or public package-registry access.
