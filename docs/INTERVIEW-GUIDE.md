# FraudVision AI — Interview Guide

## 30-second explanation

FraudVision AI is an explainable, real-time fraud decisioning platform. A transaction is enriched with velocity and graph context, scored by complementary ML models, calibrated by a meta-learner, and returned with SHAP evidence, deterministic rules, and an analyst-friendly narrative.

## Why multiple models?

- XGBoost captures supervised tabular fraud patterns.
- Isolation Forest detects unusual behavior without requiring fraud labels.
- Graph features expose coordinated activity between accounts, devices, IPs, and merchants.
- The meta-learner calibrates the combined score into a decision probability.

## How is the result explained?

SHAP attributes the tabular score to individual features. Rules provide transparent hard signals. The optional local LLM turns the evidence into natural language; it is never the source of the numeric decision.

## What happens when Ollama is unavailable?

The scoring and SHAP pipeline still works. The backend returns a deterministic fallback narrative, which keeps the decision service available.

## What is the latency strategy?

Keep hot-path work bounded: ONNX inference for tabular scoring, Redis for sliding-window features, cached graph neighborhoods, and asynchronous narrative generation. The 10K TPS / 50ms claim must be validated with a repeatable load test rather than assumed.

## Compliance features

The upgrade pack adds a compliance boundary: configurable sanctions matching, deterministic rules, and a draft SAR endpoint. In a regulated deployment, an authoritative refreshed sanctions dataset, schema validation, RBAC, human review, retention policy, and legal/compliance approval are mandatory.

## Strong answer about limitations

"The repository contains the core scoring, explainability, case-management, and streaming foundations. The remaining production work is measurable hardening: authoritative sanctions data, SAR schema validation, online learning approval gates, distributed tracing, integration tests, and a verified load-test report. I would not claim a 10K TPS SLA until those tests pass in a production-like environment."
