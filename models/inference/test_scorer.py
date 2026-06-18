import sys
import time
sys.path.insert(0, ".")

from models.inference.scorer import FraudScorer

print("="*50)
print("  FraudScorer — End-to-End Test")
print("="*50)

scorer = FraudScorer()

# --- Test 1: Normal transaction ---
normal_tx = {
    "TransactionAmt": 49.99,
    "ProductCD": "W",
    "card4": "visa",
    "card6": "debit",
    "P_emaildomain": "gmail.com",
    "R_emaildomain": "gmail.com",
    "addr1": 299,
    "addr2": 87,
    "dist1": 0,
    "C1": 1, "C2": 1, "C3": 0, "C4": 0,
    "C5": 0, "C6": 1, "C7": 0, "C8": 0,
    "C9": 1, "C10": 0,
    "V1": 1, "V2": 1, "V3": 1, "V4": 1, "V5": 1,
    "V6": 1, "V7": 1, "V8": 1, "V9": 1, "V10": 1,
}

# --- Test 2: Suspicious transaction ---
suspicious_tx = {
    "TransactionAmt": 12500.00,   # Very high amount
    "ProductCD": "C",
    "card4": "mastercard",
    "card6": "credit",
    "P_emaildomain": "mailinator.com",   # Burner email
    "R_emaildomain": "guerrillamail.com", # Burner email
    "addr1": -999,   # Missing address
    "addr2": -999,
    "dist1": 9999,
    "C1": 15, "C2": 15, "C3": 5, "C4": 5,
    "C5": 5,  "C6": 0,  "C7": 5, "C8": 5,
    "C9": 0,  "C10": 5,
    "V1": 0, "V2": 0, "V3": 0, "V4": 0, "V5": 0,
    "V6": 0, "V7": 0, "V8": 0, "V9": 0, "V10": 0,
}

# --- Test 3: Latency benchmark ---
print("\n--- Test 1: Normal Transaction ---")
result = scorer.score(normal_tx, "TX_NORMAL_001")
print(f"  Fraud probability: {result.fraud_probability}")
print(f"  Risk level:        {result.risk_level}")
print(f"  XGBoost score:     {result.xgb_score}")
print(f"  IF score:          {result.isolation_score}")
print(f"  Triggered rules:   {result.triggered_rules or 'None'}")

print("\n--- Test 2: Suspicious Transaction ---")
result = scorer.score(suspicious_tx, "TX_SUSP_001")
print(f"  Fraud probability: {result.fraud_probability}")
print(f"  Risk level:        {result.risk_level}")
print(f"  XGBoost score:     {result.xgb_score}")
print(f"  IF score:          {result.isolation_score}")
print(f"  Triggered rules:")
for rule in result.triggered_rules:
    print(f"    → {rule}")

print("\n--- Test 3: Latency Benchmark (1000 transactions) ---")
import copy
txs = [copy.copy(normal_tx) for _ in range(1000)]

start = time.perf_counter()
results = scorer.score_batch(txs)
elapsed_ms = (time.perf_counter() - start) * 1000

print(f"  1000 transactions scored in {elapsed_ms:.1f} ms")
print(f"  Average per transaction:    {elapsed_ms/1000:.3f} ms")
print(f"  Projected throughput:       {1000/elapsed_ms*1000:.0f} tx/sec")

print("\n" + "="*50)
print("  Day 4 COMPLETE")
print("="*50)
print("\nArtifacts saved:")
import os
for f in sorted(os.listdir("models/artifacts")):
    size = os.path.getsize(f"models/artifacts/{f}")
    print(f"  {f:<35} {size/1024:.1f} KB")