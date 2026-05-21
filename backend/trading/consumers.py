import asyncio

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import Trade
from .serializers import TradeSerializer
from .services import update_open_trades_live_pnl


class TradeLiveConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        await self.accept()
        self.keep_running = True
        self.live_task = asyncio.create_task(
            self.send_live_updates()
        )

    async def disconnect(self, close_code):
        self.keep_running = False

        if hasattr(self, "live_task"):
            self.live_task.cancel()

    async def send_live_updates(self):
        while self.keep_running:
            try:
                await sync_to_async(update_open_trades_live_pnl)()

                all_trades = await sync_to_async(
                    lambda: list(
                        Trade.objects.all().order_by("-created_at")
                    )
                )()

                data = await sync_to_async(
                    lambda: TradeSerializer(
                        all_trades,
                        many=True
                    ).data
                )()

                await self.send_json({
                    "type": "live_trades",
                    "trades": data,
                })

            except Exception as error:
                await self.send_json({
                    "type": "error",
                    "message": str(error),
                })

                print("WebSocket live update error:", error)

            await asyncio.sleep(1)