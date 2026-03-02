from rest_framework import serializers
from finance.models import Transaction, Category, Account, Currency, FinancialGoal

class VoiceTransactionSerializer(serializers.Serializer):
    """Serializer for validating voice transaction input requests."""
    audio_file = serializers.FileField()
    account_id = serializers.IntegerField()
    chat_id = serializers.IntegerField(required=False, allow_null=True)


class TextTransactionSerializer(serializers.Serializer):
    """Serializer for validating text transaction input requests."""
    text = serializers.CharField()
    account_id = serializers.IntegerField()
    chat_id = serializers.IntegerField(required=False, allow_null=True)


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for the Category model."""
    class Meta:
        model = Category
        fields = ["id", "name", "type", "is_essential"]


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for the Transaction model, providing detailed category data on read, and accepting an ID on write."""
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    amount = serializers.DecimalField(
        max_digits=18, decimal_places=2, source='amount_original'
    )

    class Meta:
        model = Transaction
        fields = [
            "id",
            "account",
            "category",
            "category_id",
            "amount",
            "amount_original",
            "amount_base",
            "description",
            "raw_text",
            "date",
        ]
        read_only_fields = ["amount_original", "amount_base", "date"]


class AccountSerializer(serializers.ModelSerializer):
    """Serializer for the Account model."""
    class Meta:
        model = Account
        fields = ["id", "name", "currency", "balance"]


class CurrencySerializer(serializers.ModelSerializer):
    """Serializer for the Currency model."""
    class Meta:
        model = Currency
        fields = ["id", "code", "name"]


class FinancialGoalSerializer(serializers.ModelSerializer):
    """Serializer for the FinancialGoal model."""
    class Meta:
        model = FinancialGoal
        fields = [
            "id",
            "name",
            "target_amount",
            "target_currency",
            "current_amount",
            "target_date",
        ]