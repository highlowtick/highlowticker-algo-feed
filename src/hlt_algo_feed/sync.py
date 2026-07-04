"""Blocking convenience wrappers — hide asyncio for the common cases.

Each builds an AlgoFeed and runs the matching async driver via asyncio.run.
Must NOT be called from inside a running event loop (asyncio.run raises there,
which is the correct signal to use the async AlgoFeed methods directly)."""
import asyncio

from .feed import AlgoFeed


def notify_when(when, then, *, once=None, watch=None, summary=False,
                reconnect=True, url=None):
    feed = AlgoFeed(url) if url else AlgoFeed()
    asyncio.run(feed.notify_when(
        when, then, once=once, watch=watch, summary=summary, reconnect=reconnect))


def run(handler, *, watch=None, summary=False, reconnect=True, url=None):
    feed = AlgoFeed(url) if url else AlgoFeed()
    asyncio.run(feed.run(
        handler, watch=watch, summary=summary, reconnect=reconnect))
