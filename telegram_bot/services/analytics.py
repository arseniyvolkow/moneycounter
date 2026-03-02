from typing import Optional, List, Dict
from .base import BaseClient
from config import API_BASE_URL

class AnalyticsService(BaseClient):
    """
    Service client for interacting with the analytics API endpoints.
    """
    def __init__(self, base_url: str = API_BASE_URL):
        """Initializes the AnalyticsService."""
        super().__init__(base_url)

    def get_analytics(self, token: str, start_date: str = None, end_date: str = None) -> Optional[Dict]:
        """
        Retrieves financial analytics (income and expense summaries) for a specified date range.
        
        Args:
            token (str): The access token.
            start_date (str, optional): The start date (YYYY-MM-DD).
            end_date (str, optional): The end date (YYYY-MM-DD).
            
        Returns:
            Optional[Dict]: A dictionary containing 'income' and 'expenses' summaries.
        """
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
            
        return self.get("/api/analytics/", token, params=params)