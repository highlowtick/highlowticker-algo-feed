import asyncio

import pytest

from conftest import make_event, FakeFeed


class _Stop(Exception):
    pass


@pytest.mark.asyncio
async def test_run_dispatches_each_event():
    feed = FakeFeed([make_event(symbol="A"), make_event(symbol="B")])
    seen = []
    await feed.run(lambda ev: seen.append(ev.symbol), reconnect=False)
    assert seen == ["A", "B"]


@pytest.mark.asyncio
async def test_run_awaits_async_handler():
    feed = FakeFeed([make_event(symbol="A")])
    seen = []

    async def handler(ev):
        seen.append(ev.symbol)

    await feed.run(handler, reconnect=False)
    assert seen == ["A"]


@pytest.mark.asyncio
async def test_run_sends_watch_frame():
    feed = FakeFeed([make_event(symbol="A")])
    sent = []

    async def rec(symbols):
        sent.append(symbols)

    feed.watch = rec
    await feed.run(lambda ev: None, watch=["SPY"], reconnect=False)
    assert sent == [["SPY"]]


@pytest.mark.asyncio
async def test_run_reconnects_after_failed_connect(monkeypatch):
    async def no_sleep(_):
        return None

    monkeypatch.setattr(asyncio, "sleep", no_sleep)
    feed = FakeFeed([make_event(symbol="A")], fail_connects=1)

    def handler(ev):
        raise _Stop

    with pytest.raises(_Stop):
        await feed.run(handler, reconnect=True)
    assert feed.connects == 2  # first failed, retried, then delivered


@pytest.mark.asyncio
async def test_run_no_reconnect_raises_on_connect_failure():
    feed = FakeFeed([make_event(symbol="A")], fail_connects=1)
    with pytest.raises(OSError):
        await feed.run(lambda ev: None, reconnect=False)
    assert feed.connects == 1
