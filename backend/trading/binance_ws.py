import asyncio
import json
import websockets

from django.core.cache import cache


SYMBOLS = [
    "btcusdt",
    "ethusdt",
    "solusdt",
    "bnbusdt",
]


async def stream_symbol(symbol):
    url = f"wss://stream.binance.com:9443/ws/{symbol}@trade"

    async with websockets.connect(url) as websocket:
        print(f"Connected to {symbol}")

        while True:
            message = await websocket.recv()
            data = json.loads(message)

            price = float(data["p"])
            key = f"price:{symbol.upper()}"

            cache.set(key, price, timeout=120)

            print(f"{key} = {price}")


async def stream_all_prices():
    tasks = [stream_symbol(symbol) for symbol in SYMBOLS]
    await asyncio.gather(*tasks)


def get_latest_price(symbol):
    key = f"price:{symbol.upper()}"
    return cache.get(key)