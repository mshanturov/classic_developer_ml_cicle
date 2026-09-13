from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
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

    def save_consumed_event(self, request_id: str, event_payload: dict[str, object]) -> None:
        ...

    def get_consumed_event(self, request_id: str) -> dict[str, object] | None:
        ...


@dataclass(frozen=True)
class KafkaSettings:
    bootstrap_servers: str
    topic: str
    group_id: str


@dataclass
class InMemoryPredictionStore:
    key_prefix: str = "lab4"

    def __post_init__(self) -> None:
        self._inference_requests: dict[str, dict[str, float]] = {}
        self._predictions: dict[str, dict[str, object]] = {}
        self._consumed_events: dict[str, dict[str, object]] = {}

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

    def save_consumed_event(self, request_id: str, event_payload: dict[str, object]) -> None:
        self._consumed_events[request_id] = event_payload

    def get_consumed_event(self, request_id: str) -> dict[str, object] | None:
        return self._consumed_events.get(request_id)


@dataclass
class RedisPredictionStore:
    redis_url: str
    key_prefix: str = "lab4"

    def __post_init__(self) -> None:
        self._client = Redis.from_url(self.redis_url, decode_responses=True)
        try:
            self._client.ping()
        except RedisError as error:
            raise StoreError("Failed to connect to Redis. Check resolved secrets and Redis availability.") from error

    def _request_key(self, request_key: str) -> str:
        return f"{self.key_prefix}:inference_request:{request_key}"

    def _prediction_key(self, request_id: str) -> str:
        return f"{self.key_prefix}:prediction:{request_id}"

    def _consumed_event_key(self, request_id: str) -> str:
        return f"{self.key_prefix}:consumed_event:{request_id}"

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

    def save_consumed_event(self, request_id: str, event_payload: dict[str, object]) -> None:
        try:
            self._client.set(self._consumed_event_key(request_id), json.dumps(event_payload))
        except RedisError as error:
            raise StoreError("Failed to write consumed event to Redis.") from error

    def get_consumed_event(self, request_id: str) -> dict[str, object] | None:
        try:
            raw_event = self._client.get(self._consumed_event_key(request_id))
        except RedisError as error:
            raise StoreError("Failed to read consumed event from Redis.") from error

        if raw_event is None:
            return None
        return json.loads(raw_event)


def _read_secret_file(path_value: str) -> str:
    path = Path(path_value)
    if not path.exists():
        raise StoreError(f"Secret file does not exist: {path}")
    return path.read_text(encoding="utf-8").strip()


def _get_secret_value(env_name: str, file_env_name: str, required: bool = True) -> str:
    file_path = os.getenv(file_env_name)
    if file_path:
        value = _read_secret_file(file_path)
        if value:
            return value

    value = os.getenv(env_name, "").strip()
    if value:
        return value

    if required:
        raise StoreError(
            f"Secret is missing: provide {env_name} or {file_env_name}."
        )
    return ""


def resolve_redis_url() -> str:
    redis_url_file = os.getenv("REDIS_URL_FILE", "").strip()
    if redis_url_file:
        return _read_secret_file(redis_url_file)

    redis_url = os.getenv("REDIS_URL", "").strip()
    if redis_url:
        return redis_url

    host = _get_secret_value("REDIS_HOST", "REDIS_HOST_FILE")
    port = _get_secret_value("REDIS_PORT", "REDIS_PORT_FILE")
    db = _get_secret_value("REDIS_DB", "REDIS_DB_FILE", required=False) or "0"
    password = _get_secret_value("REDIS_PASSWORD", "REDIS_PASSWORD_FILE")

    return f"redis://default:{password}@{host}:{port}/{db}"


def resolve_kafka_settings() -> KafkaSettings:
    bootstrap_servers = _get_secret_value(
        "KAFKA_BOOTSTRAP_SERVERS",
        "KAFKA_BOOTSTRAP_SERVERS_FILE",
    )
    topic = _get_secret_value("KAFKA_TOPIC", "KAFKA_TOPIC_FILE")
    group_id = _get_secret_value(
        "KAFKA_GROUP_ID",
        "KAFKA_GROUP_ID_FILE",
        required=False,
    ) or "ml-prediction-consumer"

    return KafkaSettings(
        bootstrap_servers=bootstrap_servers,
        topic=topic,
        group_id=group_id,
    )


def create_prediction_store() -> PredictionStore:
    backend = os.getenv("PREDICTION_STORE_BACKEND", "redis").strip().lower()
    key_prefix = os.getenv("REDIS_KEY_PREFIX", "lab4")

    if backend == "inmemory":
        return InMemoryPredictionStore(key_prefix=key_prefix)

    return RedisPredictionStore(redis_url=resolve_redis_url(), key_prefix=key_prefix)
