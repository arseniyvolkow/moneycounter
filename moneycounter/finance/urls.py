from django.urls import path, include
from rest_framework import routers

from finance.views import (
    CategoryViewSet,
    TransactionViewSet,
    AccountViewSet,
    CurrencyViewSet,
    FinancialGoalViewSet,
    VoiceTransactionView,
    TextTransactionView,
    AnalyticsView,
)

# API Router for standard viewsets
router = routers.DefaultRouter()

router.register(r"categories", CategoryViewSet)
router.register(r"transactions", TransactionViewSet)
router.register(r"accounts", AccountViewSet)
router.register(r"currencies", CurrencyViewSet)
router.register(r"financial-goals", FinancialGoalViewSet)

urlpatterns = [
    # Custom endpoints for ML processing and analytics
    path(
        "voice-to-transaction/",
        VoiceTransactionView.as_view(),
        name="voice-to-transaction",
    ),
    path(
        "text-to-transaction/",
        TextTransactionView.as_view(),
        name="text-to-transaction",
    ),
    path(
        "analytics/",
        AnalyticsView.as_view(),
        name="analytics",
    ),
    # Included router endpoints (e.g. /categories/, /transactions/)
    path("", include(router.urls)),
]