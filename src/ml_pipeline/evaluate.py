from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.pipeline import Pipeline

from src.ml_pipeline.data import FEATURE_COLUMNS, TARGET_COLUMN


class ModelEvaluator:
    """Evaluates trained model quality and stores metrics."""

    def evaluate(self, model: Pipeline, test_df: pd.DataFrame) -> dict[str, float | dict[str, float]]:
        x_test = test_df[FEATURE_COLUMNS]
        y_test = test_df[TARGET_COLUMN]

        predictions = model.predict(x_test)

        accuracy = accuracy_score(y_test, predictions)
        macro_f1 = f1_score(y_test, predictions, average="macro")
        report = classification_report(y_test, predictions, output_dict=True, zero_division=0)

        return {
            "accuracy": float(accuracy),
            "f1_macro": float(macro_f1),
            "class_metrics": {
                key: value
                for key, value in report.items()
                if key in {"1", "2", "3"}
            },
        }

    @staticmethod
    def save_metrics(metrics: dict[str, object], metrics_path: Path) -> None:
        metrics_path.parent.mkdir(parents=True, exist_ok=True)
        with metrics_path.open("w", encoding="utf-8") as file:
            json.dump(metrics, file, ensure_ascii=False, indent=2)
