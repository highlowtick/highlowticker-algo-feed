import pytest

from conftest import make_event, FakeFeed


@pytest.mark.asyncio
async def test_new_highs_filters_high_events():
    feed = FakeFeed([
        make_event(event="new_high", symbol="A"),
        make_event(event="price_update", symbol="B"),
        make_event(event="new_low", symbol="C"),
        make_event(event="new_high_and_low", symbol="D"),
    ])
    out = [ev.symbol async for ev in feed.new_highs()]
    assert out == ["A", "D"]


@pytest.mark.asyncio
async def test_new_lows_filters_low_events():
    feed = FakeFeed([
        make_event(event="new_high", symbol="A"),
        make_event(event="new_low", symbol="C"),
        make_event(event="new_high_and_low", symbol="D"),
    ])
    out = [ev.symbol async for ev in feed.new_lows()]
    assert out == ["C", "D"]


@pytest.mark.asyncio
async def test_summaries_filters_market_summary():
    feed = FakeFeed([
        make_event(event="new_high", symbol="A"),
        make_event(event="market_summary", symbol="-"),
    ])
    out = [ev.event async for ev in feed.summaries()]
    assert out == ["market_summary"]
