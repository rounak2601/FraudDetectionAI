"""
models/inference/scorer.py  (Day 5 update)
==========================================
WHAT CHANGED FROM DAY 4:
  - FraudExplainer imported and initialised at startup
  - score() now calls explainer when fraud_probability >= 0.7
  - explanation field contains full SHAP + LLM output for high-risk
  - explanation field contains simple scores for low-risk (saves compute)
  - Everything else (FraudScore, score_batch, rules) unchanged

THRESHOLD 0.7:
  Below 0.7 = LOW/MEDIUM risk — simple score explanation only
  At/above 0.7 = HIGH/CRITICAL — full SHAP + LLM explanation generated
  This matches the Day 5 spec exactly and saves compute on low-risk txns
"""

import sys
import os
import numpy as np
import pickle
import json
import onnxruntime as rt
from dataclasses import dataclass
from typing import Dict, Any

# Add project root to path so explainability imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from explainability.explainer import FraudExplainer
from models.inference.preprocessing import FeaturePreprocessor, normalize_transaction


@dataclass
class FraudScore:
    transaction_id:    str
    fraud_probability: float
    risk_level:        str          # LOW / MEDIUM / HIGH / CRITICAL
    xgb_score:         float
    isolation_score:   float
    triggered_rules:   list
    explanation:       dict
    is_fraud_predicted: bool


