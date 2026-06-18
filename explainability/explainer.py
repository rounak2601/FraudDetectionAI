"""
explainability/explainer.py
============================
Step 3 of Day 5: Unified wrapper combining SHAP + LLM into one call.

WHAT THIS DOES:
  Single function call in — full explanation object out.
  Everything downstream (scorer.py, API, dashboard) calls only this.

  Input:  transaction dict + fraud_probability
  Output: {
    top_features:    [...],        # top 5 SHAP features
    all_shap_values: {...},        # all 29 features
    base_value:      float,        # XGBoost base rate
    shap_sum:        float,        # sum of SHAP contributions
    narrative:       str,          # 2-sentence LLM explanation
    fraud_probability: float,      # echo back for convenience
    generated_at:    str,          # ISO timestamp
  }

USAGE:
  from explainability.explainer import FraudExplainer
  explainer = FraudExplainer()
  result = explainer.explain(transaction_dict, fraud_probability=0.87)
"""

from datetime import datetime, timezone
from typing import Any, Dict

from explainability.shap_explainer import SHAPExplainer
from explainability.llm_explainer  import LLMExplainer


class FraudExplainer:
    """
    Combines SHAPExplainer + LLMExplainer into one clean interface.
    Instantiate once at startup; call .explain() per transaction.
    """

    def __init__(
        self,
        artifacts_dir: str = "models/artifacts",
        llm_model:     str = "qwen2.5:1.5b",
        llm_host:      str = "http://localhost:11434",
    ):
        print("[FraudExplainer] Initialising...")
        self.shap_explainer = SHAPExplainer(artifacts_dir=artifacts_dir)
        self.llm_explainer  = LLMExplainer(model=llm_model, host=llm_host)
        print("[FraudExplainer] Ready.")

    def explain(
        self,
        transaction:       Dict[str, Any],
        fraud_probability: float,
    ) -> dict:
        """
        Generate full explanation for a high-risk transaction.

        Args:
            transaction:       Raw transaction dict (same format scorer receives)
            fraud_probability: Final fraud score from the ensemble (0–1)

        Returns:
            Complete explanation dict with SHAP values + LLM narrative
        """
        # Step 1: SHAP — which features matter and by how much
        shap_results = self.shap_explainer.explain(transaction)

        # Step 2: LLM — plain English narrative for fraud analysts
        narrative = self.llm_explainer.explain(
            transaction       = transaction,
            shap_results      = shap_results,
            fraud_probability = fraud_probability,
        )

        # Step 3: Combine into one unified response object
        return {
            "top_features":      shap_results["top_features"],
            "all_shap_values":   shap_results["all_shap_values"],
            "base_value":        shap_results["base_value"],
            "shap_sum":          shap_results["shap_sum"],
            "narrative":         narrative,
            "fraud_probability": round(fraud_probability, 4),
            "generated_at":      datetime.now(timezone.utc).isoformat(),
        }
