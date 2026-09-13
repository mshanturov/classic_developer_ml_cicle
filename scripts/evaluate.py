from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.ml_pipeline.evaluate import ModelEvaluator
from src.ml_pipeline.model import SeedsModelTrainer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate Wheat Seeds classifier")
    parser.add_argument("--test-path", default="data/processed/test.csv")
    parser.add_argument("--model-path", default="artifacts/model.joblib")
    parser.add_argument("--metrics-path", default="artifacts/metrics_cd.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    model = SeedsModelTrainer.load_model(Path(args.model_path))
    test_df = pd.read_csv(args.test_path)

    evaluator = ModelEvaluator()
    metrics = evaluator.evaluate(model, test_df)
    evaluator.save_metrics(metrics, Path(args.metrics_path))
    print(metrics)


if __name__ == "__main__":
    main()
