from django.db import models

class AnalysisRequest(models.Model):
    user = models.ForeignKey('users.MMDEUser', on_delete=models.CASCADE)
    market = models.CharField(max_length=20)
    symbol = models.CharField(max_length=20)
    selected_modules = models.JSONField(default=list)
    result = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    duration_ms = models.IntegerField(default=0)

    def __str__(self): return f"{self.user.email} — {self.symbol} — {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-created_at']


class TradingViewFeed(models.Model):
    """Stores the latest candles sent from TradingView webhook"""
    user_secret = models.CharField(max_length=100, default='default')
    symbol      = models.CharField(max_length=20)
    interval    = models.CharField(max_length=10)
    market      = models.CharField(max_length=20, default='forex')
    candles_json= models.TextField()  # raw JSON list
    received_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-received_at']

    def __str__(self):
        return f"{self.symbol} {self.interval} — {self.received_at.strftime('%H:%M:%S')}"
