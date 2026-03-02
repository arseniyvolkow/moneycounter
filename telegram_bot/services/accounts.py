from typing import List, Dict, Optional, Any
from .base import BaseClient
from config import API_BASE_URL

class AccountService(BaseClient):
    """
    Service client for interacting with the accounts API endpoints.
    """
    def __init__(self, base_url: str = API_BASE_URL):
        """Initializes the AccountService."""
        super().__init__(base_url)

    def get_accounts(self, token: str, page: int = 1, page_size: int = 10) -> Optional[Dict]:
        """
        Retrieves a paginated list of accounts for the user.
        
        Args:
            token (str): The access token.
            page (int): The page number to retrieve.
            page_size (int): The number of items per page.
            
        Returns:
            Optional[Dict]: A dictionary containing the paginated response.
        """
        return self.get("/api/accounts/", token, params={"page": page, "page_size": page_size})

    def get_account(self, token: str, account_id: int) -> Optional[Dict]:
        """
        Retrieves details of a specific account by its ID.
        
        Args:
            token (str): The access token.
            account_id (int): The ID of the account.
            
        Returns:
            Optional[Dict]: The account data.
        """
        return self.get(f"/api/accounts/{account_id}/", token)

    def create_account(self, token: str, name: str, currency_id: int, balance: float) -> bool:
        """
        Creates a new financial account for the user.
        
        Args:
            token (str): The access token.
            name (str): The name of the account.
            currency_id (int): The ID of the associated currency.
            balance (float): The initial balance of the account.
            
        Returns:
            bool: True if created successfully, False otherwise.
        """
        data = {
            "name": name,
            "currency": currency_id,
            "balance": balance
        }
        return self.post("/api/accounts/", token, json=data) is not None

    def update_account(self, token: str, account_id: int, data: Dict[str, Any]) -> bool:
        """
        Updates an existing account.
        
        Args:
            token (str): The access token.
            account_id (int): The ID of the account to update.
            data (Dict): The data to update.
            
        Returns:
            bool: True if updated successfully, False otherwise.
        """
        return self.patch(f"/api/accounts/{account_id}/", token, json=data) is not None

    def get_currencies(self, token: str) -> Optional[List[Dict]]:
        """
        Retrieves a list of available currencies.
        
        Args:
            token (str): The access token.
            
        Returns:
            Optional[List[Dict]]: A list of currency data dictionaries.
        """
        response = self.get("/api/currencies/", token)
        if isinstance(response, dict) and 'results' in response:
            return response['results']
        if isinstance(response, list):
            return response
        return None