from django.contrib import admin
from .models import TradingBot, Trade


@admin.register(TradingBot)
class TradingBotAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "symbol",
        "balance",
        "risk_per_trade",
        "is_active",
    )


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "symbol",
        "signal",
        "entry_price",
        "take_profit",
        "stop_loss",
        "pnl",
        "created_at",
    )