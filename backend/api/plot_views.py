import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Bot
from trading.plot_service import get_bot_plot_data

class BotPlotDataAPIView(APIView):
    def get(self, request, pk):
        try:
            bot = Bot.objects.get(pk=pk)
        except Bot.DoesNotExist:
            return Response({'detail':'Not found'}, status=status.HTTP_404_NOT_FOUND)

        data = get_bot_plot_data(
            token_id = bot.token_id,
            tm_key   = os.getenv('TOKEN_METRICS_API_KEY')
        )
        return Response(data)
