"""Recreate the exact LabelEncoder class ordering used by the trained models."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.preprocessing import LabelEncoder

COLUMNS = ["ProductCD", "card4", "card6", "P_emaildomain", "R_emaildomain"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Path to train_transaction.csv")
    parser.add_argument(
        "--output",
        default="models/artifacts/categorical_encoders.json",
        help="Output JSON path",
    )
    args = parser.parse_args()

    frame = pd.read_csv(args.data, usecols=COLUMNS)
    encoders: dict[str, list[str]] = {}
    for column in COLUMNS:
        encoder = LabelEncoder()
        encoder.fit(frame[column].astype(str))
        encoders[column] = [str(value) for value in encoder.classes_.tolist()]
        print(f"{column}: {len(encoders[column])} classes")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(encoders, indent=2), encoding="utf-8")
    print(f"Saved exact categorical encoders to {output}")


if __name__ == "__main__":
    main()
