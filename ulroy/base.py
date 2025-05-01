from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import httpx

class UlroyError(Exception):
    """Base exception for Ulroy client errors."""
    pass

class APIError(UlroyError):
    """Exception raised when the API returns an error."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error {status_code}: {message}")

class BaseClient:
    """Base client class with common functionality."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://www.ulroy.com/api/v1",
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        """
        Initialize the base client.
        
        Args:
            api_key: Your Ulroy API key
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _build_url(self, endpoint: str) -> str:
        """Build the full URL for an endpoint."""
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle the API response and raise appropriate exceptions."""
        if response.status_code >= 400:
            try:
                error_data = response.json()
                message = error_data.get("message", "Unknown error")
            except ValueError:
                message = response.text or "Unknown error"
            raise APIError(response.status_code, message)
        
        return response.json()

    def _get_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Get headers with optional additional headers."""
        headers = self._headers.copy()
        if additional_headers:
            headers.update(additional_headers)
        return headers 