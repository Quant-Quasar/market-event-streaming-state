from typing import Any
from app.events import MarketDataEvent


APPLY_EVENT = """
if redis.call('SET', KEYS[2], '1', 'NX', 'EX', ARGV[5]) == false then
  return 0
end
redis.call('HINCRBY', KEYS[1], 'net_qty', ARGV[1])
redis.call('HINCRBYFLOAT', KEYS[1], 'cash', ARGV[2])
redis.call('HSET', KEYS[1], 'last_price', ARGV[3], 'last_event_ts', ARGV[4])
return 1
"""


class PositionStore:
    """Live per-symbol state in Redis. Fast reads/writes, survives restarts."""

    def __init__(self, client: Any, dedup_ttl_seconds: int = 604800):
        self.r = client
        self.dedup_ttl_seconds = dedup_ttl_seconds

    def _key(self, symbol: str) -> str:
        return f"position:{symbol}"

    def apply(self, event: MarketDataEvent) -> bool:
        """Apply one event atomically; return False when it is a replay."""
        key = self._key(event.symbol)
        signed_qty = event.signed_quantity
        cash_delta = -(event.price * signed_qty)
        applied = self.r.eval(
            APPLY_EVENT,
            2,
            key,
            f"processed:{event.event_id}",
            signed_qty,
            cash_delta,
            event.price,
            event.ts_ms,
            self.dedup_ttl_seconds,
        )
        return bool(applied)

    def snapshot(self, symbol: str) -> dict:
        raw = self.r.hgetall(self._key(symbol))
        if not raw:
            return {}
        net_qty = int(raw.get("net_qty", 0))
        cash = float(raw.get("cash", 0.0))
        last_price = float(raw.get("last_price", 0.0))
        return {
            **raw,
            "net_qty": net_qty,
            "cash": cash,
            "last_price": last_price,
            "market_value": net_qty * last_price,
            "pnl": cash + net_qty * last_price,
        }
