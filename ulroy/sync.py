from typing import Optional, Dict, Any, Union
import httpx
from .base import BaseClient, APIError
from .helpers import (
    create_index_helpers_sync,
    create_document_helpers_sync,
    create_task_helpers_sync
)

class UlroyClient(BaseClient):
    """Synchronous client for the Ulroy API."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://www.ulroy.com/api/v1",
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        super().__init__(api_key, base_url, timeout, max_retries)
        self._client = httpx.Client(
            timeout=timeout,
            headers=self._headers,
            base_url=self.base_url,
        )
        
        # Initialize helper functions
        self.index = create_index_helpers_sync(self)
        self.document = create_document_helpers_sync(self)
        self.task = create_task_helpers_sync(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the HTTP client."""
        if hasattr(self, '_client') and self._client is not None:
            self._client.close()
            self._client = None

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request with retry logic."""
        if not hasattr(self, '_client') or self._client is None:
            raise RuntimeError("Client is closed")
            
        url = self._build_url(endpoint)
        headers = self._get_headers(headers)
        
        for attempt in range(self.max_retries):
            try:
                response = self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    headers=headers,
                )
                return self._handle_response(response)
            except (httpx.RequestError, APIError) as e:
                if attempt == self.max_retries - 1:
                    raise
                continue

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a GET request."""
        return self._request("GET", endpoint, params=params, headers=headers)

    def post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a POST request."""
        return self._request("POST", endpoint, json=json, headers=headers)

    def put(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a PUT request."""
        return self._request("PUT", endpoint, json=json, headers=headers)

    def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a DELETE request."""
        return self._request("DELETE", endpoint, params=params, headers=headers) 