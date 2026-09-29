import os
import logging
import redis
from app.consumer import build_consumer, run
from app.state import PositionStore
from app.handler import safe_apply
from app.producer import build_producer, publish_dead_letter

logging.basicConfig(level=logging.INFO)


def main() -> None:
    client = redis.Redis(
        host=os.environ.get("REDIS_HOST", "redis"),
        port=int(os.environ.get("REDIS_PORT", "6379")),
        decode_responses=True,
    )
    store = PositionStore(client)
    consumer = build_consumer(group_id="position-tracker")
    dlq_producer = build_producer()

    # Each raw Kafka message flows through the robust handler into Redis state.
    def handle(raw: bytes) -> None:
        safe_apply(store, raw, lambda payload: publish_dead_letter(dlq_producer, payload))

    run(consumer, handle)


if __name__ == "__main__":
    main()
