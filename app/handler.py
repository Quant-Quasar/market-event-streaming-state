import logging
from collections.abc import Callable
from app.events import MarketDataEvent
from app.state import PositionStore

log = logging.getLogger("tracker")


def safe_apply(
    store: PositionStore,
    raw: bytes,
    dead_letter: Callable[[bytes], None],
) -> bool:
    # A single bad record must not crash the whole consumer. Parse defensively;
    # on failure, route the raw bytes to a dead-letter sink and keep going.
    try:
        event = MarketDataEvent.from_bytes(raw)
    except Exception as exc:  # noqa: BLE001 - we deliberately catch all here
        log.warning("dropping poison message: %s", exc)
        dead_letter(raw)
        return False
    return store.apply(event)


def make_event_id(event: MarketDataEvent) -> str:
    # A stable id for one logical event: symbol + exact timestamp + qty.
    # Lets us de-duplicate if at-least-once delivery replays an event.
    return event.event_id
