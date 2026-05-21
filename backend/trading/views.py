from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TradingBot, Trade
from .serializers import TradingBotSerializer, TradeSerializer
from .services import run_bot, update_open_trades_live_pnl


class TradingBotViewSet(viewsets.ModelViewSet):
    queryset = TradingBot.objects.all()
    serializer_class = TradingBotSerializer

    @action(detail=True, methods=["post"])
    def run(self, request, pk=None):
        trade = run_bot(pk)

        if not trade:
            return Response({
                "message": "No trade generated"
            })

        serializer = TradeSerializer(trade)
        return Response(serializer.data)


class TradeViewSet(viewsets.ModelViewSet):
    queryset = Trade.objects.all().order_by("-created_at")
    serializer_class = TradeSerializer


class UpdateLivePnlAPIView(APIView):
    def post(self, request):
        trades = update_open_trades_live_pnl()
        serializer = TradeSerializer(trades, many=True)
        return Response(serializer.data)