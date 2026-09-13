from __future__ import annotations

from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

from src.api.app import app, service
from src.ml_pipeline.config import ModelConfig
from src.ml_pipeline.model import SeedsModelTrainer


client = TestClient(app)


def _train_minimal_model(model_path: Path) -> None:
    train_df = pd.DataFrame(
        {
            "area": [15.26, 14.88, 14.29, 13.84, 16.14, 14.38, 13.99, 15.69, 14.70],
            "perimeter": [14.84, 14.57, 14.09, 13.94, 14.99, 14.21, 13.83, 14.75, 14.21],
            "compactness": [0.8710, 0.8811, 0.9050, 0.8955, 0.9034, 0.8951, 0.9183, 0.9058, 0.9153],
            "kernel_length": [5.763, 5.554, 5.291, 5.324, 5.658, 5.386, 5.119, 5.527, 5.205],
            "kernel_width": [3.312, 3.333, 3.337, 3.379, 3.562, 3.312, 3.383, 3.514, 3.466],
            "asymmetry_coefficient": [2.221, 1.018, 2.699, 2.259, 1.355, 2.462, 5.234, 1.599, 1.767],
            "groove_length": [5.220, 4.956, 4.825, 4.805, 5.175, 4.956, 4.781, 5.046, 4.649],
            "class": [1, 1, 1, 2, 2, 2, 3, 3, 3],
        }
    )
    trainer = SeedsModelTrainer(
        ModelConfig(n_estimators=15, max_depth=3, random_state=42, test_size=0.2)
    )
    model = trainer.train(train_df)
    SeedsModelTrainer.save_model(model, model_path)


def test_healthcheck() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_predict_success(tmp_path: Path) -> None:
    model_path = tmp_path / "model.joblib"
    _train_minimal_model(model_path)

    service.model_path = model_path
    service.reload_model()

    payload = {
        "area": 15.0,
        "perimeter": 14.5,
        "compactness": 0.89,
        "kernel_length": 5.5,
        "kernel_width": 3.4,
        "asymmetry_coefficient": 1.8,
        "groove_length": 5.0,
    }

    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert response.json()["predicted_class"] in {1, 2, 3}


def test_predict_validation_error() -> None:
    response = client.post(
        "/predict",
        json={
            "area": -1,
            "perimeter": 14.5,
            "compactness": 0.89,
            "kernel_length": 5.5,
            "kernel_width": 3.4,
            "asymmetry_coefficient": 1.8,
            "groove_length": 5.0,
        },
    )
    assert response.status_code == 422
