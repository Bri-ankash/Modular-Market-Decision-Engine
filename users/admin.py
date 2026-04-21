from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import MMDEUser

@admin.register(MMDEUser)
class MMDEUserAdmin(UserAdmin):
    list_display = ['email', 'subscription_plan', 'is_active_subscription', 'market_access', 'subscription_expires', 'date_joined']
    list_filter = ['subscription_plan', 'is_active_subscription', 'is_staff']
    search_fields = ['email', 'username', 'first_name']
    ordering = ['-date_joined']
    list_editable = ['subscription_plan', 'is_active_subscription']

    fieldsets = (
        ('Login', {'fields': ('username', 'email', 'password')}),
        ('Personal', {'fields': ('first_name', 'last_name', 'google_id')}),
        ('Subscription', {'fields': ('subscription_plan', 'is_active_subscription', 'allowed_markets', 'subscription_expires')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {'fields': ('username', 'email', 'password1', 'password2', 'subscription_plan', 'is_active_subscription')}),
    )

    def market_access(self, obj):
        if not obj.allowed_markets:
            return '— None'
        return ', '.join(obj.allowed_markets)
    market_access.short_description = 'Markets'
