from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import time
from datetime import datetime, timedelta
from ulroy.exceptions import APIError
from .async_helpers import (
    IndexInfo, DocumentInfo, QueryRequest, DocumentQuery,
    HybridSearchRequest, UpdateMetadataRequest, PaginatedResponse,
    IndexListResponse, DocumentListResponse, TaskStatus
)

def create_index_helpers(client):
    """Create sync index helper functions"""
    def create(index_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new index"""
        return client.post("/indexes", json=index_config)

    def list(page: int = 1, per_page: int = 10, search: Optional[str] = None) -> IndexListResponse:
        """List all indexes"""
        params = {"page": page, "per_page": per_page}
        if search:
            params["search"] = search
        response = client.get("/indexes", params=params)
        return IndexListResponse(**response)

    def get(index_id: str) -> Dict[str, Any]:
        """Get index details"""
        return client.get(f"/indexes/{index_id}")

    def delete(index_id: str) -> Dict[str, Any]:
        """Delete an index"""
        return client.delete(f"/indexes/{index_id}")

    return type("IndexHelpers", (), {
        "create": create,
        "list": list,
        "get": get,
        "delete": delete
    })()

def create_document_helpers(client):
    """Create sync document helper functions"""
    def add(index_id: str, document: Dict[str, Any]) -> Dict[str, Any]:
        """Add a document to an index"""
        return client.post(f"/indexes/{index_id}/documents", json=document)

    def get(index_id: str, doc_id: str) -> Dict[str, Any]:
        """Get a document from an index"""
        return client.get(f"/indexes/{index_id}/documents/{doc_id}")

    def update(index_id: str, document: Dict[str, Any]) -> Dict[str, Any]:
        """Update a document in an index"""
        return client.put(f"/indexes/{index_id}/documents/{document['id']}", json=document)

    def delete(index_id: str, doc_id: str) -> Dict[str, Any]:
        """Delete a document from an index"""
        return client.delete(f"/indexes/{index_id}/documents/{doc_id}")

    def search(index_id: str, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """Search documents in an index"""
        response = client.post(f"/indexes/{index_id}/search", json={"query": query, "k": k})
        return response.get("results", [])

    return type("DocumentHelpers", (), {
        "add": add,
        "get": get,
        "update": update,
        "delete": delete,
        "search": search
    })()

def create_task_helpers(client):
    """Create sync task helper functions"""
    def get_status(task_id: str) -> TaskStatus:
        """Get task status"""
        response = client.get(f"/tasks/{task_id}")
        return TaskStatus(**response)

    def wait_for_completion(task_id: str, poll_interval: float = 1.0, timeout: float = 300.0) -> TaskStatus:
        """Wait for a task to complete"""
        start_time = time.time()
        while True:
            status = get_status(task_id)
            if status.status in ["completed", "failed"]:
                return status
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")
            time.sleep(poll_interval)

    return type("TaskHelpers", (), {
        "get_status": get_status,
        "wait_for_completion": wait_for_completion
    })() 