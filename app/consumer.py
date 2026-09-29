import os

from kafka import KafkaConsumer
from app.producer import TOPIC


def build_consumer(group_id: str, bootstrap: str | None = None) -> KafkaConsumer:
    # All consumers sharing a group_id form ONE logical consumer: Kafka splits
    # the topic's partitions across them, so each event is handled exactly once
    # by the group. Add an instance and the partitions rebalance automatically.
    bootstrap = bootstrap or os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    return KafkaConsumer(
        TOPIC,
        bootstrap_servers=bootstrap,
        group_id=group_id,
        enable_auto_commit=False,
        auto_offset_reset="earliest",
    )


def run(consumer: KafkaConsumer, handle) -> None:
    for message in consumer:
        # Commit only after the state update (or DLQ write) succeeds. An
        # infrastructure failure therefore causes Kafka to replay the event.
        handle(message.value)
        consumer.commit()
