from django.db import models
from django.conf import settings
from django.core.validators import MinLengthValidator

class Currency(models.Model):
    """
    Represents a currency code and its full name.
    """
    code = models.TextField(max_length=3)
    name = models.TextField(max_length=30)


class ExchangeRateHistory(models.Model):
    """
    Tracks the historical exchange rates between two currencies on specific dates.
    """
    from_currency = models.CharField(max_length=3, db_index=True)
    to_currency = models.CharField(max_length=3, db_index=True)
    rate = models.DecimalField(max_digits=18, decimal_places=6)
    date = models.DateField(auto_now_add=True, db_index=True) # Храним курс на конкретный день

    class Meta:
        get_latest_by = 'date'

class Account(models.Model):
    """
    Represents a user's financial account (e.g., Main Card, Savings).
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.TextField(max_length=30, validators=[MinLengthValidator(3)], null=False, blank=False)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)



class Category(models.Model):
    """
    Represents a transaction category which can be either an income or expense type.
    Categories can be user-specific or global (user=None).
    """
    class Type(models.TextChoices):
        INCOME = 'INCOME', 'Income'
        EXPENSE = 'EXPENSE', 'Expense'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    name = models.TextField(max_length=30)
    type = models.CharField(max_length=10, choices=Type.choices)
    is_essential = models.BooleanField()

class Transaction(models.Model):
    """
    Represents a single financial transaction (income or expense) made by a user.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount_original = models.DecimalField(max_digits=18, decimal_places=2)
    amount_base = models.DecimalField(max_digits=18, decimal_places=2)
    description = models.TextField(max_length=255, null=True, blank=True)
    raw_text = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

class Subscriptions(models.Model):
    """
    Represents a recurring subscription (monthly or yearly) for a user.
    """
    class Cycle(models.TextChoices):
        MONTHLY = 'MONTHLY', 'Monthly'
        YEARLY = 'YEARLY', 'Yearly'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.TextField(max_length=50)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    next_billing_date = models.DateField()
    billing_cycle = models.CharField(max_length=10, choices=Cycle.choices)
    is_active = models.BooleanField(default=True)

class FinancialGoal(models.Model):
    """
    Represents a financial goal set by a user, tracking the target amount and the current amount saved.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.TextField(max_length=50)
    target_amount = models.DecimalField(max_digits=18, decimal_places=2)
    target_currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    current_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    target_date = models.DateField()
