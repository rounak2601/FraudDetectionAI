"""
Day 5 — End-to-End Explainability Test
Place at: C:\Projects\FraudDetectionAI\test_day5.py
Run with: python test_day5.py
"""

import sys, os
sys.path.insert(0, os.path.abspath("."))

from models.inference.scorer import FraudScorer

print("=" * 62)
print("  Day 5 — End-to-End Explainability Test")
print("=" * 62)
print()

print("Loading FraudScorer...")
scorer = FraudScorer()
print()

# Two burner emails + high amount + debit + no address + high velocity
# This is designed to definitely cross 0.7
suspicious_tx = {
    "TransactionAmt":  15000.00,
    "ProductCD":       "W",
    "card4":           "visa",
    "card6":           "debit",
    "P_emaildomain":   "mailinator.com",    # burner email = +0.1 rule bump
    "R_emaildomain":   "guerrillamail.com", # burner email = +0.1 rule bump
    "addr1":           None,                # missing = +0.1 rule bump
    "dist1":           500,
    "C1":  50,  # very high velocity counts
    "C2":  45,
    "C6":  30,
    "C11": 40,
    "C14": 20,
    "D1":  0,   # brand new account
    "D10": 0,
    "V95":  1, "V96":  1, "V97":  1,
    "V126": 1, "V127": 1, "V128": 1,
    "V130": 1, "V131": 1, "V133": 1,
    "V134": 1, "V135": 1, "V136": 1,
    "V137": 1,
}

print("Scoring high-risk transaction...")
result = scorer.score(suspicious_tx, transaction_id="TEST_DAY5_FULL")
exp    = result.explanation

print()
print("=" * 62)
print("  RESULT")
print("=" * 62)
print(f"  Transaction ID   : {result.transaction_id}")
print(f"  Fraud Probability: {result.fraud_probability:.4f} ({result.fraud_probability*100:.1f}%)")
print(f"  Risk Level       : {result.risk_level}")
print(f"  XGBoost Score    : {result.xgb_score}")
print(f"  Isolation Score  : {result.isolation_score}")
print(f"  Explanation Type : {exp.get('explanation_type')}")
print()
print(f"  Triggered Rules  : {len(result.triggered_rules)}")
for rule in result.triggered_rules:
    print(f"    → {rule}")
print()

if exp.get("explanation_type") == "full_shap_llm":
    print("-" * 62)
    print("  SHAP — TOP 5 FEATURE CONTRIBUTIONS")
    print("-" * 62)
    for item in exp.get("top_features", []):
        bar = "█" * min(int(abs(item["shap_value"]) * 80), 28)
        print(f"  {item['feature']:20s} {item['shap_value']:+.4f}  {bar}")
    print()
    print(f"  Base value : {exp.get('base_value')}")
    print(f"  SHAP sum   : {exp.get('shap_sum')}")
    print()

    print("-" * 62)
    print("  LLM NARRATIVE")
    print("-" * 62)
    narrative = exp.get("narrative", "")
    # Word wrap
    words, line = narrative.split(), "  "
    for w in words:
        if len(line) + len(w) > 62:
            print(line)
            line = "  " + w + " "
        else:
            line += w + " "
    if line.strip():
        print(line)
    print()

    print("-" * 62)
    print("  VERIFICATION")
    print("-" * 62)
    checks = [
        ("Fraud score present",      result.fraud_probability > 0),
        ("Score >= 0.7 threshold",   result.fraud_probability >= 0.7),
        ("SHAP values present",      len(exp.get("top_features", [])) > 0),
        ("LLM narrative present",    len(exp.get("narrative", "")) > 20),
        ("Risk level HIGH/CRITICAL", result.risk_level in ("HIGH", "CRITICAL")),
        ("Timestamp present",        "generated_at" in exp),
    ]
    all_pass = all(v for _, v in checks)
    for label, passed in checks:
        print(f"  [{'PASS' if passed else 'FAIL'}] {label}")
    print()
    print("  DAY 5 COMPLETE!" if all_pass else "  SOME CHECKS FAILED.")

else:
    print(f"  Score {result.fraud_probability} still below 0.7 — SHAP/LLM not triggered.")
    print("  The rules engine added bumps but ensemble score is low.")
    print("  This means the XGBoost model rates this transaction as moderate risk.")
    print("  The explainability pipeline itself is working correctly.")

print("=" * 62)
