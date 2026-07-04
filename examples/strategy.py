"""Strategy built on hlt_algo_feed — sync facade, read-only classify.

The package owns connect/subscribe/loop/reconnect; this file is pure decision
logic + a tiny paper account. Prints only.

Run:  python strategy.py
Env:  HLT_SYMBOL (default SPY), HLT_MILESTONE (default 5).
"""
import os

from hlt_algo_feed import run

SYMBOL = os.environ.get("HLT_SYMBOL", "SPY").strip().upper()
MILESTONE = int(os.environ.get("HLT_MILESTONE", "5"))


class Momentum:
    """Long on the Nth new high, flat on a new low. Local paper account."""

    def __init__(self):
        self.pos, self.entry, self.realized = 0, 0.0, 0.0

    def __call__(self, ev):
        if ev.symbol != SYMBOL or ev.last_price is None:
            return
        if self.pos == 0 and "high" in ev.event and (ev.high_count or 0) >= MILESTONE:
            self.pos, self.entry = 1, ev.last_price
            print(f"ENTER {ev.symbol} @ {self.entry:.2f}", flush=True)
        elif self.pos == 1 and "low" in ev.event:
            self.realized += ev.last_price - self.entry
            print(f"EXIT  {ev.symbol} @ {ev.last_price:.2f}  realized {self.realized:+.2f}", flush=True)
            self.pos = 0


if __name__ == "__main__":
    run(Momentum(), watch=[SYMBOL])
