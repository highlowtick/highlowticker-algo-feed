from hlt_algo_feed.feed import build_watch, build_summary


def test_build_watch_uppercases():
    msg = build_watch(["aapl", "Msft"])
    assert msg["type"] == "SUBSCRIBE_WATCH"
    assert msg["symbols"] == ["AAPL", "MSFT"]


def test_build_watch_empty_list():
    assert build_watch([]) == {"type": "SUBSCRIBE_WATCH", "symbols": []}


def test_build_summary_toggle():
    assert build_summary(True) == {"type": "SUBSCRIBE_SUMMARY", "enabled": True}
    assert build_summary(False) == {"type": "SUBSCRIBE_SUMMARY", "enabled": False}
