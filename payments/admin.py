from django.contrib import admin
from django.utils.html import format_html
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user_email', 'plan', 'amount', 'currency', 'mpesa_code', 'status', 'created_at', 'approve_btn']
    list_filter = ['status', 'plan']
    search_fields = ['user__email', 'mpesa_code', 'reference']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'reference']
    actions = ['approve_selected']

    def user_email(self, obj): return obj.user.email
    user_email.short_description = 'User'

    def approve_btn(self, obj):
        if obj.status == 'PENDING':
            return format_html(
                '<a href="/admin/payments/payment/{}/approve/" style="background:#16A34A;color:#fff;padding:4px 12px;border-radius:6px;text-decoration:none;font-size:11px;font-weight:700">✓ Approve</a>',
                obj.id
            )
        return format_html('<span style="color:#16A34A;font-weight:700">{}</span>', obj.status)
    approve_btn.short_description = 'Action'

    def approve_selected(self, request, queryset):
        for payment in queryset.filter(status='PENDING'):
            payment.approve(admin_user=request.user)
        self.message_user(request, f'{queryset.count()} payment(s) approved.')
    approve_selected.short_description = 'Approve selected payments'
