from rest_framework import serializers

from .models import (
    TradingBot,
    Trade,
)


class TradeSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = Trade
        fields = "__all__"


class TradingBotSerializer(
    serializers.ModelSerializer
):

    trades = TradeSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = TradingBot
        fields = "__all__"