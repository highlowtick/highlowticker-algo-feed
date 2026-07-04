import json

from hlt_algo_feed.feed import AlgoFeed, parse_frame

_BASE = {
    "type": "TAPE_EVENT", "symbol": "AAPL", "event": "new_high",
    "ts": "2026-07-03T14:00:00.000Z",
    "high_count": 1, "low_count": 0,
    "market_high_rate_30s": 0, "market_high_rate_1m": 0,
    "market_low_rate_30s": 0, "market_low_rate_1m": 0,
    "volume_spike": False,
    "is_week52_high": False, "is_week52_low": False,
}


def make_event(**over):
    """Build a valid TapeEvent; override any field via kwargs."""
    return parse_frame(json.dumps({**_BASE, **over}))


class FakeFeed(AlgoFeed):
    """AlgoFeed with no socket: yields scripted events, then StopAsyncIteration."""

    def __init__(self, events, fail_connects=0):
        super().__init__()
        self._events = list(events)
        self._fail_connects = fail_connects
        self.connects = 0

    async def _connect(self):
        self.connects += 1
        if self.connects <= self._fail_connects:
            raise OSError("simulated connect failure")
        self._ws = object()

    async def __anext__(self):
        if self._events:
            return self._events.pop(0)
        raise StopAsyncIteration

    async def watch(self, symbols):
        pass

    async def subscribe_summary(self, enabled=True):
        pass
