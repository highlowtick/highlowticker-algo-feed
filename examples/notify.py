"""Notifier built on hlt_algo_feed — sync facade, channel-neutral.

Alerts the first time a symbol makes its Nth new high. Delivery is one swappable
send() function; Discord and Telegram shown. No async code visible.

Run:  DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..." python notify.py
"""
import json
import os
import ssl
import urllib.parse
import urllib.request

from hlt_algo_feed import notify_when

MILESTONE = int(os.environ.get("HLT_MILESTONE", "5"))
try:
    import certifi
    _SSL = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL = ssl.create_default_context()


def send(text: str) -> None:
    """Deliver one alert. Swap this body for any channel."""
    # --- Discord / Slack / generic webhook (one POST) ---
    url = os.environ["DISCORD_WEBHOOK_URL"]
    data = json.dumps({"content": text}).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST",
        headers={"Content-Type": "application/json", "User-Agent": "HLT-Notifier/1.0"})
    with urllib.request.urlopen(req, context=_SSL, timeout=10) as r:
        r.read()

    # --- Telegram alternative (set TELEGRAM_TOKEN / TELEGRAM_CHAT, then use this
    #     instead of the block above) ---
    # tok, chat = os.environ["TELEGRAM_TOKEN"], os.environ["TELEGRAM_CHAT"]
    # q = urllib.parse.urlencode({"chat_id": chat, "text": text})
    # with urllib.request.urlopen(
    #         f"https://api.telegram.org/bot{tok}/sendMessage?{q}",
    #         context=_SSL, timeout=10) as r:
    #     r.read()


if __name__ == "__main__":
    notify_when(
        when=lambda ev: ev.event == "new_high" and (ev.high_count or 0) >= MILESTONE,
        then=lambda ev: send(f"🔼 {ev.symbol} · {ev.high_count} new highs"),
        once=lambda ev: (ev.symbol, "high"),
    )
