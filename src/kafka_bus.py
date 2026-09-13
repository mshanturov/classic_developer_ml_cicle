from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from typing import Protocol

from kafka import KafkaProducer
from kafka.errors import KafkaError

try:
    from prediction_store import resolve_kafka_settings
except ModuleNotFoundError:
    from src.prediction_store import resolve_kafka_settings


class MessageBusError(RuntimeError):
    """Raised when producer cannot publish events."""


class PredictionEventBus(Protocol):
    def publish_prediction_event(self, event: dict[str, object]) -> None:
        ...


@dataclass
class InMemoryPredictionEventBus:
    _events: list[dict[str, object]] = field(default_factory=list)

    def publish_prediction_event(self, event: dict[str, object]) -> None:
        self._events.append(event)


@dataclass
class KafkaPredictionEventBus:
    bootstrap_servers: str
    topic: str

    def __post_init__(self) -> None:
        try:
            self._producer = KafkaProducer(
                bootstrap_servers=[server.strip() for server in self.bootstrap_servers.split(",") if server.strip()],
                value_serializer=lambda payload: json.dumps(payload).encode("utf-8"),
                retries=5,
                acks="all",
            )
        except KafkaError as error:
            raise MessageBusError("Failed to initialize Kafka producer.") from error

    def publish_prediction_event(self, event: dict[str, object]) -> None:
        try:
            future = self._producer.send(self.topic, event)
            future.get(timeout=10)
            self._producer.flush(timeout=10)
        except KafkaError as error:
            raise MessageBusError("Failed to publish prediction event to Kafka.") from error


def create_prediction_event_bus() -> PredictionEventBus:
    backend = os.getenv("MESSAGE_BUS_BACKEND", "kafka").strip().lower()
    if backend == "inmemory":
        return InMemoryPredictionEventBus()

    kafka_settings = resolve_kafka_settings()
    return KafkaPredictionEventBus(
        bootstrap_servers=kafka_settings.bootstrap_servers,
        topic=kafka_settings.topic,
    )
