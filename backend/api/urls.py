from django.urls import path
from .views import BotListCreateAPIView, TradeAPIView

urlpatterns = [
    path('bots/', BotListCreateAPIView.as_view(), name='bots-list-create'),
    path('trade/', TradeAPIView.as_view(), name='trade'),
]
