"""Thin async wrapper over the algo feed websocket."""
from __future__ import annotations

import asyncio
import inspect
import json
from typing import AsyncIterator, Optional

import websockets
from websockets.exceptions import ConnectionClosed

from .models import TapeEvent

DEFAULT_URL = "ws://127.0.0.1:7412"


async def _maybe_await(result) -> None:
    """Await the result if it is awaitable; otherwise do nothing (sync callback)."""
    if inspect.isawaitable(result):
        await result


def event_matches(ev: TapeEvent, side: str) -> bool:
    """True if the event is a new-high (side='high') or new-low (side='low'),
    including the combined new_high_and_low."""
    return side in ev.event


def parse_frame(raw: str) -> Optional[TapeEvent]:
    """Parse one egress frame. Returns None for anything that is not a TAPE_EVENT."""
    obj = json.loads(raw)
    if obj.get("type") != "TAPE_EVENT":
        return None
    return TapeEvent.model_validate(obj)


def build_watch(symbols: list[str]) -> dict:
    """Build the SUBSCRIBE_WATCH frame that replaces the price_update watch set."""
    return {"type": "SUBSCRIBE_WATCH", "symbols": [s.upper() for s in symbols]}


def build_summary(enabled: bool = True) -> dict:
    """Build the SUBSCRIBE_SUMMARY frame that toggles the market_summary stream."""
    return {"type": "SUBSCRIBE_SUMMARY", "enabled": enabled}


class AlgoFeed:
    """Async context manager. ``async for ev in feed`` yields typed TapeEvents."""

    def __init__(self, url: str = DEFAULT_URL):
        self.url = url
        self._ws = None

    async def _connect(self) -> None:
        self._ws = await websockets.connect(self.url)

    async def __aenter__(self) -> "AlgoFeed":
        await self._connect()
        return self

    async def __aexit__(self, *exc) -> None:
        if self._ws is not None:
            await self._ws.close()

    def __aiter__(self) -> "AlgoFeed":
        return self

    async def __anext__(self) -> TapeEvent:
        async for raw in self._ws:
            ev = parse_frame(raw)
            if ev is not None:
                return ev
        raise StopAsyncIteration

    async def watch(self, symbols: list[str]) -> None:
        """Subscribe to price_update ticks for ``symbols`` (replaces the prior set)."""
        await self._ws.send(json.dumps(build_watch(symbols)))

    async def unwatch(self) -> None:
        """Clear the price_update watch set."""
        await self._ws.send(json.dumps(build_watch([])))

    async def subscribe_summary(self, enabled: bool = True) -> None:
        """Toggle the periodic market_summary stream on or off."""
        await self._ws.send(json.dumps(build_summary(enabled)))

    async def new_highs(self) -> AsyncIterator[TapeEvent]:
        """Yield only new-high events (new_high, new_high_and_low)."""
        async for ev in self:
            if event_matches(ev, "high"):
                yield ev

    async def new_lows(self) -> AsyncIterator[TapeEvent]:
        """Yield only new-low events (new_low, new_high_and_low)."""
        async for ev in self:
            if event_matches(ev, "low"):
                yield ev

    async def summaries(self) -> AsyncIterator[TapeEvent]:
        """Yield only market_summary events."""
        async for ev in self:
            if ev.event == "market_summary":
                yield ev

    async def run(self, handler, *, watch=None, summary=False, reconnect=True) -> None:
        """Own the whole lifecycle: connect, (re)subscribe, iterate, dispatch,
        reconnect. ``handler(ev)`` may be sync or async. Blocks until cancelled."""
        backoff = 0.5
        while True:
            try:
                if self._ws is None:
                    await self._connect()
                if watch is not None:
                    await self.watch(watch)
                if summary:
                    await self.subscribe_summary(True)
                backoff = 0.5  # reset after a healthy connect
                async for ev in self:
                    await _maybe_await(handler(ev))
                # Stream ended (socket closed cleanly).
                if not reconnect:
                    return
            except (ConnectionClosed, OSError):
                if not reconnect:
                    raise
            self._ws = None
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 30.0)

    async def notify_when(self, condition, action, *, once=None,
                          watch=None, summary=False, reconnect=True) -> None:
        """Declarative wrapper over run(): for each event where condition(ev) is
        true (and, with once=, the key hasn't fired), call/await action(ev)."""
        seen = set()

        async def handler(ev):
            if not condition(ev):
                return
            if once is not None:
                key = once(ev)
                if key in seen:
                    return
                seen.add(key)
            await _maybe_await(action(ev))

        await self.run(handler, watch=watch, summary=summary, reconnect=reconnect)
