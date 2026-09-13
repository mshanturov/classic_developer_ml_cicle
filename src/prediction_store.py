from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from typing import Protocol
from uuid import uuid4

from redis import Redis
from redis.exceptions import RedisError


class StoreError(RuntimeError):
    """Raised when data source operations fail."""


class PredictionStore(Protocol):
    def save_inference_request(self, request_key: str, payload: dict[str, float]) -> None:
        ...

    def get_inference_request(self, request_key: str) -> dict[str, float] | None:
        ...

    def save_prediction(
        self,
        request_payload: dict[str, float],
        model_name: str,
        predicted_class: int,
    ) -> str:
        ...

    def get_prediction(self, request_id: str) -> dict[str, object] | None:
        ...


@dataclass
class InMemoryPredictionStore:
    key_prefix: str = "lab2"

    def __post_init__(self) -> None:
        self._inference_requests: dict[str, dict[str, float]] = {}
        self._predictions: dict[str, dict[str, object]] = {}

    def save_inference_request(self, request_key: str, payload: dict[str, float]) -> None:
        self._inference_requests[request_key] = payload

    def get_inference_request(self, request_key: str) -> dict[str, float] | None:
        return self._inference_requests.get(request_key)

    def save_prediction(
        self,
        request_payload: dict[str, float],
        model_name: str,
        predicted_class: int,
    ) -> str:
        request_id = str(uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        self._predictions[request_id] = {
            "request_id": request_id,
            "model": model_name,
            "predicted_class": predicted_class,
            "created_at": created_at,
            "payload": request_payload,
        }
        return request_id

    def get_prediction(self, request_id: str) -> dict[str, object] | None:
        return self._predictions.get(request_id)


@dataclass
class RedisPredictionStore:
    redis_url: str
    key_prefix: str = "lab2"

    def __post_init__(self) -> None:
        self._client = Redis.from_url(self.redis_url, decode_responses=True)
        try:
            self._client.ping()
        except RedisError as error:
            raise StoreError("Failed to connect to Redis. Check REDIS_URL and credentials.") from error

    def _request_key(self, request_key: str) -> str:
        return f"{self.key_prefix}:inference_request:{request_key}"

    def _prediction_key(self, request_id: str) -> str:
        return f"{self.key_prefix}:prediction:{request_id}"

    def save_inference_request(self, request_key: str, payload: dict[str, float]) -> None:
        try:
            self._client.set(self._request_key(request_key), json.dumps(payload))
        except RedisError as error:
            raise StoreError("Failed to write inference request to Redis.") from error

    def get_inference_request(self, request_key: str) -> dict[str, float] | None:
        try:
            raw_payload = self._client.get(self._request_key(request_key))
        except RedisError as error:
            raise StoreError("Failed to read inference request from Redis.") from error

        if raw_payload is None:
            return None
        return json.loads(raw_payload)

    def save_prediction(
        self,
        request_payload: dict[str, float],
        model_name: str,
        predicted_class: int,
    ) -> str:
        request_id = str(uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        payload = {
            "request_id": request_id,
            "model": model_name,
            "predicted_class": predicted_class,
            "created_at": created_at,
            "payload": request_payload,
        }

        try:
            self._client.set(self._prediction_key(request_id), json.dumps(payload))
        except RedisError as error:
            raise StoreError("Failed to write prediction to Redis.") from error

        return request_id

    def get_prediction(self, request_id: str) -> dict[str, object] | None:
        try:
            raw_prediction = self._client.get(self._prediction_key(request_id))
        except RedisError as error:
            raise StoreError("Failed to read prediction from Redis.") from error

        if raw_prediction is None:
            return None
        return json.loads(raw_prediction)


def create_prediction_store() -> PredictionStore:
    backend = os.getenv("PREDICTION_STORE_BACKEND", "redis").strip().lower()
    key_prefix = os.getenv("REDIS_KEY_PREFIX", "lab2")

    if backend == "inmemory":
        return InMemoryPredictionStore(key_prefix=key_prefix)

    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        raise StoreError(
            "REDIS_URL is not set. Provide it via environment (for example in docker-compose/.env)."
        )

    return RedisPredictionStore(redis_url=redis_url, key_prefix=key_prefix)