class FraudScorer:
    """
    Real-time fraud scorer combining XGBoost (ONNX), Isolation Forest,
    and a Meta-Learner into a single ensemble decision.
    Day 5: SHAP + LLM explanations attached for fraud_probability >= 0.7
    """

    RISK_THRESHOLDS = {
        "LOW":      (0.0,  0.3),
        "MEDIUM":   (0.3,  0.5),
        "HIGH":     (0.5,  0.75),
        "CRITICAL": (0.75, 1.0),
    }

    # Transactions scoring at or above this get full SHAP + LLM explanation
    EXPLANATION_THRESHOLD = 0.7

    def __init__(self, artifacts_dir: str | None = None):
        print("Loading FraudScorer models...")
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        artifacts_dir = artifacts_dir or os.path.join(project_root, "models", "artifacts")
        self.inline_explanations = os.getenv("INLINE_EXPLANATIONS", "false").lower() == "true"

        # ONNX runtime for XGBoost
        self.onnx_sess   = rt.InferenceSession(f"{artifacts_dir}/xgboost_model.onnx")
        self.input_name  = self.onnx_sess.get_inputs()[0].name
        self.output_name = self.onnx_sess.get_outputs()[1].name

        # Isolation Forest
        with open(f"{artifacts_dir}/isolation_forest_model.pkl", "rb") as f:
            self.if_model = pickle.load(f)

        with open(f"{artifacts_dir}/if_normalization.pkl", "rb") as f:
            self.if_stats = pickle.load(f)

        # Meta-Learner
        with open(f"{artifacts_dir}/meta_learner.pkl", "rb") as f:
            self.meta_model = pickle.load(f)

        # Feature config
        with open(f"{artifacts_dir}/feature_names.pkl", "rb") as f:
            self.feature_names = pickle.load(f)

        with open(f"{artifacts_dir}/feature_mapping.json", "r") as f:
            self.feature_mapping = json.load(f)

        self.name_to_numeric = {v: k for k, v in self.feature_mapping.items()}
        self.preprocessor = FeaturePreprocessor(self.feature_names, artifacts_dir)
        self.encoding_mode = self.preprocessor.encoding_mode
        self.fraud_threshold = float(os.getenv("MODEL_FRAUD_THRESHOLD", "0.5"))

        # Day 5: SHAP + LLM explainer (initialised once, reused per request)
        print("Loading FraudExplainer (SHAP + LLM)...")
        self.explainer = FraudExplainer(artifacts_dir=artifacts_dir)

        print(f"FraudScorer ready. Features: {len(self.feature_names)}; encoding={self.encoding_mode}; threshold={self.fraud_threshold}")

    def _preprocess(self, transaction: Dict[str, Any]) -> np.ndarray:
        return self.preprocessor.transform(transaction)

    def _normalize_if_score(self, raw_score: float) -> float:
        mn = self.if_stats["min"]
        mx = self.if_stats["max"]
        return float(np.clip((raw_score - mn) / (mx - mn + 1e-9), 0, 1))

    def _get_risk_level(self, probability: float) -> str:
        for level, (lo, hi) in self.RISK_THRESHOLDS.items():
            if lo <= probability < hi:
                return level
        return "CRITICAL"

    def _check_rules(self, transaction: Dict[str, Any]) -> list:
        triggered = []
        amt = float(transaction.get("TransactionAmt", transaction.get("amount", 0)))

        if amt > 5000:
            triggered.append(f"HIGH_AMOUNT: ${amt:.2f} exceeds $5,000 threshold")
        if amt > 10000:
            triggered.append(f"VERY_HIGH_AMOUNT: ${amt:.2f} exceeds $10,000 (SAR threshold)")

        card6 = str(transaction.get("card6", "")).lower()
        if card6 == "debit":
            addr1 = transaction.get("addr1", None)
            if addr1 is None or addr1 == -999:
                triggered.append("DEBIT_NO_ADDRESS: Debit card with no billing address")

        p_email = str(transaction.get("P_emaildomain", "")).lower()
        r_email = str(transaction.get("R_emaildomain", "")).lower()
        burner  = {"guerrillamail.com", "mailinator.com", "tempmail.com", "throwam.com"}
        if p_email in burner:
            triggered.append(f"BURNER_EMAIL: Purchaser using disposable email {p_email}")
        if r_email in burner:
            triggered.append(f"BURNER_EMAIL: Recipient using disposable email {r_email}")

        return triggered

    def _build_simple_explanation(
        self, xgb_score, if_score, meta_score, features_array
    ) -> dict:
        """
        Simple explanation for low/medium risk transactions (< 0.7).
        No SHAP or LLM — fast and lightweight.
        """
        top_features = {}
        for name, val in zip(self.feature_names, features_array.flatten()):
            if val != -999:
                top_features[name] = round(float(val), 4)

        return {
            "model_scores": {
                "xgboost":          round(xgb_score, 4),
                "isolation_forest": round(if_score, 4),
                "ensemble":         round(meta_score, 4),
            },
            "feature_values": top_features,
            "shap_values":    None,   # not computed for low-risk
            "narrative":      None,   # not generated for low-risk
            "explanation_type": "simple",
        }

    def score(
        self,
        transaction:    Dict[str, Any],
        transaction_id: str = "unknown",
    ) -> FraudScore:
        """
        Score a single transaction.
        Returns FraudScore with full SHAP+LLM explanation if score >= 0.7.
        """

        # 1. Normalize aliases (API `amount` -> trained feature `TransactionAmt`) and preprocess.
        transaction = normalize_transaction(transaction)
        features_array = self._preprocess(transaction)

        # 2. XGBoost via ONNX
        xgb_proba = self.onnx_sess.run(
            [self.output_name],
            {self.input_name: features_array}
        )[0][0][1]

        # 3. Isolation Forest
        if_raw   = -self.if_model.decision_function(features_array)[0]
        if_score = self._normalize_if_score(if_raw)

        # 4. Meta-Learner
        meta_input  = np.array([[xgb_proba, if_score]], dtype=np.float64)
        fraud_proba = self.meta_model.predict_proba(meta_input)[0][1]

        # 5. Rules are evidence for analysts, not arbitrary probability boosts.
        # A high-value legitimate payment must not be labelled fraud solely by rule count.
        triggered_rules = self._check_rules(transaction)

        # 6. Explanation — full SHAP+LLM for high risk, simple for low risk
        if self.inline_explanations and fraud_proba >= self.EXPLANATION_THRESHOLD:
            # Day 5: full explainability for HIGH / CRITICAL transactions
            explanation = self.explainer.explain(
                transaction       = transaction,
                fraud_probability = float(fraud_proba),
            )
            explanation["explanation_type"] = "full_shap_llm"
            explanation["model_scores"] = {
                "xgboost":          round(float(xgb_proba), 4),
                "isolation_forest": round(float(if_score), 4),
                "ensemble":         round(float(fraud_proba), 4),
            }
        else:
            explanation = self._build_simple_explanation(
                xgb_proba, if_score, fraud_proba, features_array
            )

        return FraudScore(
            transaction_id    = transaction_id,
            fraud_probability = round(float(fraud_proba), 4),
            risk_level        = self._get_risk_level(fraud_proba),
            xgb_score         = round(float(xgb_proba), 4),
            isolation_score   = round(float(if_score), 4),
            triggered_rules   = triggered_rules,
            explanation       = explanation,
            is_fraud_predicted = bool(fraud_proba >= self.fraud_threshold),
        )

    def score_batch(self, transactions: list) -> list:
        """Score a list of transactions. High-risk ones get full explanations."""
        if not transactions:
            return []

        transactions = [normalize_transaction(tx) for tx in transactions]
        features_matrix = np.vstack([self._preprocess(tx) for tx in transactions])

        xgb_probas = self.onnx_sess.run(
            [self.output_name],
            {self.input_name: features_matrix}
        )[0][:, 1]

        if_raw    = -self.if_model.decision_function(features_matrix)
        if_scores = np.clip(
            (if_raw - self.if_stats["min"]) /
            (self.if_stats["max"] - self.if_stats["min"] + 1e-9),
            0, 1
        )

        meta_input   = np.column_stack([xgb_probas, if_scores])
        fraud_probas = self.meta_model.predict_proba(meta_input)[:, 1]

        results = []
        for i, tx in enumerate(transactions):
            tx = normalize_transaction(tx)
            rules = self._check_rules(tx)
            prob  = float(fraud_probas[i])

            if self.inline_explanations and prob >= self.EXPLANATION_THRESHOLD:
                explanation = self.explainer.explain(
                    transaction       = tx,
                    fraud_probability = prob,
                )
                explanation["explanation_type"] = "full_shap_llm"
                explanation["model_scores"] = {
                    "xgboost":          round(float(xgb_probas[i]), 4),
                    "isolation_forest": round(float(if_scores[i]), 4),
                    "ensemble":         round(prob, 4),
                }
            else:
                explanation = self._build_simple_explanation(
                    xgb_probas[i], if_scores[i], prob,
                    features_matrix[i:i+1]
                )

            results.append(FraudScore(
                transaction_id    = tx.get("TransactionID", f"tx_{i}"),
                fraud_probability = round(prob, 4),
                risk_level        = self._get_risk_level(prob),
                xgb_score         = round(float(xgb_probas[i]), 4),
                isolation_score   = round(float(if_scores[i]), 4),
                triggered_rules   = rules,
                explanation       = explanation,
                is_fraud_predicted = bool(prob >= self.fraud_threshold),
            ))

        return results
