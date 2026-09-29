import time
from app.events import MarketDataEvent


def event_age_ms(event: MarketDataEvent, now_ms: int | None = None) -> float:
    # How stale is this event by the time we process it? End-to-end latency
    # from the producer's timestamp to now — the number that must stay small.
    now = now_ms if now_ms is not None else int(time.time() * 1000)
    return float(now - event.ts_ms)


def health_snapshot(store, symbols: list[str]) -> dict:
    # A cheap liveness/PnL snapshot: read each symbol's live state from Redis.
    out = {}
    for symbol in symbols:
        snap = store.snapshot(symbol)
        out[symbol] = {
            "net_qty": int(snap.get("net_qty", 0) or 0),
            "last_price": float(snap.get("last_price", 0) or 0),
            "market_value": float(snap.get("market_value", 0) or 0),
            "pnl": float(snap.get("pnl", 0) or 0),
        }
    return out
