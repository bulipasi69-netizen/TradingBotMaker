from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .models import Bot
from .serializers import BotSerializer
from utils import infinite_games

import socket
import subprocess
import threading
import os
import sys
import logging
import time
import psutil  # You might need to install this: pip install psutil


# ────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────
def is_port_in_use(port, host="0.0.0.0"):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((host, port))
        sock.close()
        return False
    except OSError:
        return True


def run_trading_bot_script():
    """
    Spawn the Dash trading bot dashboard on port 8050.
    """
    try:
        trading_dir = os.path.join(settings.BASE_DIR, "trading")
        subprocess.Popen(
            [sys.executable, "trading_bot_with_plot.py"],  # <-- FIXED filename
            cwd=trading_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        return True
    except Exception as e:
        print(f"Exception while starting trading bot: {e}")
        return False


# ────────────────────────────────────────────────────────────────
# API views
# ────────────────────────────────────────────────────────────────
@api_view(["POST"])
def run_trading_bot(request):
    if not request.method == "POST":
        return Response(
            {"error": "Method not allowed"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    if is_port_in_use(8050):
        return Response(
            {
                "message": "Trading bot dashboard is already running on port 8050",
                "dash_url": "http://localhost:8050",
                "status": "already_running",
            },
            status=status.HTTP_200_OK,
        )

    success = run_trading_bot_script()
    if success:
        return Response(
            {
                "message": "Trading bot deployment initiated. Dashboard will be available shortly.",
                "dash_url": "http://localhost:8050",
                "status": "success",
            },
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            {
                "message": "Failed to start trading bot. Check server logs for details.",
                "dash_url": "http://localhost:8050",
                "status": "failed",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@csrf_exempt
@api_view(["GET", "POST"])
def bot_list_create(request):
    if request.method == "POST":
        # Process the incoming data and create a bot...
        return Response(
            {"message": "Bot created successfully."},
            status=status.HTTP_201_CREATED,
        )
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
                "description": serializer.validated_data.get("description")
                or "Event created for live trading bot.",
                "cutoff": "2050-01-01T00:00:00Z",  # A future date
            }
            infinite_event_response = infinite_games.create_event(event_payload)
            infinite_event_id = infinite_event_response.get(
                "event_id", "ifgames-dummy-event-id"
            )
            serializer.save(infinite_event_id=infinite_event_id)

        elif trade_type == "backtesting":
            # For backtesting bots, simulate an event using historical data.
            event_payload = {
                "title": serializer.validated_data.get("bot_name") + " (Backtest)",
                "description": serializer.validated_data.get("description")
                or "Event created for backtesting using historical data.",
                "cutoff": "2020-01-01T00:00:00Z",  # A past date for backtesting
            }
            infinite_event_response = infinite_games.create_event_for_backtesting(
                event_payload
            )
            infinite_event_id = infinite_event_response.get(
                "event_id", "backtest-dummy-event-id"
            )
            serializer.save(infinite_event_id=infinite_event_id)

        else:
            # If no recognized trade_type is provided, just save with a default ID.
            serializer.save(infinite_event_id="unknown")


# Dummy view for simulating trade execution via Coinbase
class TradeAPIView(APIView):
    def post(self, request, format=None):
        from utils import coinbase

        trade_response = coinbase.place_trade(request.data)
        return Response(trade_response, status=status.HTTP_200_OK)
