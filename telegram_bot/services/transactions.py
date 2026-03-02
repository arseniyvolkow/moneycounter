from typing import Optional, Dict, List, Any
from .base import BaseClient
from config import API_BASE_URL

class TransactionService(BaseClient):
    """
    Service client for interacting with the transactions API endpoints.
    """
    def __init__(self, base_url: str = API_BASE_URL):
        """Initializes the TransactionService."""
        super().__init__(base_url)

    def get_transactions(self, token: str, page: int = 1, page_size: int = 10, category_id: int = None, start_date: str = None, end_date: str = None) -> Optional[Dict]:
        """
        Retrieves a paginated list of transactions, optionally filtered.
        
        Args:
            token (str): The access token.
            page (int): The page number.
            page_size (int): Items per page.
            category_id (int, optional): Filter by category.
            start_date (str, optional): Filter by start date (YYYY-MM-DD).
            end_date (str, optional): Filter by end date (YYYY-MM-DD).
            
        Returns:
            Optional[Dict]: A dictionary containing the paginated response.
        """
        params = {
            "page": page,
            "page_size": page_size
        }
        if category_id:
            params["category"] = category_id
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        return self.get("/api/transactions/", token, params=params)

    def create_text_transaction(self, token: str, text: str, account_id: int, chat_id: int = None) -> bool:
        """
        Submits a text-based transaction description for AI processing.
        
        Args:
            token (str): The access token.
            text (str): The raw text description of the transaction.
            account_id (int): The ID of the account.
            chat_id (int, optional): Telegram chat ID for asynchronous notifications.
            
        Returns:
            bool: True if successfully submitted, False otherwise.
        """
        data = {
            "text": text,
            "account_id": account_id
        }
        if chat_id:
            data["chat_id"] = chat_id
            
        return self.post("/api/text-to-transaction/", token, json=data) is not None

    def create_voice_transaction(self, token: str, file_obj, account_id: int, chat_id: int = None) -> bool:
        """
        Submits a voice-based transaction audio file for STT and AI processing.
        
        Args:
            token (str): The access token.
            file_obj: The opened file object containing the voice message.
            account_id (int): The ID of the account.
            chat_id (int, optional): Telegram chat ID for asynchronous notifications.
            
        Returns:
            bool: True if successfully submitted, False otherwise.
        """
        files = {'audio_file': file_obj}
        data = {'account_id': account_id}
        if chat_id:
            data['chat_id'] = chat_id
            
        return self.post("/api/voice-to-transaction/", token, data=data, files=files) is not None

    def update_transaction(self, token: str, transaction_id: int, data: Dict[str, Any]) -> bool:
        """
        Updates an existing transaction.
        
        Args:
            token (str): The access token.
            transaction_id (int): The ID of the transaction to update.
            data (Dict): The data to update.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        return self.patch(f"/api/transactions/{transaction_id}/", token, json=data) is not None

    def delete_transaction(self, token: str, transaction_id: int) -> bool:
        """
        Deletes a specific transaction.
        
        Args:
            token (str): The access token.
            transaction_id (int): The ID of the transaction to delete.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        return self.delete(f"/api/transactions/{transaction_id}/", token) is not None