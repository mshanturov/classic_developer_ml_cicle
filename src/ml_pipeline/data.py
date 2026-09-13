from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

FEATURE_COLUMNS = [
    "area",
    "perimeter",
    "compactness",
    "kernel_length",
    "kernel_width",
    "asymmetry_coefficient",
    "groove_length",
]
TARGET_COLUMN = "class"


@dataclass(frozen=True)
class DatasetPaths:
    raw_path: Path
    train_path: Path
    test_path: Path


class SeedsDataPreprocessor:
    """Prepares train/test datasets from the UCI Wheat Seeds dataset."""

    def __init__(self, paths: DatasetPaths, test_size: float, random_state: int) -> None:
        self.paths = paths
        self.test_size = test_size
        self.random_state = random_state

    def _read_raw_data(self) -> pd.DataFrame:
        if not self.paths.raw_path.exists():
            raise FileNotFoundError(
                f"Raw dataset was not found at {self.paths.raw_path}. Run scripts/download_data.py first."
            )

        dataset = pd.read_csv(self.paths.raw_path, sep=r"\s+", header=None)
        dataset.columns = [*FEATURE_COLUMNS, TARGET_COLUMN]
        return dataset

    def split_and_save(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        dataset = self._read_raw_data()

        train_df, test_df = train_test_split(
            dataset,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=dataset[TARGET_COLUMN],
        )

        self.paths.train_path.parent.mkdir(parents=True, exist_ok=True)
        self.paths.test_path.parent.mkdir(parents=True, exist_ok=True)

        train_df.to_csv(self.paths.train_path, index=False)
        test_df.to_csv(self.paths.test_path, index=False)
        return train_df, test_df
