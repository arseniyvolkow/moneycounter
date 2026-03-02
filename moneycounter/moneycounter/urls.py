"""
URL configuration for moneycounter project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from finance import urls as finance_urls
from user_auth import urls as auth_urls


urlpatterns = [
    # Admin interface route
    path('admin/', admin.site.urls),
    # Core finance API routes
    path('api/', include(finance_urls)),
    # Authentication API routes
    path('api/auth/', include(auth_urls)),
]