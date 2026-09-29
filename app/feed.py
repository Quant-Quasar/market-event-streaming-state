import random
import time
from app.events import MarketDataEvent
from app.producer import build_producer, publish

# A few symbols to spread across partitions.
SYMBOLS = ["AAPL", "MSFT", "GOOG", "AMZN"]


def random_walk_tick(symbol: str, last: float) -> MarketDataEvent:
    # Nudge the price by a small random step — a crude but useful price model.
    step = random.uniform(-0.5, 0.5)
    price = round(max(1.0, last + step), 2)
    quantity = random.randint(1, 100)
    side = random.choice(["BUY", "SELL"])
    return MarketDataEvent(symbol, price, quantity, int(time.time() * 1000), side)


def run_feed(rate_per_sec: float = 20.0, ticks: int = 1000) -> None:
    producer = build_producer()
    prices = {s: 100.0 for s in SYMBOLS}
    delay = 1.0 / rate_per_sec
    for _ in range(ticks):
        symbol = random.choice(SYMBOLS)
        event = random_walk_tick(symbol, prices[symbol])
        prices[symbol] = event.price
        publish(producer, event)
        time.sleep(delay)
    # flush() blocks until every buffered record is actually delivered.
    producer.flush()


if __name__ == "__main__":
    run_feed()
