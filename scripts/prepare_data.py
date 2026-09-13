from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.ml_pipeline.data import DatasetPaths, SeedsDataPreprocessor


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare Wheat Seeds dataset")
    parser.add_argument("--input", default="data/raw/seeds_dataset.txt")
    parser.add_argument("--train-output", default="data/processed/train.csv")
    parser.add_argument("--test-output", default="data/processed/test.csv")
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    preprocessor = SeedsDataPreprocessor(
        paths=DatasetPaths(
            raw_path=Path(args.input),
            train_path=Path(args.train_output),
            test_path=Path(args.test_output),
        ),
        test_size=args.test_size,
        random_state=args.random_state,
    )
    train_df, test_df = preprocessor.split_and_save()
    print(f"Train rows: {len(train_df)} | Test rows: {len(test_df)}")


if __name__ == "__main__":
    main()
