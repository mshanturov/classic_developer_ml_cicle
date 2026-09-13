from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(1, os.path.join(os.getcwd(), "src"))

from prediction_store import InMemoryPredictionStore, resolve_kafka_settings, resolve_redis_url


class TestInMemoryPredictionStore(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryPredictionStore(key_prefix="lab2-test")

    def test_save_and_get_inference_request(self) -> None:
        key = "req-1"
        payload = {
            "area": 10.0,
            "perimeter": 5.0,
            "compactness": 0.8,
            "kernel_length": 2.0,
            "kernel_width": 1.0,
            "asymmetry_coefficient": 0.2,
            "groove_length": 1.2,
        }

        self.store.save_inference_request(key, payload)
        restored_payload = self.store.get_inference_request(key)
        self.assertEqual(payload, restored_payload)

    def test_save_and_get_prediction(self) -> None:
        payload = {
            "area": 10.0,
            "perimeter": 5.0,
            "compactness": 0.8,
            "kernel_length": 2.0,
            "kernel_width": 1.0,
            "asymmetry_coefficient": 0.2,
            "groove_length": 1.2,
        }

        request_id = self.store.save_prediction(payload, "RAND_FOREST", 2)
        stored_prediction = self.store.get_prediction(request_id)

        self.assertIsNotNone(stored_prediction)
        assert stored_prediction is not None
        self.assertEqual(stored_prediction["model"], "RAND_FOREST")
        self.assertEqual(stored_prediction["predicted_class"], 2)

    def test_save_and_get_consumed_event(self) -> None:
        event = {
            "event_type": "prediction.created",
            "request_id": "abc",
            "model": "RAND_FOREST",
            "predicted_class": 1,
        }
        self.store.save_consumed_event("abc", event)
        restored_event = self.store.get_consumed_event("abc")
        self.assertEqual(restored_event, event)


class TestRedisSecretResolution(unittest.TestCase):
    def setUp(self) -> None:
        self._saved_env = os.environ.copy()
        for key in [
            "REDIS_URL",
            "REDIS_URL_FILE",
            "REDIS_HOST",
            "REDIS_PORT",
            "REDIS_DB",
            "REDIS_PASSWORD",
            "REDIS_HOST_FILE",
            "REDIS_PORT_FILE",
            "REDIS_DB_FILE",
            "REDIS_PASSWORD_FILE",
            "KAFKA_BOOTSTRAP_SERVERS",
            "KAFKA_BOOTSTRAP_SERVERS_FILE",
            "KAFKA_TOPIC",
            "KAFKA_TOPIC_FILE",
            "KAFKA_GROUP_ID",
            "KAFKA_GROUP_ID_FILE",
        ]:
            os.environ.pop(key, None)

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._saved_env)

    def test_resolve_url_from_single_secret_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            redis_url_file = Path(tmp) / "redis_url"
            redis_url_file.write_text("redis://default:test-pass@redis:6379/0", encoding="utf-8")

            os.environ["REDIS_URL_FILE"] = str(redis_url_file)
            resolved_url = resolve_redis_url()
            self.assertEqual(resolved_url, "redis://default:test-pass@redis:6379/0")

    def test_resolve_url_from_split_secret_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            host_file = Path(tmp) / "redis_host"
            port_file = Path(tmp) / "redis_port"
            db_file = Path(tmp) / "redis_db"
            password_file = Path(tmp) / "redis_password"

            host_file.write_text("redis", encoding="utf-8")
            port_file.write_text("6379", encoding="utf-8")
            db_file.write_text("1", encoding="utf-8")
            password_file.write_text("another-pass", encoding="utf-8")

            os.environ["REDIS_HOST_FILE"] = str(host_file)
            os.environ["REDIS_PORT_FILE"] = str(port_file)
            os.environ["REDIS_DB_FILE"] = str(db_file)
            os.environ["REDIS_PASSWORD_FILE"] = str(password_file)

            resolved_url = resolve_redis_url()
            self.assertEqual(resolved_url, "redis://default:another-pass@redis:6379/1")

    def test_resolve_kafka_settings_from_secret_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bootstrap_file = Path(tmp) / "kafka_bootstrap_servers"
            topic_file = Path(tmp) / "kafka_topic"
            group_file = Path(tmp) / "kafka_group_id"

            bootstrap_file.write_text("kafka:9092", encoding="utf-8")
            topic_file.write_text("prediction-events", encoding="utf-8")
            group_file.write_text("consumer-group-1", encoding="utf-8")

            os.environ["KAFKA_BOOTSTRAP_SERVERS_FILE"] = str(bootstrap_file)
            os.environ["KAFKA_TOPIC_FILE"] = str(topic_file)
            os.environ["KAFKA_GROUP_ID_FILE"] = str(group_file)

            settings = resolve_kafka_settings()
            self.assertEqual(settings.bootstrap_servers, "kafka:9092")
            self.assertEqual(settings.topic, "prediction-events")
            self.assertEqual(settings.group_id, "consumer-group-1")


if __name__ == "__main__":
    unittest.main()
