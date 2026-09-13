from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(1, os.path.join(os.getcwd(), "src"))

from kafka_bus import InMemoryPredictionEventBus, create_prediction_event_bus


class TestKafkaBus(unittest.TestCase):
    def test_inmemory_bus_collects_events(self) -> None:
        bus = InMemoryPredictionEventBus()
        event = {
            "event_type": "prediction.created",
            "request_id": "request-1",
            "model": "RAND_FOREST",
            "predicted_class": 2,
        }
        bus.publish_prediction_event(event)
        self.assertEqual(len(bus._events), 1)
        self.assertEqual(bus._events[0]["request_id"], "request-1")

    def test_factory_returns_inmemory_bus(self) -> None:
        previous = os.environ.get("MESSAGE_BUS_BACKEND")
        os.environ["MESSAGE_BUS_BACKEND"] = "inmemory"
        try:
            bus = create_prediction_event_bus()
            self.assertIsInstance(bus, InMemoryPredictionEventBus)
        finally:
            if previous is None:
                os.environ.pop("MESSAGE_BUS_BACKEND", None)
            else:
                os.environ["MESSAGE_BUS_BACKEND"] = previous


if __name__ == "__main__":
    unittest.main()
