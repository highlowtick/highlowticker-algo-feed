from hlt_algo_feed.feed import build_watch, build_summary


def test_build_watch_uppercases_and_wraps():
    msg = build_watch(["aapl", "Msft"])
    assert msg["type"] == "ALGO_CUSTOM"
    assert msg["tag"] == "ALGO_WEB_WATCH"
    assert msg["data"]["symbols"] == ["AAPL", "MSFT"]
    assert "timestamp" in msg


def test_build_summary_toggle():
    assert build_summary(True)["data"]["enabled"] is True
    assert build_summary(False)["data"]["enabled"] is False
    assert build_summary(True)["tag"] == "ALGO_WEB_SUMMARY"
