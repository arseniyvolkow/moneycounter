from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserRegistrationSerializer, UserProfileSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationAPIView(generics.CreateAPIView):
    """
    API endpoint for handling user registration.
    Accessible to any unauthenticated user.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for viewing and updating the authenticated user's profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        """Retrieves the profile of the currently logged-in user."""
        return self.request.user

def register_webapp_view(request):
    """Serves the Telegram Mini App Registration HTML Page."""
    return render(request, 'user_auth/register.html')

def login_webapp_view(request):
    """Serves the Telegram Mini App Login HTML Page."""
    return render(request, 'user_auth/login.html')
