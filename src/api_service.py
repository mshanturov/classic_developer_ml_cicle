from __future__ import annotations

import configparser
import os
from pathlib import Path
import pickle

import pandas as pd
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from sklearn.preprocessing import StandardScaler

try:
    from kafka_bus import MessageBusError, PredictionEventBus, create_prediction_event_bus
    from prediction_store import PredictionStore, StoreError, create_prediction_store
except ModuleNotFoundError:
    from src.kafka_bus import MessageBusError, PredictionEventBus, create_prediction_event_bus
    from src.prediction_store import PredictionStore, StoreError, create_prediction_store


class PredictRequest(BaseModel):
    area: float = Field(..., gt=0)
    perimeter: float = Field(..., gt=0)
    compactness: float = Field(..., gt=0)
    kernel_length: float = Field(..., gt=0)
    kernel_width: float = Field(..., gt=0)
    asymmetry_coefficient: float = Field(..., ge=0)
    groove_length: float = Field(..., gt=0)


class PredictionResponse(BaseModel):
    request_id: str
    model: str
    predicted_class: int


class InferenceService:
    def __init__(self, prediction_store: PredictionStore, event_bus: PredictionEventBus) -> None:
        self.prediction_store = prediction_store
        self.event_bus = event_bus

        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

        x_train = pd.read_csv(self.config["SPLIT_DATA"]["x_train"], index_col=0)
        self.scaler = StandardScaler()
        self.scaler.fit(x_train)

        self._loaded_models: dict[str, object] = {}
        self.message_bus_backend = os.getenv("MESSAGE_BUS_BACKEND", "kafka").strip().lower()

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

    def _build_prediction_event(
        self,
        request_id: str,
        model_name: str,
        predicted_class: int,
        payload: dict[str, float],
    ) -> dict[str, object]:
        return {
            "event_type": "prediction.created",
            "request_id": request_id,
            "model": model_name,
            "predicted_class": predicted_class,
            "payload": payload,
        }

    def predict_and_store(self, model_name: str, request: PredictRequest) -> PredictionResponse:
        model = self.load_model(model_name)
        payload = request.model_dump()

        x_frame = pd.DataFrame([payload])
        x_scaled = self.scaler.transform(x_frame)
        predicted_value = int(model.predict(x_scaled)[0])

        request_id = self.prediction_store.save_prediction(
            request_payload=payload,
            model_name=model_name,
            predicted_class=predicted_value,
        )

        event = self._build_prediction_event(
            request_id=request_id,
            model_name=model_name,
            predicted_class=predicted_value,
            payload=payload,
        )
        self.event_bus.publish_prediction_event(event)

        # For unit tests/local dry-runs without Kafka consumer.
        if self.message_bus_backend == "inmemory":
            self.prediction_store.save_consumed_event(request_id, event)

        return PredictionResponse(request_id=request_id, model=model_name, predicted_class=predicted_value)


app = FastAPI(title="Wheat Seeds API with Vault + Redis + Kafka", version="4.0.0")


def get_inference_service() -> InferenceService:
    service = getattr(app.state, "inference_service", None)
    if service is None:
        prediction_store = create_prediction_store()
        event_bus = create_prediction_event_bus()
        service = InferenceService(prediction_store=prediction_store, event_bus=event_bus)
        app.state.inference_service = service
    return service


@app.on_event("startup")
def startup() -> None:
    get_inference_service()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/inference-requests/{request_key}")
def save_inference_request(request_key: str, request: PredictRequest) -> dict[str, str]:
    try:
        service = get_inference_service()
        service.prediction_store.save_inference_request(request_key, request.model_dump())
    except StoreError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error

    return {"status": "saved", "request_key": request_key}


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictRequest, model: str = "RAND_FOREST") -> PredictionResponse:
    try:
        service = get_inference_service()
        return service.predict_and_store(model, request)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error
    except (StoreError, MessageBusError) as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error


@app.post("/predict/from-redis", response_model=PredictionResponse)
def predict_from_redis(request_key: str, model: str = "RAND_FOREST") -> PredictionResponse:
    try:
        service = get_inference_service()
        payload = service.prediction_store.get_inference_request(request_key)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inference request with key '{request_key}' was not found.",
            )
        validated_payload = PredictRequest.model_validate(payload)
        return service.predict_and_store(model, validated_payload)
    except HTTPException:
        raise
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    except (StoreError, MessageBusError) as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error


@app.get("/predictions/{request_id}")
def get_prediction(request_id: str) -> dict[str, object]:
    try:
        service = get_inference_service()
        prediction = service.prediction_store.get_prediction(request_id)
    except StoreError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error

    if prediction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction with request_id '{request_id}' was not found.",
        )
    return prediction


@app.get("/consumed-events/{request_id}")
def get_consumed_event(request_id: str) -> dict[str, object]:
    try:
        service = get_inference_service()
        consumed_event = service.prediction_store.get_consumed_event(request_id)
    except StoreError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error

    if consumed_event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consumed event for request_id '{request_id}' was not found.",
        )

    return consumed_event
