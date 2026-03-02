import requests
from typing import Optional, Dict, Any, Union
from config import API_BASE_URL

class BaseClient:
    """
    Base API client providing common HTTP request methods to interact with the backend service.
    """
    def __init__(self, base_url: str = API_BASE_URL):
        """
        Initializes the base client.
        
        Args:
            base_url (str): The base URL of the API.
        """
        self.base_url = base_url

    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        """
        Constructs the HTTP headers including the authorization token if provided.
        
        Args:
            token (str, optional): The JWT access token.
            
        Returns:
            Dict[str, str]: The constructed headers dictionary.
        """
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _request(self, method: str, endpoint: str, token: Optional[str] = None, **kwargs) -> Optional[Union[Dict, list, bool]]:
        """
        Executes an HTTP request and handles the response.
        
        Args:
            method (str): The HTTP method (GET, POST, PATCH, DELETE).
            endpoint (str): The API endpoint path.
            token (str, optional): The authorization token.
            **kwargs: Additional arguments to pass to the requests library (json, data, files, params).
            
        Returns:
            Optional[Union[Dict, list, bool]]: The parsed JSON response, a boolean indicating success, or None on error.
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(token)
        # Merge headers if provided in kwargs, but don't overwrite Authorization if we set it
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))
        
        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            
            if response.status_code == 204:
                return True
            
            if 200 <= response.status_code < 300:
                try:
                    return response.json()
                except ValueError:
                    return True # Success but no body
            
            # Log error (could be improved with a proper logger)
            print(f"API Error [{method} {endpoint}]: {response.status_code} - {response.text}")
            return None
            
        except requests.RequestException as e:
            print(f"Request Exception [{method} {endpoint}]: {e}")
            return None

    def get(self, endpoint: str, token: str, params: Dict = None) -> Any:
        """Performs a GET request."""
        return self._request("GET", endpoint, token, params=params)

    def post(self, endpoint: str, token: str, json: Dict = None, data: Dict = None, files: Dict = None) -> Any:
        """Performs a POST request."""
        return self._request("POST", endpoint, token, json=json, data=data, files=files)

    def patch(self, endpoint: str, token: str, json: Dict = None) -> Any:
        """Performs a PATCH request."""
        return self._request("PATCH", endpoint, token, json=json)

    def delete(self, endpoint: str, token: str) -> Any:
        """Performs a DELETE request."""
        return self._request("DELETE", endpoint, token)