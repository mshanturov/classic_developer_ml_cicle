from __future__ import annotations

import os
import sys
import unittest

from fastapi.testclient import TestClient

sys.path.insert(1, os.path.join(os.getcwd(), "src"))

from api_service import app


class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def test_healthcheck(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)

    def test_predict_success(self) -> None:
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
        self.assertIn(response.json()["predicted_class"], [1, 2, 3])

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
