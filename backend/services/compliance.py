"""Lightweight compliance services used by the analyst API.

This module intentionally keeps external sanctions data out of source control.
Provide a comma-separated SANCTIONS_ENTITIES environment variable or replace
this matcher with a managed, refreshed OFAC SDN index in production.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from html import escape
from typing import Any


def _sanctions_entities() -> set[str]:
    raw = os.getenv("SANCTIONS_ENTITIES", "")
    return {item.strip().casefold() for item in raw.split(",") if item.strip()}


def sanctions_check(values: dict[str, Any]) -> dict[str, Any]:
    entities = _sanctions_entities()
    searchable = {
        str(values.get(key, "")).strip().casefold()
        for key in ("account_id", "merchant", "merchant_name", "beneficiary", "country", "ip_address")
        if values.get(key) is not None
    }
    matches = sorted(value for value in searchable if value and value in entities)
    return {
        "matched": bool(matches),
        "matches": matches,
        "source": "configured_sanctions_entities",
        "review_required": bool(matches),
        "message": "Potential sanctions match requires analyst review." if matches else "No configured sanctions match.",
    }


def evaluate_rules(values: dict[str, Any]) -> list[dict[str, Any]]:
    rules: list[dict[str, Any]] = []
    amount = float(values.get("amount") or 0)
    score = float(values.get("fraud_score") or 0)
    country = str(values.get("country") or "").upper()
    if amount >= float(os.getenv("RULE_HIGH_AMOUNT", "50000")):
        rules.append({"rule": "HIGH_AMOUNT", "severity": "high", "reason": "Transaction exceeds the configured amount limit."})
    if score >= float(os.getenv("MODEL_FRAUD_THRESHOLD", "0.5")):
        rules.append({"rule": "MODEL_THRESHOLD", "severity": "high", "reason": "Model score exceeds the configured fraud threshold."})
    blocked_countries = {x.strip().upper() for x in os.getenv("BLOCKED_COUNTRIES", "").split(",") if x.strip()}
    if country and country in blocked_countries:
        rules.append({"rule": "BLOCKED_COUNTRY", "severity": "critical", "reason": "Country is configured for enhanced review."})
    return rules


def build_draft_sar(transaction: dict[str, Any], rules: list[dict[str, Any]], sanctions: dict[str, Any]) -> str:
    """Return a reviewable SAR-style XML draft, not an automatic filing."""
    now = datetime.now(timezone.utc).isoformat()
    tx_id = escape(str(transaction.get("transaction_id", "unknown")))
    reason = escape("; ".join(rule["reason"] for rule in rules) or sanctions["message"])
    account = escape(str(transaction.get("account_id", "unknown")))
    amount = escape(str(transaction.get("amount", "0")))
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<SARDraft generatedAt="{escape(now)}" status="analyst-review-required">
  <TransactionId>{tx_id}</TransactionId>
  <AccountId>{account}</AccountId>
  <Amount>{amount}</Amount>
  <Narrative>{reason}</Narrative>
  <Disclaimer>This is a draft for human review and is not an electronic filing.</Disclaimer>
</SARDraft>'''


def hash_evidence(payload: dict[str, Any], previous_hash: str = "") -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(f"{previous_hash}|{canonical}".encode("utf-8")).hexdigest()
