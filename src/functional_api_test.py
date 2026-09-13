from __future__ import annotations

import json
import os
from pathlib import Path

import requests


def assert_status(response: requests.Response, expected_status: int, context: str) -> None:
    if response.status_code != expected_status:
        raise RuntimeError(
            f"{context}: expected status {expected_status}, got {response.status_code}, body={response.text}"
        )


def main() -> None:
    scenario = json.loads(Path("scenario.json").read_text(encoding="utf-8"))
    base_url = os.getenv("SCENARIO_BASE_URL", scenario["base_url"])

    health_response = requests.get(f"{base_url}/health", timeout=10)
    assert_status(health_response, 200, "healthcheck")

    direct_case = scenario["direct_case"]
    direct_response = requests.post(
        f"{base_url}/predict",
        params={"model": direct_case["model"]},
        json=direct_case["payload"],
        timeout=10,
    )
    assert_status(direct_response, direct_case["expected_status"], "direct prediction")

    request_id = direct_response.json()["request_id"]
    stored_response = requests.get(f"{base_url}/predictions/{request_id}", timeout=10)
    assert_status(stored_response, 200, "stored prediction fetch")

    redis_case = scenario["redis_case"]
    save_request_response = requests.post(
        f"{base_url}/inference-requests/{redis_case['request_key']}",
        json=redis_case["payload"],
        timeout=10,
    )
    assert_status(save_request_response, 200, "save inference request to redis")

    redis_predict_response = requests.post(
        f"{base_url}/predict/from-redis",
        params={"request_key": redis_case["request_key"], "model": redis_case["model"]},
        timeout=10,
    )
    assert_status(redis_predict_response, redis_case["expected_status"], "predict from redis request")

    redis_prediction_id = redis_predict_response.json()["request_id"]
    redis_stored_response = requests.get(f"{base_url}/predictions/{redis_prediction_id}", timeout=10)
    assert_status(redis_stored_response, 200, "stored redis prediction fetch")

    invalid_case = scenario["invalid_case"]
    invalid_response = requests.post(
        f"{base_url}/predict",
        params={"model": invalid_case["model"]},
        json=invalid_case["payload"],
        timeout=10,
    )
    assert_status(invalid_response, invalid_case["expected_status"], "invalid payload")

    print("Functional API scenario passed")


if __name__ == "__main__":
    main()
