from app.events import MarketDataEvent
from app.handler import safe_apply


class Store:
    def __init__(self) -> None:
        self.events = []

    def apply(self, event):
        self.events.append(event)
        return True


def test_poison_event_goes_to_dead_letter() -> None:
    store = Store()
    dead = []
    assert safe_apply(store, b"not-json", dead.append) is False
    assert dead == [b"not-json"]
    assert store.events == []


def test_valid_event_is_applied() -> None:
    store = Store()
    event = MarketDataEvent("MSFT", 99.0, 3, 1_700_000_000_000)
    assert safe_apply(store, event.to_bytes(), lambda _: None) is True
    assert store.events == [event]
