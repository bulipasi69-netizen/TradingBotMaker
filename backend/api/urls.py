from django.urls import path
from .views import BotListCreateAPIView, TradeAPIView, run_trading_bot

urlpatterns = [
    path('bots/', BotListCreateAPIView.as_view(), name='bots-list-create'),
    path('trade/', TradeAPIView.as_view(), name='trade'),
    path('run-trading-bot/', run_trading_bot, name='run_trading_bot'),  # Fixed URL
]