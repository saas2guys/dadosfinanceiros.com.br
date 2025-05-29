from django.urls import re_path

from . import consumers

# WebSocket URL patterns
websocket_urlpatterns = [
    # Stock market WebSocket proxy endpoint - using high-performance consumer
    re_path(r"ws/stocks/$", consumers.HighPerformanceStockProxyConsumer.as_asgi()),
    # Alternative basic version without connection pooling:
    # re_path(r'ws/stocks/$', consumers.StockMarketProxyConsumer.as_asgi()),
    # Add more WebSocket endpoints here as needed:
    # re_path(r'ws/other-service/$', consumers.OtherServiceConsumer.as_asgi()),
]
