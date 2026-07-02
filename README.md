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

- HighLowTicker running with the algo feed enabled (Settings, Algo feed :7412).
- Python 3.9 or newer.

## Usage

```python
import asyncio
from hlt_algo_feed import AlgoFeed

async def main():
    async with AlgoFeed() as feed:
        await feed.watch(["AAPL", "MSFT"])   # get price_update ticks for these
        await feed.subscribe_summary()       # get the periodic market_summary
        async for ev in feed:
            if ev.event == "new_high":
                print(ev.symbol, ev.last_price)

asyncio.run(main())
```

Every `ev` is a typed `TapeEvent` (a pydantic model). Unknown fields from a
newer app build are ignored, so an older client keeps working against a newer
binary.

## Note on the schema

`schema/algo-feed.schema.json` is a vendored copy of the wire-protocol schema
generated from the app's Rust types. The pydantic models in
`src/hlt_algo_feed/models.py` are generated from that file. When the protocol
changes, refresh both: copy the new schema in, then regenerate the models with
`datamodel-code-generator` (see `tests/test_models_drift.py` for the exact
command). The drift test fails if the committed models do not match the schema.
