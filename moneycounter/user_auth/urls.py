from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegistrationAPIView, UserProfileView, register_webapp_view, login_webapp_view

urlpatterns = [
    # JWT Authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User Profile & Registration endpoints
    path('register/', RegistrationAPIView.as_view(), name='register_api'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # Telegram Mini App endpoints
    path('webapp/register/', register_webapp_view, name='register_webapp'),
    path('webapp/login/', login_webapp_view, name='login_webapp'),
]
