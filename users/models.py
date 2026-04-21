from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

PLAN_CHOICES = [('FREE', 'Free'), ('BASIC', 'Basic $30')]


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
    created_at = models.DateTimeField(auto_now_add=True)

    # IMPORTANT: email login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # 🔥 FIX: attach custom manager
    objects = MMDEUserManager()

    def __str__(self):
        return f"{self.email} ({self.subscription_plan})"

    def can_access_market(self, market):
        if self.is_superuser:
            return True
        if not self.is_active_subscription:
            return False
        return market in self.allowed_markets

    def get_allowed_markets(self):
        from django.conf import settings
        plan = settings.SUBSCRIPTION_PLANS.get(self.subscription_plan, {})
        return plan.get('markets', [])

    def save(self, *args, **kwargs):
        from django.conf import settings
        self.allowed_markets = self.get_allowed_markets()
        super().save(*args, **kwargs)
