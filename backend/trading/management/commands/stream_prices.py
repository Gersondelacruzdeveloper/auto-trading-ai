import asyncio

from django.core.management.base import BaseCommand
from trading.binance_ws import stream_all_prices


class Command(BaseCommand):
    help = "Stream live prices from Binance WebSocket"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                "Starting Binance WebSocket multi-price stream..."
            )
        )

        asyncio.run(
            stream_all_prices()
        )