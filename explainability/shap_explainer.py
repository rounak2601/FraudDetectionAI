"""
explainability/shap_explainer.py
=================================
Step 1 of Day 5: SHAP-based feature attribution for the XGBoost model.

WHAT THIS DOES:
  For any transaction, computes which features pushed the fraud score
  up or down, and by how much.  Output example:
    TransactionAmt : +0.42  (pushed score UP — suspicious)
    card4          : +0.18  (pushed score UP)
    P_emaildomain  : -0.09  (pushed score DOWN — normal domain)

WHY TreeExplainer (not KernelExplainer):
  - TreeExplainer is exact for tree models (XGBoost, LightGBM, RF)
  - 100x faster than KernelExplainer
  - No background dataset needed
  - shap 0.51.0 fully supports it

IMPORTANT — CATEGORICAL ENCODING:
  Uses the EXACT same encoding as scorer.py (_preprocess method)
  so SHAP values map to the correct features.
  Categoricals are hash-encoded: abs(hash(str_val)) % 10000
"""

import pickle
import numpy as np
import shap
from typing import Any, Dict


# Must match scorer.py exactly
CATEGORICAL_COLS = {"ProductCD", "card4", "card6", "P_emaildomain", "R_emaildomain"}


class SHAPExplainer:
    """
    Loads the trained XGBoost model and computes SHAP values
    for any transaction dict.
    """

    def __init__(self, artifacts_dir: str = "models/artifacts"):
        print("  [SHAPExplainer] Loading XGBoost model...")

        # TreeExplainer needs the actual model object, NOT the ONNX file
        with open(f"{artifacts_dir}/xgboost_model.pkl", "rb") as f:
            self.xgb_model = pickle.load(f)

        with open(f"{artifacts_dir}/feature_names.pkl", "rb") as f:
            self.feature_names: list = pickle.load(f)

        # TreeExplainer: exact SHAP for tree-based models
        # check_additivity=False: suppresses a harmless warning in shap 0.51
        self.explainer = shap.TreeExplainer(
            self.xgb_model,
            feature_perturbation="tree_path_dependent",
        )

        print(f"  [SHAPExplainer] Ready. {len(self.feature_names)} features.")

    # ──────────────────────────────────────────────────────
    # Internal: same preprocessing as scorer.py _preprocess
    # MUST stay in sync with scorer.py
    # ──────────────────────────────────────────────────────
    def _preprocess(self, transaction: Dict[str, Any]) -> np.ndarray:
        row = []
        for feat in self.feature_names:
            val = transaction.get(feat, -999)

            if val is None or val == "" or (isinstance(val, float) and np.isnan(val)):
                val = -999.0
            elif feat in CATEGORICAL_COLS:
                if isinstance(val, str):
                    val = float(abs(hash(val)) % 10000)
                else:
                    val = float(val)
            else:
                try:
                    val = float(val)
                except (ValueError, TypeError):
                    val = -999.0

            row.append(val)

        return np.array(row, dtype=np.float32).reshape(1, -1)

    # ──────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────
    def explain(self, transaction: Dict[str, Any]) -> dict:
        """
        Compute SHAP values for one transaction.

        Returns:
            {
              "top_features":    [{"feature": str, "shap_value": float, "direction": str}, ...],  # top 5
              "all_shap_values": {"feature_name": shap_value, ...},   # all 29
              "base_value":      float,   # expected model output (avg fraud rate ~0.035)
              "shap_sum":        float,   # sum of all SHAP values (base + shap_sum ≈ fraud prob)
            }
        """
        features_array = self._preprocess(transaction)

        # shap 0.51 TreeExplainer returns an Explanation object
        # .values shape: (1, n_features, n_classes) for multi-output
        # or (1, n_features) for single output
        shap_explanation = self.explainer(features_array, check_additivity=False)

        # Extract values — handle both output shapes safely
        vals = shap_explanation.values

        if vals.ndim == 3:
            # Shape (1, n_features, 2) — binary classification
            # Index 1 = fraud class SHAP values
            shap_vals = vals[0, :, 1]
            base_val  = float(shap_explanation.base_values[0, 1])
        elif vals.ndim == 2:
            # Shape (1, n_features) — single output
            shap_vals = vals[0, :]
            base_val  = float(shap_explanation.base_values[0])
        else:
            # Fallback — flatten whatever we get
            shap_vals = vals.flatten()[: len(self.feature_names)]
            base_val  = 0.0

        shap_vals = shap_vals.astype(float)

        # Build full mapping: feature_name -> shap_value
        all_shap = {
            name: round(float(sv), 6)
            for name, sv in zip(self.feature_names, shap_vals)
        }

        # Top 5 by absolute value — these are the most influential features
        sorted_feats = sorted(all_shap.items(), key=lambda x: abs(x[1]), reverse=True)
        top_5 = [
            {
                "feature":    name,
                "shap_value": round(sv, 4),
                "direction":  "increases_fraud_risk" if sv > 0 else "decreases_fraud_risk",
            }
            for name, sv in sorted_feats[:5]
        ]

        return {
            "top_features":    top_5,
            "all_shap_values": all_shap,
            "base_value":      round(base_val, 6),
            "shap_sum":        round(float(shap_vals.sum()), 6),
        }
