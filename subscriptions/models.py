from django.db import models

class SubscriptionPlan(models.Model):
    PLAN_KEYS = [
        ('FREE', 'Free'),
        ('BASIC', 'Basic — $30/mo'),
        ('PRO', 'Pro — $40/mo'),
        ('ELITE', 'Elite — $50/mo'),
    ]
    key = models.CharField(max_length=10, choices=PLAN_KEYS, unique=True)
    display_name = models.CharField(max_length=50)
    price_usd = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    allowed_markets = models.JSONField(default=list, help_text='e.g. ["forex","gold","indices","crypto","stocks"]')
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.display_name} — Markets: {', '.join(self.allowed_markets) or 'None'}"

    class Meta:
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'
        ordering = ['price_usd']
