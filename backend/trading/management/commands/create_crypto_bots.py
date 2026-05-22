from django.core.management.base import BaseCommand

from trading.models import TradingBot


BOTS = [
    "BTC-USD",
    "ETH-USD",
    "SOL-USD",
    "BNB-USD",
    "XRP-USD",
    "DOGE-USD",
    "ADA-USD",
]


class Command(BaseCommand):
    help = "Create crypto trading bots"

    def handle(self, *args, **options):

        for symbol in BOTS:
            bot, created = TradingBot.objects.update_or_create(
                symbol=symbol,
                defaults={
                    "name": f"Bot - {symbol}",
                    "balance": 1000,
                    "risk_per_trade": 0.005,
                    "reward_ratio": 3,
                    "is_active": True,
                    "auto_close_profit_amount": 5,
                   "auto_close_loss_amount": 3,
                },
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created {bot.name}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Updated {bot.name}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "All crypto bots are ready."
            )
        )