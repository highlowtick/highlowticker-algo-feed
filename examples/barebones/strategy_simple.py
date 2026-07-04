"""Minimal HighLowTicker strategy — bare-bones, no dependencies, read-only.

"Classify the stream": watch a symbol via SUBSCRIBE_WATCH, keep a tiny in-memory
paper account, print enter/exit. No pip package required. Emits nothing back to
the app (the old ALGO_SIGNAL/ALGO_ORDER report frames were removed in v1.0.2).

Run:  python strategy_simple.py
Env:  HLT_ALGO_WS (default ws://127.0.0.1:7412), HLT_SYMBOL (default SPY),
      HLT_MILESTONE (default 5).
"""
import asyncio
import json
import os

import websockets

WS_URL = os.environ.get("HLT_ALGO_WS", "ws://127.0.0.1:7412").strip()
SYMBOL = os.environ.get("HLT_SYMBOL", "SPY").strip().upper()
MILESTONE = int(os.environ.get("HLT_MILESTONE", "5"))


async def main() -> None:
    position, entry_price, realized = 0, 0.0, 0.0
    print(f"[strategy] {SYMBOL}: long on new high #{MILESTONE}, exit on a new low", flush=True)
    async with websockets.connect(WS_URL, ping_interval=20, ping_timeout=120) as ws:
        await ws.send(json.dumps({"type": "SUBSCRIBE_WATCH", "symbols": [SYMBOL]}))
        async for raw in ws:
            ev = json.loads(raw)
            if ev.get("type") != "TAPE_EVENT" or ev.get("symbol") != SYMBOL:
                continue
            event, last_price = ev.get("event", ""), ev.get("last_price")
            if position == 0 and "high" in event and (ev.get("high_count") or 0) >= MILESTONE \
                    and last_price is not None:
                position, entry_price = 1, last_price
                print(f"[strategy] ENTER long {SYMBOL} @ {entry_price:.2f}", flush=True)
            elif position == 1 and "low" in event and last_price is not None:
                realized += last_price - entry_price
                print(f"[strategy] EXIT  {SYMBOL} @ {last_price:.2f}  realized {realized:+.2f}", flush=True)
                position, entry_price = 0, 0.0
            elif position == 1 and event == "price_update" and last_price is not None:
                print(f"[strategy] hold {SYMBOL} entry {entry_price:.2f} last {last_price:.2f} "
                      f"unrealized {last_price - entry_price:+.2f}", flush=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[strategy] stopped", flush=True)
