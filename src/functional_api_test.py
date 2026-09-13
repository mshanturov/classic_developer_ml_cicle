from __future__ import annotations

import json
from pathlib import Path

import requests


def main() -> None:
    scenario = json.loads(Path("scenario.json").read_text(encoding="utf-8"))
    base_url = scenario["base_url"]

    health_response = requests.get(f"{base_url}/health", timeout=10)
    if health_response.status_code != 200:
        raise RuntimeError(f"Healthcheck failed with status {health_response.status_code}")

    for case in scenario["cases"]:
        response = requests.post(
            f"{base_url}/predict",
            params={"model": case["model"]},
            json=case["payload"],
            timeout=10,
        )
        if response.status_code != case["expected_status"]:
            raise RuntimeError(
                f"Case {case['name']} failed: expected {case['expected_status']}, got {response.status_code}"
            )

    print("Functional API scenario passed")


if __name__ == "__main__":
    main()
