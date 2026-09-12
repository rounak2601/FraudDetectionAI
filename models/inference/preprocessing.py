"""Shared, deterministic preprocessing for scoring and SHAP."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import numpy as np

CATEGORICAL_COLS = {"ProductCD", "card4", "card6", "P_emaildomain", "R_emaildomain"}
ALIASES = {"TransactionAmt": "amount"}


def normalize_transaction(transaction: Mapping[str, Any]) -> dict[str, Any]:
    normalized = dict(transaction)
    for canonical, alias in ALIASES.items():
        if canonical not in normalized and alias in normalized:
            normalized[canonical] = normalized[alias]
    return normalized


class FeaturePreprocessor:
    def __init__(self, feature_names: list[str], artifacts_dir: str | Path):
        self.feature_names = feature_names
        encoder_path = Path(artifacts_dir) / "categorical_encoders.json"
        self.encoders: dict[str, dict[str, int]] = {}
        self.encoding_mode = "deterministic_fallback"
        if encoder_path.exists():
            raw = json.loads(encoder_path.read_text(encoding="utf-8"))
            self.encoders = {
                column: {str(value): index for index, value in enumerate(classes)}
                for column, classes in raw.items()
            }
            self.encoding_mode = "training_compatible"
        else:
            print(
                "WARNING: categorical_encoders.json is missing. "
                "Run models/training/build_categorical_encoders.py for exact training-compatible inference."
            )

    @staticmethod
    def _stable_fallback(value: str) -> float:
        digest = hashlib.sha256(value.encode("utf-8")).digest()
        return float(int.from_bytes(digest[:4], "big") % 10000)

    def _encode_category(self, feature: str, value: Any) -> float:
        text = str(value)
        mapping = self.encoders.get(feature)
        if mapping is not None:
            # Unknown categories are deliberately represented as missing.
            return float(mapping.get(text, -999))
        return self._stable_fallback(text)

    def transform(self, transaction: Mapping[str, Any]) -> np.ndarray:
        transaction = normalize_transaction(transaction)
        row: list[float] = []
        for feature in self.feature_names:
            value = transaction.get(feature, -999)
            if value is None or value == "" or (
                isinstance(value, (float, np.floating)) and np.isnan(value)
            ):
                value = -999.0
            elif feature in CATEGORICAL_COLS:
                value = self._encode_category(feature, value)
            else:
                try:
                    value = float(value)
                except (TypeError, ValueError):
                    value = -999.0
            row.append(float(value))
        return np.asarray(row, dtype=np.float32).reshape(1, -1)
