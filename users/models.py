from django.contrib.auth.models import AbstractUser
from django.db import models

PLAN_CHOICES = [('FREE','Free'),('BASIC','Basic $30'),('PRO','Pro $40'),('ELITE','Elite $50')]

class MMDEUser(AbstractUser):
    email = models.EmailField(unique=True)
    google_id = models.CharField(max_length=255, blank=True)
    subscription_plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default='FREE')
    is_active_subscription = models.BooleanField(default=False)
    allowed_markets = models.JSONField(default=list)
    subscription_expires = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self): return f"{self.email} ({self.subscription_plan})"

    def can_access_market(self, market):
        if self.is_superuser: return True
        if not self.is_active_subscription: return False
        return market in self.allowed_markets

    def get_allowed_markets(self):
        from django.conf import settings
        plan = settings.SUBSCRIPTION_PLANS.get(self.subscription_plan, {})
        return plan.get('markets', [])

    def save(self, *args, **kwargs):
        from django.conf import settings
        self.allowed_markets = self.get_allowed_markets()
        super().save(*args, **kwargs)
