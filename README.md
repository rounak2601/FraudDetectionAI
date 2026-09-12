# FraudVision AI

### Real-Time Financial Fraud Detection with Explainable ML

> **AI that sees fraud patterns before they become losses.**

FraudVision AI is a full-stack fraud detection platform that combines ensemble machine learning, graph-based fraud-ring analysis, real-time feature engineering, SHAP explainability, and an analyst investigation dashboard.

The system is designed as a practical end-to-end engineering project: transactions are scored in real time, risk is made explainable, and analysts can investigate, approve, or block suspicious activity from one interface.

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-TypeScript-61DAFB?logo=react&logoColor=111827)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7.2-DC382D?logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

## Product Overview

FraudVision AI turns a raw financial transaction into an explainable decision:

```text
Transaction
    ↓
Kafka ingestion and event flow
    ↓
Redis velocity and behavioral features
    ↓
Graph-based relationship analysis
    ↓
XGBoost + Isolation Forest + Meta-Learner ensemble
    ↓
SHAP feature attribution and analyst narrative
    ↓
React investigation queue
    ↓
Approve, block, investigate, or audit
```

### What the analyst sees

- Fraud probability and risk band: `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`
- Per-feature SHAP contributions
- Triggered deterministic fraud rules
- AI-generated or fallback explanation narrative
- Account, device, IP, email, address, amount, and behavioral context
- Investigation, approval, blocking, and audit actions
- Live model and transaction monitoring

---

## Application Pages

| Page | Route | Purpose |
|---|---|---|
| Landing page | `/` | Product overview and architecture walkthrough |
| Investigation queue | `/dashboard` | Live transaction queue and fraud alerts |
| Investigation view | `/investigation/:id` | Detailed transaction evidence and explanation |
| Live monitoring | `/monitoring` | Volume, risk, model, and score trends |

> Local development URLs use `http://localhost:3000`. If port 3000 is already busy, Create React App may use port 3001.

---

## Core Capabilities

| Capability | Implementation |
|---|---|
| Ensemble fraud scoring | XGBoost ONNX + Isolation Forest + calibrated Meta-Learner |
| Fraud-ring analysis | Neo4j relationship graph and GraphSAGE-oriented graph service |
| Real-time feature engineering | Redis sorted sets for velocity and behavioral signals |
| Explainability | SHAP feature attribution for each scored transaction |
| Analyst narratives | Optional Ollama LLM with a deterministic fallback mode |
| Case management | Investigate, approve, block, and persist decisions |
| Auditability | Hash-chained audit trail for investigation actions |
| Live demo feed | Automatically sends a scored transaction every five seconds |
| Monitoring | Live counters, transaction volume, average-score trends, and model health |
| Persistence | PostgreSQL transaction and case storage |

---

## System Architecture

```mermaid
flowchart TD
    A[React Analyst Dashboard] -->|REST / JSON| B[FastAPI Backend]
    B --> C[Transaction Scoring API]
    C --> D[XGBoost ONNX]
    C --> E[Isolation Forest]
    C --> F[Meta-Learner]
    B --> G[Redis Feature Store]
    B --> H[PostgreSQL]
    B --> I[Neo4j Graph Service]
    B --> J[SHAP Explainer]
    J --> K[Optional Ollama Narrative]
    B --> L[Kafka Event Pipeline]
    L --> G
    L --> I
```

### Transaction decision flow

1. A transaction enters through the scoring API or Kafka pipeline.
2. Redis supplies velocity and behavioral context.
3. Graph services enrich the transaction with relationship signals.
4. XGBoost and Isolation Forest produce complementary scores.
5. The Meta-Learner combines the model outputs into a calibrated fraud probability.
6. Rules add deterministic signals such as unusual amounts, burner emails, and velocity spikes.
7. SHAP identifies the features that influenced the decision.
8. The result is stored and displayed in the analyst dashboard.

---

## Machine Learning Pipeline

### XGBoost primary scorer

- Trained on the IEEE-CIS fraud detection dataset.
- Exported to ONNX for lightweight CPU inference.
- Uses engineered card, address, email, device, amount, and behavioral features.

### Isolation Forest anomaly detector

- Learns normal transaction behavior without requiring fraud labels.
- Detects unusual transactions that may not resemble known fraud examples.

### Meta-Learner ensemble

- Combines the primary model and anomaly score.
- Produces the final fraud probability used for risk classification.
- Supports a configurable fraud threshold through environment settings.

### Graph service

- Maintains relationships between accounts, devices, addresses, IPs, cards, and email domains.
- Supports neighborhood and fraud-ring investigation workflows.

---

## Explainability

For a suspicious transaction, FraudVision AI provides:

1. **Fraud probability** — calibrated score between 0 and 1.
2. **Risk level** — human-readable severity classification.
3. **SHAP values** — features that pushed the prediction higher or lower.
4. **Triggered rules** — transparent deterministic indicators.
5. **Analyst narrative** — generated by Ollama when enabled, otherwise a fallback explanation is returned.

Ollama is optional. Core scoring, dashboards, SHAP output, and case management continue to work with:

