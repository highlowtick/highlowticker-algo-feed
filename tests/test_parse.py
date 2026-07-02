from hlt_algo_feed.feed import parse_frame

_FULL = ('{"type":"TAPE_EVENT","ts":"t","symbol":"NVDA","event":"new_high",'
         '"session_high":1.0,"session_low":null,"last_price":1.0,"close_price":null,'
         '"volume":null,"pct_change":null,"high_count":1,"low_count":0,'
         '"is_week52_high":false,"is_week52_low":false,"volume_spike":false,'
         '"market_high_rate_30s":0,"market_high_rate_1m":0,"market_low_rate_30s":0,'
         '"market_low_rate_1m":0,"market_high_rate_5m":0,"market_low_rate_5m":0,'
         '"market_high_rate_20m":0,"market_low_rate_20m":0%s}')


def test_parse_tape_event():
    ev = parse_frame(_FULL % "")
    assert ev.event == "new_high"
    assert ev.symbol == "NVDA"
    assert ev.high_count == 1


def test_parse_ignores_unknown_fields():
    # A newer binary may add fields; an older client must keep working (version skew).
    ev = parse_frame(_FULL % ',"future_field_from_newer_binary":42')
    assert ev.high_count == 1


def test_parse_non_tape_returns_none():
    assert parse_frame('{"type":"SOMETHING_ELSE"}') is None
