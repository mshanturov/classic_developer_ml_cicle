from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.ml_pipeline.data import FEATURE_COLUMNS
from src.ml_pipeline.model import SeedsModelTrainer

CLASS_LABELS = {
    1: "Kama",
    2: "Rosa",
    3: "Canadian",
}


class ModelNotReadyError(RuntimeError):
    """Raised when prediction is requested before model is loaded."""


@dataclass
class ModelService:
    model_path: Path

    def __post_init__(self) -> None:
        self._model = None
        self.reload_model()

    def reload_model(self) -> None:
        if self.model_path.exists():
            self._model = SeedsModelTrainer.load_model(self.model_path)
        else:
            self._model = None

    def predict(self, features: dict[str, float]) -> tuple[int, str]:
        if self._model is None:
            raise ModelNotReadyError(
                f"Model file {self.model_path} is missing. Train model before running API predictions."
            )

        input_df = pd.DataFrame([[features[column] for column in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)
        predicted_value = int(self._model.predict(input_df)[0])
        class_name = CLASS_LABELS.get(predicted_value, "Unknown")
        return predicted_value, class_name
