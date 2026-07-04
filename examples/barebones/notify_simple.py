"""Discord/any-channel notifier — bare-bones, no dependencies, read-only.

Posts an alert the first time a symbol reaches its Nth new high/low. Uses raw
websockets; needs no pip package. Swap post_to_channel() for any service.

Run:  DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..." python notify_simple.py
Env:  HLT_ALGO_WS (default ws://127.0.0.1:7412), HLT_MILESTONE (default 5).
"""
import asyncio
import json
import os
import ssl
import urllib.request

import websockets

WS_URL = os.environ.get("HLT_ALGO_WS", "ws://127.0.0.1:7412").strip()
MILESTONE = int(os.environ.get("HLT_MILESTONE", "5"))
try:
    import certifi
    _SSL = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL = ssl.create_default_context()


def post_to_channel(text: str) -> None:
    url = os.environ["DISCORD_WEBHOOK_URL"]
    data = json.dumps({"content": text}).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST",
        headers={"Content-Type": "application/json", "User-Agent": "HLT-Notifier/1.0"})
    with urllib.request.urlopen(req, context=_SSL, timeout=10) as resp:
        resp.read()


async def main() -> None:
    alerted = set()
    print(f"[notify] connecting to {WS_URL} (alert on hit #{MILESTONE}) …", flush=True)
    async with websockets.connect(WS_URL, ping_interval=20, ping_timeout=120) as ws:
        async for raw in ws:
            ev = json.loads(raw)
            if ev.get("type") != "TAPE_EVENT":
                continue
            symbol, event = ev.get("symbol"), ev.get("event", "")
            for side, key in (("high", "high_count"), ("low", "low_count")):
                if side not in event:
                    continue
                count = ev.get(key)
                k = (symbol, side)
                if count is None or count < MILESTONE or k in alerted:
                    continue
                alerted.add(k)
                arrow = "🔼" if side == "high" else "🔽"
                price = ev.get("last_price")
                tail = f" @ ${price:,.2f}" if price is not None else ""
                post_to_channel(f"{arrow} {symbol} · {count} new {side}s{tail}")
                print(f"[notify] {symbol} {side} #{count} -> sent", flush=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[notify] stopped", flush=True)
