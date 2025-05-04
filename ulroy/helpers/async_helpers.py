from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import asyncio
import time
from datetime import datetime, timedelta
from ulroy.exceptions import APIError

class IndexInfo(BaseModel):
    """Information about an index"""
    id: str
    name: str
    description: str

class DocumentInfo(BaseModel):
    """Information about a document"""
    id: str
    name: str
    description: Optional[str] = None

class QueryRequest(BaseModel):
    """Request for querying an index or document"""
    text: str
    k: int = 10

class DocumentQuery(BaseModel):
    """Request for querying a document"""
    query: str
    k: int = 10

class HybridSearchRequest(BaseModel):
    """Request for hybrid search"""
    text: str
    k: int = 10
    vector_weight: float = 0.5
    text_weight: float = 0.5
    min_text_score: float = 0.0

class UpdateMetadataRequest(BaseModel):
    """Request for updating metadata"""
    primary_id: str
    metadata: Dict[str, Any]

class PaginatedResponse(BaseModel):
    """Base class for paginated responses"""
    total: int
    page: int
    per_page: int

class IndexListResponse(PaginatedResponse):
    """Response for listing indexes"""
    indexes: List[IndexInfo]

class DocumentListResponse(PaginatedResponse):
    """Response for listing documents"""
    documents: List[DocumentInfo]

class TaskStatus(BaseModel):
    """Status of a task"""
    id: str
    status: str
    progress: Optional[float] = None
    result: Optional[Dict[str, Any]] = None

async def create_index_helpers(client):
    """Create async index helper functions"""
    async def create(self, index_config: Dict[str, Any]) -> str:
        """Create a new index"""
        response = await client.post("/index/create", json=index_config)
        return response["index_id"]

    async def list(self, page: int = 1, per_page: int = 10, search: Optional[str] = None) -> IndexListResponse:
        """List all indexes"""
        params = {"page": page, "per_page": per_page}
        if search:
            params["search"] = search
        response = await client.get("/index/list", params=params)
        return IndexListResponse(**response)

    async def get(self, index_id: str) -> Dict[str, Any]:
        """Get index details"""
        return await client.get(f"/index/{index_id}/info")

    async def delete(self, index_id: str) -> Dict[str, Any]:
        """Delete an index"""
        return await client.post(f"/index/{index_id}/delete-complete")

    return type("IndexHelpers", (), {
        "create": create,
        "list": list,
        "get": get,
        "delete": delete
    })()

async def create_document_helpers(client):
    """Create async document helper functions"""
    class DocumentHelpers:
        async def add(self, index_id: str, document: Dict[str, Any]) -> Dict[str, Any]:
            """Add a document to an index"""
            # Note: This endpoint requires file upload and metadata as form data
            # The current implementation needs to be updated to handle file uploads
            raise NotImplementedError("Document creation requires file upload. Use the appropriate file upload method.")

        async def get(self, index_id: str, doc_id: str) -> Dict[str, Any]:
            """Get a document from an index"""
            return await client.get(f"/document/{doc_id}/info")

        async def update(self, index_id: str, document: Dict[str, Any]) -> Dict[str, Any]:
            """Update a document in an index"""
            # Note: The API doesn't have a direct update endpoint for documents
            raise NotImplementedError("Document update is not supported by the API")

        async def delete(self, index_id: str, doc_id: str) -> Dict[str, Any]:
            """Delete a document from an index"""
            return await client.post(f"/document/{doc_id}/delete")

        async def search(self, index_id: str, query: str, k: int = 10) -> List[Dict[str, Any]]:
            """Search documents in an index"""
            response = await client.post(f"/document/{index_id}/index/query", json={"query": query, "k": k})
            return response.get("results", [])

        async def list(self, page: int = 1, per_page: int = 10, search: Optional[str] = None) -> Dict[str, Any]:
            """List all documents with pagination and search"""
            params = {"page": page, "per_page": per_page}
            if search:
                params["search"] = search
            return await client.get("/document/list", params=params)

        async def index(self, doc_id: str) -> Dict[str, Any]:
            """Index a document"""
            return await client.post(f"/document/{doc_id}/index")

        async def research(self, doc_id: str, query: str, k: int = 10) -> Dict[str, Any]:
            """Research a document"""
            return await client.post(f"/document/{doc_id}/research/index", json={"query": query, "k": k})

        async def query_research(self, doc_id: str, research_id: str, query: str, k: int = 10) -> List[Dict[str, Any]]:
            """Query a specific research within a document"""
            return await client.post(f"/document/{doc_id}/research/{research_id}/query", json={"query": query, "k": k})

    return DocumentHelpers()

async def create_task_helpers(client):
    """Create async task helper functions"""
    async def get_status(task_id: str) -> TaskStatus:
        """Get task status"""
        response = await client.get(f"/tasks/{task_id}")
        return TaskStatus(**response)

    async def wait_for_completion(task_id: str, poll_interval: float = 1.0, timeout: float = 300.0) -> TaskStatus:
        """Wait for a task to complete"""
        start_time = time.time()
        while True:
            status = await get_status(task_id)
            if status.status in ["completed", "failed"]:
                return status
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")
            await asyncio.sleep(poll_interval)

    return type("TaskHelpers", (), {
        "get_status": get_status,
        "wait_for_completion": wait_for_completion
    })() 