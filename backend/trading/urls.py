from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    TradingBotViewSet,
    TradeViewSet,
    UpdateLivePnlAPIView,
)

router = DefaultRouter()

router.register("bots", TradingBotViewSet)
router.register("trades", TradeViewSet)

urlpatterns = [
    path(
        "trades/update-live-pnl/",
        UpdateLivePnlAPIView.as_view(),
        name="update-live-pnl",
    ),
] + router.urls