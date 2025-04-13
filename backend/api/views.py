from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Bot
from .serializers import BotSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from utils import infinite_games

@csrf_exempt
@api_view(['GET', 'POST'])
def bot_list_create(request):
    if request.method == 'POST':
        # Process the incoming data and create a bot...
        return Response({"message": "Bot created successfully."}, status=status.HTTP_201_CREATED)
    else:
        # Return existing bots or a dummy response
        return Response({"bots": []}, status=status.HTTP_200_OK)


# List all bots or create a new bot
class BotListCreateAPIView(generics.ListCreateAPIView):
    queryset = Bot.objects.all()
    serializer_class = BotSerializer

    authentication_classes = []  # Add your authentication classes here

    def perform_create(self, serializer):
        trade_type = serializer.validated_data.get("trade_type", "live").lower()
        if trade_type == "live":
            # For live trading bots, create an event with a future cutoff.
            event_payload = {
                "title": serializer.validated_data.get("bot_name"),
                "description": serializer.validated_data.get("description") or "Event created for live trading bot.",
                "cutoff": "2050-01-01T00:00:00Z"  # A future date
            }
            infinite_event_response = infinite_games.create_event(event_payload)
            infinite_event_id = infinite_event_response.get("event_id", "ifgames-dummy-event-id")
            serializer.save(infinite_event_id=infinite_event_id)
        elif trade_type == "backtesting":
            # For backtesting bots, simulate an event using historical data.
            # The cutoff here represents a past date, indicating that the bot will use historical data.
            event_payload = {
                "title": serializer.validated_data.get("bot_name") + " (Backtest)",
                "description": serializer.validated_data.get("description") or "Event created for backtesting using historical data.",
                "cutoff": "2020-01-01T00:00:00Z"  # A past date for backtesting
            }
            # Here we call a different utility function for backtesting, if desired.
            # It can simulate historical event creation or perform another operation.
            infinite_event_response = infinite_games.create_event_for_backtesting(event_payload)
            infinite_event_id = infinite_event_response.get("event_id", "backtest-dummy-event-id")
            serializer.save(infinite_event_id=infinite_event_id)
        else:
            # If no recognized trade_type is provided, just save with a default infinite_event_id.
            serializer.save(infinite_event_id="unknown")

# Dummy view for simulating trade execution via Coinbase
class TradeAPIView(APIView):
    def post(self, request, format=None):
        # You could call a function from utils.coinbase to simulate a trade.
        from utils import coinbase
        trade_response = coinbase.place_trade(request.data)
        return Response(trade_response, status=status.HTTP_200_OK)

