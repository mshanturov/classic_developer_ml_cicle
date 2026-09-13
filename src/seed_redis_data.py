from __future__ import annotations

import argparse
import json
import os

import pandas as pd
from redis import Redis
from redis.exceptions import RedisError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed Redis with inference request payloads")
    parser.add_argument("--input", default="data/Test_Seeds_X.csv")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--prefix", default="lab2")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        raise RuntimeError("REDIS_URL is not set.")

    dataframe = pd.read_csv(args.input, index_col=0).head(args.limit)
    client = Redis.from_url(redis_url, decode_responses=True)

    try:
        client.ping()
    except RedisError as error:
        raise RuntimeError("Could not connect to Redis with provided REDIS_URL") from error

    for idx, (_, row) in enumerate(dataframe.iterrows(), start=1):
        request_key = f"sample-{idx}"
        payload = {column: float(value) for column, value in row.items()}
        redis_key = f"{args.prefix}:inference_request:{request_key}"
        client.set(redis_key, json.dumps(payload))

    print(f"Seeded {len(dataframe)} inference requests into Redis.")


if __name__ == "__main__":
    main()
