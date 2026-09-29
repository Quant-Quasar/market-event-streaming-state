from dataclasses import asdict, dataclass, field
import json
from uuid import uuid4


@dataclass(frozen=True)
class MarketDataEvent:
    """One tick of market data. Frozen = immutable, like an event should be."""
    symbol: str
    price: float
    quantity: int
    ts_ms: int  # event time in epoch milliseconds
    side: str = "BUY"
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        symbol = self.symbol.strip().upper()
        side = self.side.strip().upper()
        if not symbol:
            raise ValueError("symbol must not be empty")
        if self.price <= 0:
            raise ValueError("price must be positive")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        if self.ts_ms <= 0:
            raise ValueError("ts_ms must be positive")
        if side not in {"BUY", "SELL"}:
            raise ValueError("side must be BUY or SELL")
        if not self.id.strip():
            raise ValueError("id must not be empty")
        object.__setattr__(self, "symbol", symbol)
        object.__setattr__(self, "side", side)

    @property
    def event_id(self) -> str:
        """Stable identity used to make Redis updates replay-safe."""
        return self.id

    @property
    def signed_quantity(self) -> int:
        return self.quantity if self.side == "BUY" else -self.quantity

    def to_bytes(self) -> bytes:
        # Kafka carries raw bytes; we serialize to JSON for portability.
        return json.dumps(asdict(self)).encode("utf-8")

    @staticmethod
    def from_bytes(raw: bytes) -> "MarketDataEvent":
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("event payload must be a JSON object")
        return MarketDataEvent(**payload)
