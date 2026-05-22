from django.core.management.base import BaseCommand

from trading.backtesting import run_backtest


class Command(BaseCommand):
    help = "Run trading strategy backtest"

    def handle(self, *args, **options):
        result = run_backtest()

        if result:
            self.stdout.write(
                self.style.SUCCESS(
                    f"""
Backtest Complete

Trades: {result.total_trades}
Wins: {result.wins}
Losses: {result.losses}
Win Rate: {result.win_rate:.2f}%
PnL: {result.total_pnl}
Profit Factor: {result.profit_factor:.2f}
                    """
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR("Backtest failed")
            )