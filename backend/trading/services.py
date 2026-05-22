import yfinance as yf

from django.utils import timezone

from .models import TradingBot, Trade
from .strategy import RiskManagedStrategy
from .market_data import get_live_price


def run_bot(bot_id):
    bot = TradingBot.objects.get(id=bot_id)

    existing_trade = Trade.objects.filter(
        bot=bot,
        symbol=bot.symbol,
        is_open=True,
    ).first()

    if existing_trade:
        return None

    strategy = RiskManagedStrategy(
        balance=bot.balance,
        risk_per_trade=bot.risk_per_trade,
        reward_ratio=bot.reward_ratio,
    )

    df_15m = yf.download(
        bot.symbol,
        period="30d",
        interval="15m",
        progress=False,
    )

    df_1h = yf.download(
        bot.symbol,
        period="90d",
        interval="1h",
        progress=False,
    )

    df_4h = yf.download(
        bot.symbol,
        period="180d",
        interval="4h",
        progress=False,
    )

    if df_15m.empty or df_1h.empty or df_4h.empty:
        return None

    signal_15m = strategy.get_signal_from_df(df_15m)
    signal_1h = strategy.get_signal_from_df(df_1h)
    signal_4h = strategy.get_signal_from_df(df_4h)

    signals = [
        signal_15m,
        signal_1h,
        signal_4h,
    ]

    print(
        bot.symbol,
        {
            "15m": signal_15m,
            "1h": signal_1h,
            "4h": signal_4h,
        }
    )

    if signals.count("BUY") == 2:
        final_signal = "BUY"
    elif signals.count("SELL") == 2:
        final_signal = "SELL"
    else:
        return None

    trade_data = strategy.create_trade(
    df_15m,
    forced_signal=final_signal
)

    if not trade_data:
        return None


    live_entry = get_live_price(bot.symbol)

    if live_entry is not None:
        trade_data["entry_price"] = live_entry

    trade = Trade.objects.create(
        bot=bot,
        symbol=bot.symbol,
        signal=trade_data["signal"],
        entry_price=trade_data["entry_price"],
        current_price=trade_data["entry_price"],
        stop_loss=trade_data["stop_loss"],
        take_profit=trade_data["take_profit"],
        position_size=trade_data["position_size"],
        risk_amount=trade_data["risk_amount"],
        pnl=0,
        pnl_percent=0,
        is_open=True,
    )

    return trade

def update_open_trades_live_pnl():
    open_trades = Trade.objects.filter(
        is_open=True
    )

    updated_trades = []

    for open_trade in open_trades:
        current_price = get_live_price(
            open_trade.symbol
        )

        if current_price is None:
            continue

        open_trade.current_price = current_price

        if open_trade.signal == "BUY":
            open_trade.pnl = (
                current_price - open_trade.entry_price
            ) * open_trade.position_size

            open_trade.pnl_percent = (
                (current_price - open_trade.entry_price)
                / open_trade.entry_price
            ) * 100

        elif open_trade.signal == "SELL":
            open_trade.pnl = (
                open_trade.entry_price - current_price
            ) * open_trade.position_size

            open_trade.pnl_percent = (
                (open_trade.entry_price - current_price)
                / open_trade.entry_price
            ) * 100

        bot = open_trade.bot

        if open_trade.pnl >= bot.auto_close_profit_amount:
            open_trade.is_open = False
            open_trade.closed_reason = "PROFIT_LOCKED"
            open_trade.closed_at = timezone.now()

            bot.profit_pot = float(bot.profit_pot) + open_trade.pnl
            bot.save()

        elif open_trade.pnl <= -bot.auto_close_loss_amount:
            open_trade.is_open = False
            open_trade.closed_reason = "MAX_LOSS_STOP"
            open_trade.closed_at = timezone.now()

        elif open_trade.signal == "BUY" and current_price <= open_trade.stop_loss:
            open_trade.is_open = False
            open_trade.closed_reason = "STOP_LOSS"
            open_trade.closed_at = timezone.now()

        elif open_trade.signal == "BUY" and current_price >= open_trade.take_profit:
            open_trade.is_open = False
            open_trade.closed_reason = "TAKE_PROFIT"
            open_trade.closed_at = timezone.now()

        elif open_trade.signal == "SELL" and current_price >= open_trade.stop_loss:
            open_trade.is_open = False
            open_trade.closed_reason = "STOP_LOSS"
            open_trade.closed_at = timezone.now()

        elif open_trade.signal == "SELL" and current_price <= open_trade.take_profit:
            open_trade.is_open = False
            open_trade.closed_reason = "TAKE_PROFIT"
            open_trade.closed_at = timezone.now()

        open_trade.save()
        updated_trades.append(open_trade)

    return updated_trades