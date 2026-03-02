from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'base_currency', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Fields', {'fields': ('base_currency',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Extra Fields', {'fields': ('base_currency',)}),
    )