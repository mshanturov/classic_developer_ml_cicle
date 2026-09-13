from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, status

from src.api.schemas import PredictRequest, PredictResponse
from src.api.service import ModelNotReadyError, ModelService

MODEL_PATH = Path("artifacts/model.joblib")
service = ModelService(model_path=MODEL_PATH)

app = FastAPI(title="Wheat Seeds Classifier", version="1.0.0")


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    try:
        predicted_class, class_name = service.predict(request.model_dump())
    except ModelNotReadyError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error

    return PredictResponse(predicted_class=predicted_class, class_name=class_name)
