import os

from kafka import KafkaProducer
from app.events import MarketDataEvent

TOPIC = "market-data"
DEAD_LETTER_TOPIC = "market-data-dlq"


def build_producer(bootstrap: str | None = None) -> KafkaProducer:
    bootstrap = bootstrap or os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    return KafkaProducer(bootstrap_servers=bootstrap)


def publish(producer: KafkaProducer, event: MarketDataEvent) -> None:
    # The KEY (symbol) decides the partition. All ticks for one symbol land on
    # the same partition, so they stay strictly ordered relative to each other.
    producer.send(
        TOPIC,
        key=event.symbol.encode("utf-8"),
        value=event.to_bytes(),
    )


def publish_dead_letter(producer: KafkaProducer, raw: bytes) -> None:
    """Publish synchronously so its source offset is not committed too early."""
    producer.send(DEAD_LETTER_TOPIC, value=raw).get(timeout=10)
