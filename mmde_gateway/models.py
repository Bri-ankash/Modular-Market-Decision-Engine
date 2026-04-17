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
