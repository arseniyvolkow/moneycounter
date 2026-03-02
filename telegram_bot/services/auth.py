from typing import Optional, Dict
from .base import BaseClient
from config import API_BASE_URL

class AuthService(BaseClient):
    """
    Service client for authentication-related API endpoints.
    """
    def __init__(self, base_url: str = API_BASE_URL):
        """Initializes the AuthService."""
        super().__init__(base_url)

    def login(self, username, password) -> Optional[Dict]:
        """
        Authenticates a user and retrieves access/refresh tokens.
        
        Args:
            username (str): The user's username.
            password (str): The user's password.
            
        Returns:
            Optional[Dict]: A dictionary containing {'access': '...', 'refresh': '...'} or None on failure.
        """
        response = self.post("/api/auth/token/", None, json={
            "username": username,
            "password": password
        })
        if isinstance(response, dict):
            return response
        return None

    def get_profile(self, token: str) -> Optional[Dict]:
        """
        Retrieves the authenticated user's profile.
        
        Args:
            token (str): The access token.
            
        Returns:
            Optional[Dict]: The user profile data.
        """
        return self.get("/api/auth/profile/", token)

    def update_profile(self, token: str, data: Dict) -> bool:
        """
        Updates the authenticated user's profile.
        
        Args:
            token (str): The access token.
            data (Dict): The profile data to update.
            
        Returns:
            bool: True if the update was successful, False otherwise.
        """
        return self.patch("/api/auth/profile/", token, json=data) is not None