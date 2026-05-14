from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

PLAN_CHOICES = [
    ('FREE', 'Free'),
    ('BASIC', 'Basic $30'),
    ('PRO', 'Pro $40'),
    ('ELITE', 'Elite $50'),
]


# 🔥 FIX: Required for createsuperuser to work with email login
class MMDEUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)


class MMDEUser(AbstractUser):
    email = models.EmailField(unique=True)
    google_id = models.CharField(max_length=255, blank=True, null=True)
    subscription_plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='FREE')
    is_active_subscription = models.BooleanField(default=False)
    allowed_markets = models.JSONField(default=list)
    subscription_expires = models.DateTimeField(null=True, blank=True)
    webhook_secret = models.CharField(max_length=50, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # IMPORTANT: email login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # 🔥 FIX: attach custom manager
    objects = MMDEUserManager()

    def __str__(self):
        return f"{self.email} ({self.subscription_plan})"


    def has_active_subscription(self):
        if self.is_superuser:
            return True
        if not self.is_active_subscription:
            return False
        if self.subscription_expires is not None:
            from django.utils import timezone
            return self.subscription_expires > timezone.now()
        return True


    def can_access_market(self, market):
        market = (market or "").lower().strip()
        if self.is_superuser:
            return True
        if not self.has_active_subscription():
            return False
        return market in [m.lower() for m in (self.allowed_markets or [])]


    def get_allowed_markets(self):
        from django.conf import settings

        plans = getattr(settings, "SUBSCRIPTION_PLANS", {})
        plan = plans.get(self.subscription_plan, {})
        markets = plan.get("markets", [])
        return [m.lower() for m in markets]


    def save(self, *args, **kwargs):
        if not self.webhook_secret:
            import uuid
            self.webhook_secret = uuid.uuid4().hex[:16].upper()
        self.allowed_markets = self.get_allowed_markets()
        super().save(*args, **kwargs)

