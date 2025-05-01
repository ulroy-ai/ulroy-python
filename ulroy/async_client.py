from typing import Optional, Dict, Any, Union
import httpx
from .base import BaseClient, APIError
from .helpers import create_index_helpers, create_document_helpers, create_task_helpers

class AsyncUlroyClient(BaseClient):
    """Asynchronous client for the Ulroy API."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.ulroy.com/v1",
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        super().__init__(api_key, base_url, timeout, max_retries)
        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers=self._headers,
            base_url=self.base_url,
        )
        
        # Initialize helper functions
        self.index = create_index_helpers(self)
        self.document = create_document_helpers(self)
        self.task = create_task_helpers(self)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Close the HTTP client."""
        if hasattr(self, '_client') and self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _request(
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
                response = await self._client.request(
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

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a GET request."""
        return await self._request("GET", endpoint, params=params, headers=headers)

    async def post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a POST request."""
        return await self._request("POST", endpoint, json=json, headers=headers)

    async def put(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a PUT request."""
        return await self._request("PUT", endpoint, json=json, headers=headers)

    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a DELETE request."""
        return await self._request("DELETE", endpoint, params=params, headers=headers) 