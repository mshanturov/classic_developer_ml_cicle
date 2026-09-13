from __future__ import annotations

import os
import sys
import unittest

from fastapi.testclient import TestClient

os.environ["PREDICTION_STORE_BACKEND"] = "inmemory"
os.environ["MESSAGE_BUS_BACKEND"] = "inmemory"

sys.path.insert(1, os.path.join(os.getcwd(), "src"))

from api_service import app


class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def test_healthcheck(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)

    def test_predict_and_get_stored_prediction(self) -> None:
        payload = {
            "area": 15.26,
            "perimeter": 14.84,
            "compactness": 0.871,
            "kernel_length": 5.763,
            "kernel_width": 3.312,
            "asymmetry_coefficient": 2.221,
            "groove_length": 5.22,
        }
        response = self.client.post("/predict", params={"model": "RAND_FOREST"}, json=payload)
        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertIn("request_id", body)
        self.assertIn(body["predicted_class"], [1, 2, 3])

        stored_response = self.client.get(f"/predictions/{body['request_id']}")
        self.assertEqual(stored_response.status_code, 200)
        self.assertEqual(stored_response.json()["request_id"], body["request_id"])

        consumed_response = self.client.get(f"/consumed-events/{body['request_id']}")
        self.assertEqual(consumed_response.status_code, 200)
        self.assertEqual(consumed_response.json()["event_type"], "prediction.created")

    def test_predict_from_redis_request(self) -> None:
        request_key = "unit-test-request"
        payload = {
            "area": 18.72,
            "perimeter": 16.19,
            "compactness": 0.8977,
            "kernel_length": 6.006,
            "kernel_width": 3.857,
            "asymmetry_coefficient": 5.324,
            "groove_length": 5.879,
        }

        save_response = self.client.post(f"/inference-requests/{request_key}", json=payload)
        self.assertEqual(save_response.status_code, 200)

        predict_response = self.client.post(
            "/predict/from-redis",
            params={"request_key": request_key, "model": "RAND_FOREST"},
        )
        self.assertEqual(predict_response.status_code, 200)
        body = predict_response.json()
        self.assertIn("request_id", body)

        consumed_response = self.client.get(f"/consumed-events/{body['request_id']}")
        self.assertEqual(consumed_response.status_code, 200)

    def test_predict_validation(self) -> None:
        invalid_payload = {
            "area": -1,
            "perimeter": 14.84,
            "compactness": 0.871,
            "kernel_length": 5.763,
            "kernel_width": 3.312,
            "asymmetry_coefficient": 2.221,
            "groove_length": 5.22,
        }
        response = self.client.post("/predict", params={"model": "RAND_FOREST"}, json=invalid_payload)
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
