import yfinance as yf

from .binance_ws import get_latest_price


BINANCE_SYMBOLS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
    "BNB-USD": "BNBUSDT",
    "XRP-USD": "XRPUSDT",
    "DOGE-USD": "DOGEUSDT",
    "ADA-USD": "ADAUSDT",
}


def convert_to_binance_symbol(symbol):
    return BINANCE_SYMBOLS.get(
        symbol,
        symbol.replace("-", "").upper()
    )


def get_live_price(symbol):
    binance_symbol = convert_to_binance_symbol(symbol)

    websocket_price = get_latest_price(
        binance_symbol
    )

    if websocket_price:
        return float(websocket_price)

    try:
        ticker = yf.Ticker(symbol)

        data = ticker.history(
            period="1d",
            interval="1m",
        )

        if not data.empty:
            return float(
                data["Close"].iloc[-1]
            )

    except Exception as error:
        print(
            f"Yahoo fallback failed for {symbol}: {error}"
        )

    return None