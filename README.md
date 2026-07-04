# highlowticker-algo-feed

Typed async Python client for the HighLowTicker algo feed, the local WebSocket
at `ws://127.0.0.1:7412` that streams live new-high / new-low tape events from
HighLowTicker to your own program.

This is the ergonomic alternative to hand-writing the connect-and-parse
boilerplate. The frame models are generated from the published wire-protocol
JSON Schema, so they always match what the app emits.

## Install

```bash
pip install highlowticker-algo-feed
```

## Requirements

- [HighLowTicker](https://highlowtick.com) running with the algo feed enabled (Settings, Algo feed :7412).
- Python 3.9 or newer.

Wire-protocol reference and examples: <https://highlowtick.com/algo-feed.html>

## Usage

Three levels of control — pick your altitude.

### Quickstart (no async)

```python
from hlt_algo_feed import notify_when

# "notify WHEN a symbol makes its 5th new high, THEN send an alert"
notify_when(
    when=lambda ev: ev.event == "new_high" and (ev.high_count or 0) >= 5,
    then=lambda ev: print(f"🔼 {ev.symbol} · {ev.high_count} new highs"),
    once=lambda ev: (ev.symbol, "high"),
    watch=["AAPL", "MSFT"],
)
```

`then` is any function you supply — post to Discord, Slack, Telegram, a webhook,
email, or anything else. The package ships no messaging SDK and is channel-neutral.
For a long-running strategy, use `run(handler, watch=[...])` with a callable that
keeps its own state.

### Async driver (already inside an event loop)

```python
import asyncio
from hlt_algo_feed import AlgoFeed

async def main():
    await AlgoFeed().run(
        lambda ev: print(ev.symbol, ev.event),
        watch=["SPY"],
    )   # owns connect + loop + reconnect

asyncio.run(main())
```

### Raw / filtered iteration (full control)

```python
import asyncio
from hlt_algo_feed import AlgoFeed

async def main():
    async with AlgoFeed() as feed:
        await feed.watch(["AAPL"])
        async for ev in feed.new_highs():   # or: async for ev in feed
            print(ev.symbol, ev.high_count)

asyncio.run(main())
```

Every `ev` is a typed `TapeEvent` (a pydantic model). Unknown fields from a
newer app build are ignored, so an older client keeps working against a newer
binary. See `examples/` for complete notify + strategy scripts, each shown
bare-bones (no dependencies) and using this package.

## Note on the schema

`schema/algo-feed.schema.json` is a vendored copy of the wire-protocol schema
generated from the app's Rust types. The pydantic models in
`src/hlt_algo_feed/models.py` are generated from that file. When the protocol
changes, refresh both: copy the new schema in, then regenerate the models with
`datamodel-code-generator` (see `tests/test_models_drift.py` for the exact
command). The drift test fails if the committed models do not match the schema.