```env
OLLAMA_REQUIRED=false
INLINE_EXPLANATIONS=false
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Ant Design, Recharts |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| ML inference | XGBoost ONNX Runtime, Isolation Forest, Meta-Learner |
| Explainability | SHAP, optional Ollama |
| Graph analysis | Neo4j and graph-service modules |
| Feature store | Redis |
| Database | PostgreSQL 16 |
| Event streaming | Apache Kafka and Zookeeper |
| Monitoring | Prometheus and Grafana configuration |
| Experiment tracking | MLflow |
| Infrastructure | Docker Compose |

---

## Quick Start — Windows PowerShell

### Prerequisites

- Docker Desktop with Docker Compose
- Python 3.11+
- Node.js 20+
- Git
- Ollama is optional

### 1. Clone the repository

```powershell
git clone https://github.com/rounak2601/FraudDetectionAI.git
cd FraudDetectionAI
```

### 2. Configure environment variables

Create or update `.env` with values appropriate for your machine. A local setup commonly uses:

```env
POSTGRES_URL=postgresql://fraud_user:fraud_pass@127.0.0.1:5433/fraud_db
POSTGRES_HOST_PORT=5433
REDIS_URL=redis://127.0.0.1:6379
REACT_APP_API_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001
OLLAMA_REQUIRED=false
INLINE_EXPLANATIONS=false
```

Never commit real passwords, tokens, or private deployment credentials.

### 3. Start the backend and infrastructure

```powershell
.\scripts\start-project.ps1 -SkipFrontend -SkipOllama
```

Verify the backend:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

### 4. Start the frontend in a second terminal

```powershell
cd frontend
npm install
npm start
```

Open:

```text
http://localhost:3000/dashboard
```

The Auto Feed starts automatically and sends a demo transaction every five seconds.

### 5. Stop the project

```powershell
.\scripts\stop-project.ps1
```

The PostgreSQL volume is preserved by the project stop script.

---

## Production Build

```powershell
cd frontend
npm run build
```

The production frontend is generated in:

```text
frontend/build
```

The backend health endpoint is:

```text
GET /health
```

The main API routes include:

```text
GET  /api/transactions/recent
POST /api/transactions/score
GET  /api/transactions/{transaction_id}
POST /api/transactions/{transaction_id}/explain
GET  /api/models/stats
GET  /api/models/health
GET  /api/monitoring
POST /api/cases/create/{transaction_id}
POST /api/cases/{case_id}/approve
POST /api/cases/{case_id}/block
```

---

## Project Structure

```text
FraudDetectionAI/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models/
│   └── routers/
├── explainability/
│   ├── shap_explainer.py
│   └── llm_explainer.py
├── feature_engineering/
├── graph_service/
├── kafka/
├── models/
│   ├── artifacts/
│   ├── inference/
│   └── training/
├── monitoring/
├── scripts/
│   ├── start-project.ps1
│   ├── stop-project.ps1
│   └── doctor.ps1
├── tests/
├── frontend/
│   └── src/
│       ├── api/
│       ├── components/
│       └── pages/
├── docker-compose.yml
└── README.md
```

---

## Improvements Added in the Current Release

### Reliability and startup

- Added repeatable PowerShell startup and stop workflows.
- Added health checks for Docker, Python, models, ports, backend, and frontend.
- Added PostgreSQL connection verification before backend startup.
- Added fallback operation when Ollama is not running.

### Dashboard and monitoring

- Fixed frontend-to-backend CORS support for both ports `3000` and `3001`.
- Fixed monitoring chart aggregation so data is grouped into five-second buckets instead of one point per minute.
- Changed monitoring refresh interval to five seconds.
- Added live transaction counters, risk bands, average scores, and model status.

### Demo experience

- Auto Feed now starts automatically when the dashboard loads.
- The demo feed sends a transaction every five seconds.
- The manual Stop Feed / Start Demo Feed control remains available.
- Transaction amounts and account identifiers vary between generated events.

### Production readiness

- Confirmed the React production build completes successfully.
- Added local production-build instructions.
- Added API health and smoke-test guidance.
- Documented optional versus required services.

---

## Validation Checklist

Before publishing a release, confirm:

- [ ] `docker compose config` passes.
- [ ] PostgreSQL and Redis are healthy.
- [ ] `GET /health` returns `healthy`.
- [ ] A transaction can be scored through `/api/transactions/score`.
- [ ] The scored transaction appears in `/api/transactions/recent`.
- [ ] The dashboard loads without CORS errors.
- [ ] Monitoring charts show multiple time buckets.
- [ ] Auto Feed sends transactions without manual activation.
- [ ] `npm run build` completes successfully.
- [ ] Secrets are excluded from Git.

---

## Deployment Notes

The repository is container-oriented and can be deployed on a Docker-capable host. For a multi-service deployment, the host must provide enough memory for the selected services, especially PostgreSQL, Redis, Kafka, Neo4j, and the backend.

For a portfolio demo, deploy the frontend and backend with Ollama disabled unless LLM-generated narratives are specifically required. Keep secrets in the host's environment-variable manager and do not commit `.env` files.

A production deployment should also add:

- HTTPS and a reverse proxy
- Managed PostgreSQL and Redis or persistent volumes
- Secret rotation
- Authentication hardening
- Database backups
- Centralized logs and alerts
- Separate demo-feed controls for non-production environments

---

## Limitations and Responsible Use

FraudVision AI is an engineering and portfolio project, not a standalone financial compliance system. Model scores should support human investigation rather than automatically deny legitimate customers. Production use requires calibration, monitoring for drift, fairness testing, privacy controls, regulatory review, and a documented incident-response process.

---

## Author

Built by **Rounak Tilante** as an end-to-end portfolio project demonstrating:

- Real-time ML inference
- Explainable AI
- Graph-based fraud analysis
- Event-driven architecture
- Full-stack product engineering
- Analyst-focused case management

GitHub: [rounak2601/FraudDetectionAI](https://github.com/rounak2601/FraudDetectionAI)

---

## License

MIT License. See [LICENSE](LICENSE) for details.
