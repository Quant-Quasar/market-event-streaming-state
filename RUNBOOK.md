# Operations runbook

## Start and verify

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f feed tracker
docker compose exec tracker python -m app.snapshot
```

The topic initializer creates `market-data` with four partitions and
`market-data-dlq` with one partition.

## Inspect state

```bash
docker compose exec redis redis-cli HGETALL position:AAPL
docker compose exec tracker python -m app.snapshot
```

## Consumer lag (the key streaming metric)

Lag = how far behind the latest offset a consumer group is. Watch it with:

```bash
docker compose exec kafka kafka-consumer-groups \
  --bootstrap-server kafka:9092 \
  --describe --group position-tracker
```

If LAG climbs steadily, the tracker can't keep up — scale it out:

```bash
docker compose up -d --scale tracker=4
```

## Inspect dead letters

```bash
docker compose exec kafka kafka-console-consumer \
  --bootstrap-server kafka:9092 \
  --topic market-data-dlq --from-beginning
```

## Failure behavior

- Invalid JSON or schema: write it to the DLQ, then commit the offset.
- Redis unavailable: fail before commit so Kafka replays the event.
- Restart after Redis write but before commit: Redis deduplication prevents a
  duplicate position update.
- Rising lag: inspect tracker errors, then scale no higher than partition count.

## Reset local demo data

`docker compose down -v` permanently removes this demo's local Kafka and Redis
data.
