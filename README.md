# Replay-Safe Market Event Pipeline

A runnable Kafka-to-Redis pipeline that simulates market trades, partitions
events by symbol, and maintains live position and mark-to-market P&L state.
It demonstrates consumer groups, manual offset commits, dead-letter handling,
and idempotent Redis updates.

## Architecture

```text
feed -> market-data (4 Kafka partitions) -> tracker consumer group -> Redis
                   invalid payloads \-> market-data-dlq
```

For each symbol, Redis stores signed net quantity, cash, last price, and event
time. Market value and P&L are calculated from that state. A Redis idempotency
key prevents a replayed Kafka event from changing the position twice.

## Run it

Requirements: Docker Desktop with Docker Compose.

```bash
docker compose up --build
```

In another terminal, inspect all four symbols:

```bash
docker compose exec tracker python -m app.snapshot
```

Stop the local services with `docker compose down`.

## Test it locally

Use Python 3.11 through 3.13:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pytest
```

See [RUNBOOK.md](RUNBOOK.md) for operations and failure scenarios.

## Design notes

- Kafka keys events by symbol, preserving per-symbol ordering.
- Offsets are committed only after Redis or the DLQ accepts a record.
- The Redis update and replay check run in one Lua script.
- Deduplication keys expire after seven days to bound storage.
- This project uses simulated trades and is not a trading system.

Built as a hands-on implementation of a replay-safe market event pipeline.
