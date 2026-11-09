from django.contrib import admin

from .models import Account, CashMovement, Trade


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "base_currency")


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ("executed_at", "account", "side", "ticker", "quantity", "price", "total", "realised_result")
    list_filter = ("account", "side", "ticker")
    search_fields = ("ticker", "name", "isin")
    date_hierarchy = "executed_at"


@admin.register(CashMovement)
class CashMovementAdmin(admin.ModelAdmin):
    list_display = ("executed_at", "account", "kind", "raw_action", "amount")
    list_filter = ("account", "kind")
