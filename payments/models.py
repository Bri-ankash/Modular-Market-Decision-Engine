from django.db import models

class Payment(models.Model):
    STATUS = [('PENDING','Pending'),('APPROVED','Approved'),('REJECTED','Rejected')]
    PLAN_CHOICES = [('BASIC','Basic $30'),('PRO','Pro $40'),('ELITE','Elite $50')]
    user = models.ForeignKey('users.MMDEUser', on_delete=models.CASCADE, related_name='payments')
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES)
    amount = models.FloatField()
    currency = models.CharField(max_length=5, default='USD')
    reference = models.CharField(max_length=100, unique=True)
    mpesa_code = models.CharField(max_length=30, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='PENDING')
    approved_by = models.ForeignKey('users.MMDEUser', null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_payments')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def approve(self, admin_user=None):
        from django.conf import settings
        from django.utils import timezone
        from datetime import timedelta
        self.status = 'APPROVED'
        self.approved_by = admin_user
        self.save()
        # Activate subscription
        u = self.user
        u.subscription_plan = self.plan
        u.is_active_subscription = True
        u.subscription_expires = timezone.now() + timedelta(days=30)
        u.save()

    def __str__(self): return f"{self.user.email} — {self.plan} — {self.status}"
