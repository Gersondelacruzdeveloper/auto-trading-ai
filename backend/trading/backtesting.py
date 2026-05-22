import yfinance as yf

from .strategy import RiskManagedStrategy
from .models import BacktestResult


def run_backtest(
    symbol="BTC-USD",
    period="180d",
    interval="1h",
    balance=1000,
):
    df = yf.download(
        symbol,
        period=period,
        interval=interval,
        progress=False,
    )

    if df.empty:
        return None

    strategy = RiskManagedStrategy(
        balance=balance,
        risk_per_trade=0.005,
        reward_ratio=1.5
    )

    df = strategy.add_indicators(df)

    trades = []
    in_trade = False
    cooldown = 0

    for i in range(80, len(df) - 20):

        if cooldown > 0:
            cooldown -= 1
            continue

        if in_trade:
            continue

        history = df.iloc[:i]

        signal = strategy.get_signal_from_df(history)

        if signal == "HOLD":
            continue

        if not strategy.passes_quality_filter(history, signal):
            continue

        current = history.iloc[-1]

        entry = float(current["Close"])
        atr = float(current["atr"])

        if atr <= 0:
            continue

        if signal == "BUY":
            stop = entry - atr
            target = entry + (atr * 1.5)
        else:
            stop = entry + atr
            target = entry - (atr * 1.5)

        future = df.iloc[i:i + 20]

        pnl = 0
        in_trade = True

        for _, candle in future.iterrows():
            high = float(candle["High"])
            low = float(candle["Low"])

            if signal == "BUY":
                if low <= stop:
                    pnl = -1
                    break

                if high >= target:
                    pnl = 2
                    break

            else:
                if high >= stop:
                    pnl = -1
                    break

                if low <= target:
                    pnl = 2
                    break

        trades.append(pnl)

        in_trade = False
        cooldown = 5

    if not trades:
        return None

    wins = len([x for x in trades if x > 0])
    losses = len([x for x in trades if x < 0])
    total = sum(trades)

    win_rate = (wins / len(trades)) * 100

    gross_profit = sum([x for x in trades if x > 0])
    gross_loss = abs(sum([x for x in trades if x < 0]))

    profit_factor = (
        gross_profit / gross_loss
        if gross_loss > 0
        else 0
    )

    result = BacktestResult.objects.create(
        symbol=symbol,
        timeframe=interval,
        total_trades=len(trades),
        wins=wins,
        losses=losses,
        win_rate=win_rate,
        total_pnl=total,
        profit_factor=profit_factor,
    )

    return result