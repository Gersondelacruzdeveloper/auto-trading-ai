from django.urls import re_path
from .consumers import TradeLiveConsumer

websocket_urlpatterns = [
    re_path(
        r"ws/trades/$",
        TradeLiveConsumer.as_asgi(),
    ),
]