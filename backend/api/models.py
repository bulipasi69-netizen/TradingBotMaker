from django.db import models

class Bot(models.Model):
    TRADE_CHOICES = [
        ('live', 'Live'),
        ('backtesting', 'Backtesting'),
    ]

    bot_name        = models.CharField(max_length=100)
    description     = models.TextField(blank=True, null=True)
    trade_type      = models.CharField(max_length=12, choices=TRADE_CHOICES, default='live')
    initial_budget  = models.DecimalField(max_digits=12, decimal_places=2)
    buy_threshold   = models.IntegerField(default=80)
    sell_threshold  = models.IntegerField(default=50)
    order_value     = models.DecimalField(max_digits=12, decimal_places=2, default=100)
    price_interval  = models.IntegerField(default=10)   # seconds
    trade_interval  = models.IntegerField(default=30)   # seconds

    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.bot_name
