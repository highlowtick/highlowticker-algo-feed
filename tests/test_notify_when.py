import pytest

from conftest import make_event, FakeFeed


@pytest.mark.asyncio
async def test_fires_only_when_condition_true():
    feed = FakeFeed([
        make_event(event="new_high", symbol="A"),
        make_event(event="new_low", symbol="B"),
    ])
    fired = []
    await feed.notify_when(
        lambda ev: ev.event == "new_high",
        lambda ev: fired.append(ev.symbol),
        reconnect=False,
    )
    assert fired == ["A"]


@pytest.mark.asyncio
async def test_once_dedupes_by_key():
    feed = FakeFeed([
        make_event(event="new_high", symbol="A", high_count=5),
        make_event(event="new_high", symbol="A", high_count=6),
        make_event(event="new_high", symbol="B", high_count=5),
    ])
    fired = []
    await feed.notify_when(
        lambda ev: True,
        lambda ev: fired.append(ev.symbol),
        once=lambda ev: (ev.symbol, "high"),
        reconnect=False,
    )
    assert fired == ["A", "B"]  # second A deduped


@pytest.mark.asyncio
async def test_async_action_is_awaited():
    feed = FakeFeed([make_event(symbol="A")])
    fired = []

    async def action(ev):
        fired.append(ev.symbol)

    await feed.notify_when(lambda ev: True, action, reconnect=False)
    assert fired == ["A"]
