from .models import TradingBot
from .services import run_bot


def run_all_active_bots():
    bots = TradingBot.objects.filter(is_active=True)

    results = []

    for bot in bots:
        trade = run_bot(bot.id)

        if trade:
            results.append({
                "bot": bot.name,
                "symbol": trade.symbol,
                "signal": trade.signal,
            })

    return results