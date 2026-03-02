from typing import Optional, Dict, Any, List
from .base import BaseClient
from config import API_BASE_URL

class CategoryService(BaseClient):
    """
    Service client for interacting with the categories API endpoints.
    """
    def __init__(self, base_url: str = API_BASE_URL):
        """Initializes the CategoryService."""
        super().__init__(base_url)

    def get_categories(self, token: str, page: int = 1, page_size: int = 10) -> Optional[Dict]:
        """
        Retrieves a paginated list of categories available to the user.
        
        Args:
            token (str): The access token.
            page (int): The page number.
            page_size (int): Items per page.
            
        Returns:
            Optional[Dict]: A dictionary containing the paginated response.
        """
        return self.get("/api/categories/", token, params={"page": page, "page_size": page_size})

    def create_category(self, token: str, name: str, type: str, is_essential: bool) -> bool:
        """
        Creates a new custom category for the user.
        
        Args:
            token (str): The access token.
            name (str): The name of the category.
            type (str): The type of the category ('INCOME' or 'EXPENSE').
            is_essential (bool): Whether the category represents an essential expense.
            
        Returns:
            bool: True if created successfully, False otherwise.
        """
        data = {
            "name": name,
            "type": type,
            "is_essential": is_essential
        }
        return self.post("/api/categories/", token, json=data) is not None

    def update_category(self, token: str, category_id: int, data: Dict[str, Any]) -> bool:
        """
        Updates an existing user category.
        
        Args:
            token (str): The access token.
            category_id (int): The ID of the category.
            data (Dict): The data to update.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        return self.patch(f"/api/categories/{category_id}/", token, json=data) is not None

    def delete_category(self, token: str, category_id: int) -> bool:
        """
        Deletes a specific user category.
        
        Args:
            token (str): The access token.
            category_id (int): The ID of the category.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        return self.delete(f"/api/categories/{category_id}/", token) is not None