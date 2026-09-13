from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
import requests


def test_container_scenario() -> None:
    if os.getenv("RUN_CONTAINER_SCENARIO") != "1":
        pytest.skip("Functional container scenario is executed only in CD/container stage.")

    scenario_path = Path("scenario.json")
    scenario = json.loads(scenario_path.read_text(encoding="utf-8"))

    base_url = scenario["base_url"]

    health = requests.get(f"{base_url}/health", timeout=10)
    assert health.status_code == 200

    for case in scenario["cases"]:
        response = requests.post(
            f"{base_url}/predict",
            json=case["payload"],
            timeout=10,
        )
        assert response.status_code == case["expected_status"]
        if response.status_code == 200:
            body = response.json()
            assert body["predicted_class"] in {1, 2, 3}
