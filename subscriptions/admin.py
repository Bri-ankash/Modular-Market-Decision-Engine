from django.contrib import admin
from .models import SubscriptionPlan

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['key', 'display_name', 'price_usd', 'market_list', 'is_active']
    list_editable = ['is_active']
    ordering = ['price_usd']

    def market_list(self, obj):
        return ', '.join(obj.allowed_markets) if obj.allowed_markets else '— No markets'
    market_list.short_description = 'Markets'
