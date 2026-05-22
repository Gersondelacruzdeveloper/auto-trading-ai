from django.db import models


class TradingBot(models.Model):
    name = models.CharField(max_length=100)

    symbol = models.CharField(
        max_length=20,
        default="BTC-USD"
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=1000
    )
    profit_pot = models.DecimalField(
    max_digits=14,
    decimal_places=2,
    default=0
    )
    auto_close_profit_amount = models.FloatField(
    default=100
     )

    risk_per_trade = models.FloatField(default=0.005)

    reward_ratio = models.FloatField(default=3)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    auto_close_loss_amount = models.FloatField(
    default=500
)

    def __str__(self):
        return self.name

class Trade(models.Model):
    SIGNALS = (
        ("BUY", "BUY"),
        ("SELL", "SELL"),
        ("HOLD", "HOLD"),
    )

    bot = models.ForeignKey(
        TradingBot,
        on_delete=models.CASCADE,
        related_name="trades"
    )

    symbol = models.CharField(max_length=20)
    signal = models.CharField(max_length=10, choices=SIGNALS)

    entry_price = models.FloatField()
    current_price = models.FloatField(default=0)

    stop_loss = models.FloatField()
    take_profit = models.FloatField()

    position_size = models.FloatField(default=0)
    risk_amount = models.FloatField(default=0)

    pnl = models.FloatField(default=0)
    pnl_percent = models.FloatField(default=0)

    is_open = models.BooleanField(default=True)
    closed_reason = models.CharField(max_length=50, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(blank=True, null=True)
    

    def __str__(self):
        return f"{self.symbol} {self.signal}"
    
class BacktestResult(models.Model):
    symbol = models.CharField(max_length=50)

    timeframe = models.CharField(max_length=20)

    total_trades = models.IntegerField(default=0)

    wins = models.IntegerField(default=0)

    losses = models.IntegerField(default=0)

    win_rate = models.FloatField(default=0)

    total_pnl = models.FloatField(default=0)

    max_drawdown = models.FloatField(default=0)

    profit_factor = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.symbol} - {self.timeframe}"