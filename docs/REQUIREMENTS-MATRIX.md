# Official Requirements Matrix

This matrix is intentionally honest: **Implemented** means demonstrated in the current repository; **Partial** means a working foundation exists but production hardening or UI work remains; **Planned** means it is not yet complete.

| Requirement | Status | Evidence / next step |
|---|---|---|
| XGBoost + Isolation Forest + Meta-Learner | Implemented | `models/inference/scorer.py` |
| SHAP tabular explanation | Implemented | `explainability/shap_explainer.py` |
| Kafka, Redis, Neo4j integration | Partial | Modules and Docker services exist; run integration tests and measure latency |
| GraphSAGE/GNN scoring | Partial | Model artifacts and training scripts exist; add online graph inference and GNNExplainer |
| Case management | Implemented | `backend/routers/cases.py` and React investigation flow |
| Tamper-evident audit model | Implemented foundation | Add append-only storage and verification endpoint |
| Configurable rules | Partial | Compliance upgrade adds amount, score, country, and sanctions configuration |
| SAR generation | Partial | Draft SAR XML endpoint; validate against the official filing schema before real filing |
| Sanctions screening | Partial | Configurable matcher; production must refresh and index an authoritative OFAC dataset |
| Concept drift | Partial | PSI service added; connect it to scheduled monitoring and model refresh workflows |
| Online learning | Planned | Add label ingestion, champion/challenger evaluation, and approval gates |
| OpenTelemetry | Planned | Add spans around Kafka, Redis, graph, scoring, and database stages |
| 10K TPS / 50ms SLA | Unverified | Run Locust/k6 against a production-like environment; do not claim it without results |
| Kubernetes + Helm | Planned | Add manifests only after Docker Compose integration tests are green |
| CI/CD | Partial | Add GitHub Actions for lint, tests, security scan, build, and staged deployment |

## Interview-safe language

Say **"production-oriented foundation"** or **"production-ready architecture in progress"** unless the load, security, compliance, and disaster-recovery requirements have been measured and signed off.
