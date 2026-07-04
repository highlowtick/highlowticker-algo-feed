import pytest

import hlt_algo_feed
from hlt_algo_feed.feed import AlgoFeed


def test_sync_notify_when_runs_async(monkeypatch):
    rec = {}

    async def fake(self, condition, action, *, once=None, watch=None,
                   summary=False, reconnect=True):
        rec["watch"] = watch
        rec["cond_true"] = condition(object())

    monkeypatch.setattr(AlgoFeed, "notify_when", fake)
    hlt_algo_feed.notify_when(when=lambda ev: True, then=lambda ev: None, watch=["A"])
    assert rec["watch"] == ["A"] and rec["cond_true"] is True


def test_sync_run_runs_async(monkeypatch):
    rec = {}

    async def fake(self, handler, *, watch=None, summary=False, reconnect=True):
        rec["watch"] = watch

    monkeypatch.setattr(AlgoFeed, "run", fake)
    hlt_algo_feed.run(lambda ev: None, watch=["SPY"])
    assert rec["watch"] == ["SPY"]


@pytest.mark.asyncio
async def test_sync_facade_rejects_running_loop():
    with pytest.raises(RuntimeError):
        hlt_algo_feed.notify_when(when=lambda ev: True, then=lambda ev: None)
