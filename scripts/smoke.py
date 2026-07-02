"""Live smoke: connect to a running HighLowTicker algo feed and print 5 frames.

Precondition: HighLowTicker running with Settings, Algo feed :7412 enabled.
Run: python scripts/smoke.py
"""
import asyncio

from hlt_algo_feed import AlgoFeed


async def main():
    async with AlgoFeed() as feed:
        await feed.subscribe_summary()
        n = 0
        async for ev in feed:
            print(ev.event, ev.symbol, ev.last_price)
            n += 1
            if n >= 5:
                break


if __name__ == "__main__":
    asyncio.run(main())
