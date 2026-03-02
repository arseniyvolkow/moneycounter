from rest_framework import serializers
from django.contrib.auth import get_user_model
from finance.models import Account, Currency

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new User.
    Handles the creation of the user and initialization of their default account.
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'base_currency')

    def create(self, validated_data):
        """
        Creates a new user and provisions a default 'Main Card' account 
        using their base currency preference.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            base_currency=validated_data.get('base_currency', 'USD')
        )

        # Automatically create a default account
        currency_code = user.base_currency or 'USD'
        try:
            currency = Currency.objects.get(code=currency_code)
        except Currency.DoesNotExist:
            currency, _ = Currency.objects.get_or_create(code='USD', defaults={'name': 'US Dollar'})

        Account.objects.create(
            user=user,
            name="Main Card",
            currency=currency,
            balance=0
        )

        return user

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for retrieving and updating user profile details."""
    class Meta:
        model = User
        fields = ('id', 'username', 'base_currency')
        read_only_fields = ('id', 'username')
