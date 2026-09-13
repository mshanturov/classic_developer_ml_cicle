from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.ml_pipeline.config import ModelConfig
from src.ml_pipeline.evaluate import ModelEvaluator
from src.ml_pipeline.model import SeedsModelTrainer


def test_training_and_evaluation(tmp_path: Path) -> None:
    train_df = pd.DataFrame(
        {
            "area": [15.26, 14.88, 14.29, 13.84, 16.14, 14.38],
            "perimeter": [14.84, 14.57, 14.09, 13.94, 14.99, 14.21],
            "compactness": [0.8710, 0.8811, 0.9050, 0.8955, 0.9034, 0.8951],
            "kernel_length": [5.763, 5.554, 5.291, 5.324, 5.658, 5.386],
            "kernel_width": [3.312, 3.333, 3.337, 3.379, 3.562, 3.312],
            "asymmetry_coefficient": [2.221, 1.018, 2.699, 2.259, 1.355, 2.462],
            "groove_length": [5.220, 4.956, 4.825, 4.805, 5.175, 4.956],
            "class": [1, 1, 1, 2, 2, 2],
        }
    )

    test_df = pd.DataFrame(
        {
            "area": [13.99, 15.69, 14.70],
            "perimeter": [13.83, 14.75, 14.21],
            "compactness": [0.9183, 0.9058, 0.9153],
            "kernel_length": [5.119, 5.527, 5.205],
            "kernel_width": [3.383, 3.514, 3.466],
            "asymmetry_coefficient": [5.234, 1.599, 1.767],
            "groove_length": [4.781, 5.046, 4.649],
            "class": [3, 3, 3],
        }
    )

    trainer = SeedsModelTrainer(
        ModelConfig(n_estimators=20, max_depth=4, random_state=42, test_size=0.2)
    )
    model = trainer.train(train_df)

    model_path = tmp_path / "model.joblib"
    SeedsModelTrainer.save_model(model, model_path)

    loaded_model = SeedsModelTrainer.load_model(model_path)
    metrics = ModelEvaluator().evaluate(loaded_model, test_df)

    assert model_path.exists()
    assert "accuracy" in metrics
    assert "f1_macro" in metrics
