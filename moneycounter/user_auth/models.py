from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom User model extending Django's default AbstractUser.
    Includes a base currency preference.
    """
    base_currency = models.CharField(max_length=3, default="KZT")