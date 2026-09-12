import os

from backend.services.compliance import evaluate_rules, sanctions_check
from backend.services.drift import drift_status, population_stability_index


def test_compliance_rules_and_sanctions(monkeypatch):
    monkeypatch.setenv("SANCTIONS_ENTITIES", "blocked-merchant")
    payload = {"merchant_name": "blocked-merchant", "amount": 60000, "fraud_score": 0.9}
    assert sanctions_check(payload)["matched"] is True
    rules = evaluate_rules(payload)
    assert {rule["rule"] for rule in rules} == {"HIGH_AMOUNT", "MODEL_THRESHOLD"}


def test_drift_status_bands():
    assert drift_status(0.01) == "stable"
    assert drift_status(0.12) == "watch"
    assert drift_status(0.30) == "significant_drift"
    psi = population_stability_index([0.1, 0.2, 0.3], [0.8, 0.9, 0.95])
    assert psi > 0
