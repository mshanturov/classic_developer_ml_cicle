from __future__ import annotations

import configparser
from pathlib import Path
import pickle

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sklearn.preprocessing import StandardScaler


class PredictRequest(BaseModel):
    area: float = Field(..., gt=0)
    perimeter: float = Field(..., gt=0)
    compactness: float = Field(..., gt=0)
    kernel_length: float = Field(..., gt=0)
    kernel_width: float = Field(..., gt=0)
    asymmetry_coefficient: float = Field(..., ge=0)
    groove_length: float = Field(..., gt=0)


class InferenceService:
    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

        x_train = pd.read_csv(self.config["SPLIT_DATA"]["x_train"], index_col=0)
        self.scaler = StandardScaler()
        self.scaler.fit(x_train)

        self._loaded_models: dict[str, object] = {}

    def _resolve_model_path(self, model_name: str) -> Path:
        if model_name == "LOG_REG":
            path = self.config["LOG_REG"]["path"]
        elif model_name == "RAND_FOREST":
            path = self.config["RAND_FOREST"]["path"]
        elif model_name == "KNN":
            path = self.config["KNN"]["path"]
        elif model_name == "GNB":
            path = self.config["GNB"]["path"]
        elif model_name == "SVM":
            path = self.config["SVM"]["path"]
        elif model_name == "D_TREE":
            path = self.config["D_TREE"]["path"]
        else:
            raise ValueError(f"Unsupported model: {model_name}")
        return Path(path)

    def load_model(self, model_name: str) -> object:
        if model_name in self._loaded_models:
            return self._loaded_models[model_name]

        path = self._resolve_model_path(model_name)
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")

        with path.open("rb") as file:
            model = pickle.load(file)
        self._loaded_models[model_name] = model
        return model

    def predict(self, model_name: str, request: PredictRequest) -> int:
        model = self.load_model(model_name)
        x_frame = pd.DataFrame([request.model_dump()])
        x_scaled = self.scaler.transform(x_frame)
        predicted_value = int(model.predict(x_scaled)[0])
        return predicted_value


app = FastAPI(title="Wheat Seeds API", version="1.0.0")
service = InferenceService()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict")
def predict(request: PredictRequest, model: str = "RAND_FOREST") -> dict[str, int | str]:
    try:
        predicted_class = service.predict(model, request)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    return {"model": model, "predicted_class": predicted_class}
