from django.db import models
from django.utils import timezone
import jsonfield  # Optional: if you want to store custom JSON. Alternatively, use models.JSONField (Django 3.1+)

class Bot(models.Model):
    bot_name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True, null=True)
    trade_type = models.CharField(max_length=10)  # 'live' or 'backtesting'
    # Use JSONField for customizations (available in Django 3.1+)
    customizations = models.JSONField(blank=True, null=True)
    infinite_event_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.bot_name
