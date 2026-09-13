from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.ml_pipeline.config import ConfigLoader
from src.ml_pipeline.evaluate import ModelEvaluator
from src.ml_pipeline.model import SeedsModelTrainer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train Wheat Seeds classifier")
    parser.add_argument("--train-path", default="data/processed/train.csv")
    parser.add_argument("--test-path", default="data/processed/test.csv")
    parser.add_argument("--model-path", default="artifacts/model.joblib")
    parser.add_argument("--metrics-path", default="artifacts/metrics.json")
    parser.add_argument("--config", default="config.ini")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    config = ConfigLoader(args.config).load()
    trainer = SeedsModelTrainer(config)
    evaluator = ModelEvaluator()

    train_df = pd.read_csv(args.train_path)
    test_df = pd.read_csv(args.test_path)

    model = trainer.train(train_df)
    metrics = evaluator.evaluate(model, test_df)

    trainer.save_model(model, Path(args.model_path))
    evaluator.save_metrics(metrics, Path(args.metrics_path))

    print("Training completed")
    print(metrics)


if __name__ == "__main__":
    main()
