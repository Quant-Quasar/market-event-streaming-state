"""Print current Redis positions as JSON."""

import json
import os

import redis

from app.feed import SYMBOLS
from app.metrics import health_snapshot
from app.state import PositionStore


def main() -> None:
    client = redis.Redis(
        host=os.environ.get("REDIS_HOST", "localhost"),
        port=int(os.environ.get("REDIS_PORT", "6379")),
        decode_responses=True,
    )
    print(json.dumps(health_snapshot(PositionStore(client), SYMBOLS), indent=2))


if __name__ == "__main__":
    main()
