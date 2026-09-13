from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.ml_pipeline.data import DatasetPaths, SeedsDataPreprocessor


def test_preprocessor_splits_data(tmp_path: Path) -> None:
    raw_path = tmp_path / "seeds_dataset.txt"
    rows = [
        "15.26 14.84 0.8710 5.763 3.312 2.221 5.220 1",
        "14.88 14.57 0.8811 5.554 3.333 1.018 4.956 1",
        "14.29 14.09 0.9050 5.291 3.337 2.699 4.825 1",
        "13.84 13.94 0.8955 5.324 3.379 2.259 4.805 2",
        "16.14 14.99 0.9034 5.658 3.562 1.355 5.175 2",
        "14.38 14.21 0.8951 5.386 3.312 2.462 4.956 2",
        "13.99 13.83 0.9183 5.119 3.383 5.234 4.781 3",
        "15.69 14.75 0.9058 5.527 3.514 1.599 5.046 3",
        "14.70 14.21 0.9153 5.205 3.466 1.767 4.649 3",
    ]
    raw_path.write_text("\n".join(rows), encoding="utf-8")

    train_path = tmp_path / "train.csv"
    test_path = tmp_path / "test.csv"

    preprocessor = SeedsDataPreprocessor(
        paths=DatasetPaths(raw_path=raw_path, train_path=train_path, test_path=test_path),
        test_size=0.33,
        random_state=42,
    )

    train_df, test_df = preprocessor.split_and_save()

    assert train_path.exists()
    assert test_path.exists()
    assert len(train_df) + len(test_df) == 9

    loaded_train = pd.read_csv(train_path)
    assert "class" in loaded_train.columns
