from __future__ import annotations

import argparse
import json
import time

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

try:
    from prediction_store import StoreError, create_prediction_store, resolve_kafka_settings
except ModuleNotFoundError:
    from src.prediction_store import StoreError, create_prediction_store, resolve_kafka_settings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Kafka consumer for model prediction events")
    parser.add_argument("--max-messages", type=int, default=0)
    parser.add_argument("--startup-retries", type=int, default=20)
    parser.add_argument("--startup-delay-seconds", type=int, default=3)
    return parser.parse_args()


def build_consumer(retries: int, delay_seconds: int) -> KafkaConsumer:
    settings = resolve_kafka_settings()

    for attempt in range(1, retries + 1):
        try:
            return KafkaConsumer(
                settings.topic,
                bootstrap_servers=[server.strip() for server in settings.bootstrap_servers.split(",") if server.strip()],
                auto_offset_reset="earliest",
                group_id=settings.group_id,
                enable_auto_commit=True,
                value_deserializer=lambda payload: json.loads(payload.decode("utf-8")),
            )
        except NoBrokersAvailable:
            if attempt == retries:
                raise
            time.sleep(delay_seconds)

    raise RuntimeError("Failed to initialize Kafka consumer")


def main() -> None:
    args = parse_args()
    store = create_prediction_store()

    try:
        consumer = build_consumer(args.startup_retries, args.startup_delay_seconds)
    except NoBrokersAvailable as error:
        raise RuntimeError("Kafka broker is unavailable for consumer startup") from error

    processed_messages = 0
    print("Kafka consumer started")

    try:
        for message in consumer:
            event = message.value
            request_id = str(event.get("request_id", "")).strip()
            if request_id:
                store.save_consumed_event(request_id, event)
            processed_messages += 1
            print(f"Consumed event #{processed_messages} request_id={request_id}")

            if args.max_messages > 0 and processed_messages >= args.max_messages:
                break
    except StoreError as error:
        raise RuntimeError(f"Failed to persist consumed event: {error}") from error
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
