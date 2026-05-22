import time

from django.core.management.base import BaseCommand
from trading.tasks import run_all_active_bots


class Command(BaseCommand):
    help = "Automatically scan all bots and open trades when rules are met"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("Auto trading started...")
        )

        while True:
            results = run_all_active_bots()

            if results:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Trades opened: {results}"
                    )
                )
            else:
                self.stdout.write(
                    "No valid trade signals right now."
                )

            time.sleep(60)