from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(1, os.path.join(os.getcwd(), "src"))

from prediction_store import InMemoryPredictionStore


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


if __name__ == "__main__":
    unittest.main()
