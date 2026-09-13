from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.ml_pipeline.config import ModelConfig
from src.ml_pipeline.data import FEATURE_COLUMNS, TARGET_COLUMN


@dataclass(frozen=True)
class TrainingArtifacts:
    model_path: Path
    metrics_path: Path


class SeedsModelTrainer:
    """Trains and persists a RandomForest pipeline for seeds classification."""

    def __init__(self, config: ModelConfig) -> None:
        self.config = config

    def build_pipeline(self) -> Pipeline:
        classifier = RandomForestClassifier(
            n_estimators=self.config.n_estimators,
            max_depth=self.config.max_depth,
            random_state=self.config.random_state,
        )
        return Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                ("classifier", classifier),
            ]
        )

    def train(self, train_df: pd.DataFrame) -> Pipeline:
        x_train = train_df[FEATURE_COLUMNS]
        y_train = train_df[TARGET_COLUMN]

        pipeline = self.build_pipeline()
        pipeline.fit(x_train, y_train)
        return pipeline

    @staticmethod
    def save_model(model: Pipeline, model_path: Path) -> None:
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, model_path)

    @staticmethod
    def load_model(model_path: Path) -> Pipeline:
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        return joblib.load(model_path)
