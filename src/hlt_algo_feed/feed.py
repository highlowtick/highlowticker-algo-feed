"""Thin async wrapper over the algo feed websocket."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Optional

import websockets

from .models import TapeEvent

DEFAULT_URL = "ws://127.0.0.1:7412"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def parse_frame(raw: str) -> Optional[TapeEvent]:
    """Parse one egress frame. Returns None for anything that is not a TAPE_EVENT."""
    obj = json.loads(raw)
    if obj.get("type") != "TAPE_EVENT":
        return None
    return TapeEvent.model_validate(obj)


def build_watch(symbols: list[str]) -> dict:
    """Build the ALGO_WEB_WATCH frame that replaces the price_update watch set."""
    return {
        "type": "ALGO_CUSTOM",
        "tag": "ALGO_WEB_WATCH",
        "timestamp": _now_iso(),
        "data": {"symbols": [s.upper() for s in symbols]},
    }


def build_summary(enabled: bool = True) -> dict:
    """Build the ALGO_WEB_SUMMARY frame that toggles the market_summary stream."""
    return {
        "type": "ALGO_CUSTOM",
        "tag": "ALGO_WEB_SUMMARY",
        "timestamp": _now_iso(),
        "data": {"enabled": enabled},
    }


class AlgoFeed:
    """Async context manager. ``async for ev in feed`` yields typed TapeEvents."""

    def __init__(self, url: str = DEFAULT_URL):
        self.url = url
        self._ws = None

    async def __aenter__(self) -> "AlgoFeed":
        self._ws = await websockets.connect(self.url)
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
