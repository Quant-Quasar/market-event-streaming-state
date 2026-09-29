import json

import pytest

from app.events import MarketDataEvent


def test_event_round_trip_and_signed_quantity() -> None:
    event = MarketDataEvent("aapl", 101.5, 7, 1_700_000_000_000, "sell")
    decoded = MarketDataEvent.from_bytes(event.to_bytes())
    assert decoded == event
    assert decoded.symbol == "AAPL"
    assert decoded.signed_quantity == -7


def test_invalid_event_is_rejected() -> None:
    with pytest.raises(ValueError):
        MarketDataEvent.from_bytes(json.dumps({"symbol": "", "price": -1, "quantity": 0, "ts_ms": 0}).encode())
