from django.contrib import admin
from .models import (
    Currency, 
    ExchangeRateHistory, 
    Account, 
    Category, 
    Transaction, 
    Subscriptions, 
    FinancialGoal
)

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')

@admin.register(ExchangeRateHistory)
class ExchangeRateHistoryAdmin(admin.ModelAdmin):
    list_display = ('from_currency', 'to_currency', 'rate', 'date')
    list_filter = ('from_currency', 'to_currency', 'date')

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'currency', 'balance')
    list_filter = ('currency',)
    search_fields = ('name', 'user__username')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'user', 'is_essential')
    list_filter = ('type', 'is_essential')
    search_fields = ('name', 'user__username')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount_original', 'category', 'account', 'date')
    list_filter = ('date', 'category', 'account')
    search_fields = ('description', 'user__username')

@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'amount', 'next_billing_date', 'is_active')
    list_filter = ('billing_cycle', 'is_active')

@admin.register(FinancialGoal)
class FinancialGoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'target_amount', 'current_amount', 'target_date')