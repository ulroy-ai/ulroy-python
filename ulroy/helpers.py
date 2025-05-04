from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import asyncio
import time
from datetime import datetime, timedelta
import httpx
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

def poll_task_status_sync(
    client,
    task_id: str,
    poll_interval: float = 1.0,
    timeout: float = 300.0,
    raise_on_error: bool = True
) -> TaskStatus:
    """
    Poll a task until it completes or times out (synchronous version).
    
    Args:
        client: The client instance
        task_id: ID of the task to poll
        poll_interval: Time between polls in seconds
        timeout: Maximum time to wait in seconds
        raise_on_error: Whether to raise an exception if the task fails
        
    Returns:
        The final task status
        
    Raises:
        TimeoutError: If the task doesn't complete within the timeout
        Exception: If the task fails and raise_on_error is True
    """
    start_time = time.time()
    
    while True:
        # Check if we've exceeded the timeout
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")
        
        # Get task status
        tasks = client.task.list_tasks()
        task = next((t for t in tasks["tasks"] if t["id"] == task_id), None)
        
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        status = task["status"]
        
        # Check if task is complete
        if status in ["completed", "failed"]:
            if status == "failed" and raise_on_error:
                raise Exception(f"Task {task_id} failed: {task.get('error', 'Unknown error')}")
            return TaskStatus(**task)
        
        # Wait before polling again
        time.sleep(poll_interval)

async def poll_task_status_async(
    client,
    task_id: str,
    poll_interval: float = 1.0,
    timeout: float = 300.0,
    raise_on_error: bool = True
) -> TaskStatus:
    """
    Poll a task until it completes or times out (asynchronous version).
    
    Args:
        client: The client instance
        task_id: ID of the task to poll
        poll_interval: Time between polls in seconds
        timeout: Maximum time to wait in seconds
        raise_on_error: Whether to raise an exception if the task fails
        
    Returns:
        The final task status
        
    Raises:
        TimeoutError: If the task doesn't complete within the timeout
        Exception: If the task fails and raise_on_error is True
        RuntimeError: If the client is closed during polling
    """
    start_time = datetime.now()
    timeout_delta = timedelta(seconds=timeout)
    last_error = None
    
    try:
        while True:
            # Check if we've exceeded the timeout
            if datetime.now() - start_time > timeout_delta:
                raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")
            
            try:
                # Get task status
                tasks = await client.task.list_tasks()
                task = next((t for t in tasks["tasks"] if t["id"] == task_id), None)
                
                if not task:
                    raise ValueError(f"Task {task_id} not found")
                
                status = task["status"]
                
                # Check if task is complete
                if status in ["completed", "failed"]:
                    if status == "failed" and raise_on_error:
                        error_msg = task.get('error', 'Unknown error')
                        raise Exception(f"Task {task_id} failed: {error_msg}")
                    return TaskStatus(**task)
                
                # Wait before polling again
                await asyncio.sleep(poll_interval)
                
            except (httpx.RequestError, APIError) as e:
                # Store the error but continue polling
                last_error = e
                await asyncio.sleep(poll_interval)
                continue
                
    except asyncio.CancelledError:
        # Handle task cancellation
        raise
    except Exception as e:
        # If we have a stored error, use that instead
        if last_error is not None:
            raise last_error
        raise
    finally:
        # Ensure we don't leave any resources hanging
        if hasattr(client, '_client') and client._client is not None:
            try:
                await client._client.aclose()
            except Exception:
                pass  # Ignore cleanup errors

def create_index_helpers_sync(client):
    """Create synchronous helper functions for index operations"""
    
    def list_indexes(page: int = 1, per_page: int = 10, search: Optional[str] = None) -> IndexListResponse:
        """List all indexes with pagination and optional search"""
        params = {"page": page, "per_page": per_page}
        if search:
            params["search"] = search
        response = client.get("/index/list", params=params)
        return IndexListResponse(**response)
    
    def get_index_info(index_id: str) -> Dict[str, Any]:
        """Get information about a specific index"""
        return client.get(f"/index/{index_id}/info")
    
    def query_index(index_id: str, text: str, k: int = 10) -> List[Dict[str, Any]]:
        """Query an index with text"""
        request = QueryRequest(text=text, k=k)
        return client.post(f"/index/{index_id}/query", json=request.model_dump())
    
    def hybrid_search(
        index_id: str,
        text: str,
        k: int = 10,
        vector_weight: float = 0.5,
        text_weight: float = 0.5,
        min_text_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Perform hybrid search on an index"""
        request = HybridSearchRequest(
            text=text,
            k=k,
            vector_weight=vector_weight,
            text_weight=text_weight,
            min_text_score=min_text_score
        )
        return client.post(f"/index/{index_id}/hybrid-search", json=request.model_dump())
    
    def update_metadata(index_id: str, primary_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Update metadata for an entry in an index"""
        request = UpdateMetadataRequest(primary_id=primary_id, metadata=metadata)
        return client.post(f"/index/{index_id}/update", json=request.model_dump())
    
    def delete_index_entries(
        index_id: str,
        entry_ids: List[str],
        wait: bool = True,
        poll_interval: float = 1.0,
        timeout: float = 300.0
    ) -> TaskStatus:
        """Delete entries from an index"""
        request = {"ids": entry_ids}
        response = client.post(f"/index/{index_id}/delete", json=request)
        task_status = TaskStatus(**response)
        
        if wait:
            return poll_task_status_sync(
                client,
                task_status.id,
                poll_interval=poll_interval,
                timeout=timeout
            )
        return task_status
    
    def list_index_entries(
        index_id: str,
        page: int = 1,
        per_page: int = 10,
        include_deleted: bool = False
    ) -> Dict[str, Any]:
        """List entries in an index with pagination"""
        params = {
            "page": page,
            "per_page": per_page,
            "include_deleted": include_deleted
        }
        return client.get(f"/index/{index_id}/entries", params=params)
    
    def delete_index_complete(
        index_id: str,
        wait: bool = True,
        poll_interval: float = 1.0,
        timeout: float = 300.0
    ) -> TaskStatus:
        """Delete an index completely, including all its data and metadata"""
        response = client.post(f"/index/{index_id}/delete-complete")
        task_status = TaskStatus(**response)
        
        if wait:
            return poll_task_status_sync(
                client,
                task_status.id,
                poll_interval=poll_interval,
                timeout=timeout
            )
        return task_status
    
    return {
        "list_indexes": list_indexes,
        "get_index_info": get_index_info,
        "query_index": query_index,
        "hybrid_search": hybrid_search,
        "update_metadata": update_metadata,
        "delete_index_entries": delete_index_entries,
        "list_index_entries": list_index_entries,
        "delete_index_complete": delete_index_complete
    }

def create_document_helpers_sync(client):
    """Create synchronous helper functions for document operations"""
    
    def list_documents(page: int = 1, per_page: int = 10, search: Optional[str] = None) -> DocumentListResponse:
        """List all documents with pagination and optional search"""
        params = {"page": page, "per_page": per_page}
        if search:
            params["search"] = search
        response = client.get("/document/list", params=params)
        return DocumentListResponse(**response)
    
    def get_document_info(doc_id: str) -> Dict[str, Any]:
        """Get information about a specific document"""
        return client.get(f"/document/{doc_id}/info")
    
    def query_document(doc_id: str, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """Query a document"""
        request = DocumentQuery(query=query, k=k)
        return client.post(f"/document/{doc_id}/index/query", json=request.model_dump())
    
    def research_document(
        doc_id: str,
        query: str,
        k: int = 10,
        wait: bool = True,
        poll_interval: float = 1.0,
        timeout: float = 300.0
    ) -> TaskStatus:
        """Research a document"""
        request = DocumentQuery(query=query, k=k)
        response = client.post(f"/document/{doc_id}/research/index", json=request.model_dump())
        task_status = TaskStatus(**response)
        
        if wait:
            return poll_task_status_sync(
                client,
                task_status.id,
                poll_interval=poll_interval,
                timeout=timeout
            )
        return task_status
    
    def query_research(doc_id: str, research_id: str, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """Query a specific research within a document"""
        request = DocumentQuery(query=query, k=k)
        return client.post(f"/document/{doc_id}/research/{research_id}/query", json=request.model_dump())
    
    def delete_document(
        doc_id: str,
        wait: bool = True,
        poll_interval: float = 1.0,
        timeout: float = 300.0
    ) -> TaskStatus:
        """Delete a document"""
        response = client.post(f"/document/{doc_id}/delete")
        task_status = TaskStatus(**response)
        
        if wait:
            return poll_task_status_sync(
                client,
                task_status.id,
                poll_interval=poll_interval,
                timeout=timeout
            )
        return task_status
    
    def index_document(
        doc_id: str,
        wait: bool = True,
        poll_interval: float = 1.0,
        timeout: float = 300.0
    ) -> TaskStatus:
        """Index a document"""
        response = client.post(f"/document/{doc_id}/index")
        task_status = TaskStatus(**response)
        
        if wait:
            return poll_task_status_sync(
                client,
                task_status.id,
                poll_interval=poll_interval,
                timeout=timeout
            )
        return task_status
    
    return {
        "list_documents": list_documents,
        "get_document_info": get_document_info,
        "query_document": query_document,
        "research_document": research_document,
        "query_research": query_research,
        "delete_document": delete_document,
        "index_document": index_document
    }

def create_task_helpers_sync(client):
    """Create synchronous helper functions for task operations"""
    
    def list_tasks(page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """List all tasks with pagination"""
        params = {"page": page, "per_page": per_page}
        return client.get("/task/list", params=params)
    
    def get_task_status(
        task_id: str,
        poll_interval: float = 1.0,
        timeout: float = 300.0
    ) -> TaskStatus:
        """Get the status of a task, optionally waiting for completion"""
        return poll_task_status_sync(
            client,
            task_id,
            poll_interval=poll_interval,
            timeout=timeout
        )
    
    return {
        "list_tasks": list_tasks,
        "get_task_status": get_task_status
    }

async def create_index_helpers_async(client):
    """Create asynchronous helper functions for index operations"""
    
    async def list_indexes(page: int = 1, per_page: int = 10, search: Optional[str] = None) -> IndexListResponse:
        """List all indexes with pagination and optional search"""
        params = {"page": page, "per_page": per_page}
        if search:
            params["search"] = search
        response = await client.get("/index/list", params=params)
        return IndexListResponse(**response)
    
    async def get_index_info(index_id: str) -> Dict[str, Any]:
        """Get information about a specific index"""
        return await client.get(f"/index/{index_id}/info")
    
    async def query_index(index_id: str, text: str, k: int = 10) -> List[Dict[str, Any]]:
        """Query an index with text"""
        request = QueryRequest(text=text, k=k)
        return await client.post(f"/index/{index_id}/query", json=request.model_dump())
    
    async def hybrid_search(
        index_id: str,
        text: str,
        k: int = 10,
        vector_weight: float = 0.5,
        text_weight: float = 0.5,
        min_text_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Perform hybrid search on an index"""
        request = HybridSearchRequest(
            text=text,
            k=k,
            vector_weight=vector_weight,
            text_weight=text_weight,
            min_text_score=min_text_score
        )
        return await client.post(f"/index/{index_id}/hybrid-search", json=request.model_dump())
    
    async def update_metadata(index_id: str, primary_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Update metadata for an entry in an index"""
        request = UpdateMetadataRequest(primary_id=primary_id, metadata=metadata)
        return await client.post(f"/index/{index_id}/update", json=request.model_dump())
    
    async def delete_index_entries(
        index_id: str,
        entry_ids: List[str],
        wait: bool = True,
        poll_interval: float = 1.0,
        timeout: float = 300.0
    ) -> TaskStatus:
        """Delete entries from an index"""
        request = {"ids": entry_ids}
        response = await client.post(f"/index/{index_id}/delete", json=request)
        task_status = TaskStatus(**response)
        
        if wait:
            return await poll_task_status_async(
                client,
                task_status.id,
                poll_interval=poll_interval,
                timeout=timeout
            )
        return task_status
    
    async def list_index_entries(
        index_id: str,
        page: int = 1,
        per_page: int = 10,
        include_deleted: bool = False
    ) -> Dict[str, Any]:
        """List entries in an index with pagination"""
        params = {
            "page": page,
            "per_page": per_page,
            "include_deleted": include_deleted
        }
        return await client.get(f"/index/{index_id}/entries", params=params)
    
    async def delete_index_complete(
        index_id: str,
        wait: bool = True,
        poll_interval: float = 1.0,
        timeout: float = 300.0
    ) -> TaskStatus:
        """Delete an index completely, including all its data and metadata"""
        response = await client.post(f"/index/{index_id}/delete-complete")
        task_status = TaskStatus(**response)
        
        if wait:
            return await poll_task_status_async(
                client,
                task_status.id,
                poll_interval=poll_interval,
                timeout=timeout
            )
        return task_status
    
    return {
        "list_indexes": list_indexes,
        "get_index_info": get_index_info,
        "query_index": query_index,
        "hybrid_search": hybrid_search,
        "update_metadata": update_metadata,
        "delete_index_entries": delete_index_entries,
        "list_index_entries": list_index_entries,
        "delete_index_complete": delete_index_complete
    }

async def create_document_helpers_async(client):
    """Create asynchronous helper functions for document operations"""
    
    async def list_documents(page: int = 1, per_page: int = 10, search: Optional[str] = None) -> DocumentListResponse:
        """List all documents with pagination and optional search"""
        params = {"page": page, "per_page": per_page}
        if search:
            params["search"] = search
        response = await client.get("/document/list", params=params)
        return DocumentListResponse(**response)
    
    async def get_document_info(doc_id: str) -> Dict[str, Any]:
        """Get information about a specific document"""
        return await client.get(f"/document/{doc_id}/info")
    
    async def query_document(doc_id: str, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """Query a document"""
        request = DocumentQuery(query=query, k=k)
        return await client.post(f"/document/{doc_id}/index/query", json=request.model_dump())
    
    async def research_document(
        doc_id: str,
        query: str,
        k: int = 10,
        wait: bool = True,
        poll_interval: float = 1.0,
        timeout: float = 300.0
    ) -> TaskStatus:
        """Research a document"""
        request = DocumentQuery(query=query, k=k)
        response = await client.post(f"/document/{doc_id}/research/index", json=request.model_dump())
        task_status = TaskStatus(**response)
        
        if wait:
            return await poll_task_status_async(
                client,
                task_status.id,
                poll_interval=poll_interval,
                timeout=timeout
            )
        return task_status
    
    async def query_research(doc_id: str, research_id: str, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """Query a specific research within a document"""
        request = DocumentQuery(query=query, k=k)
        return await client.post(f"/document/{doc_id}/research/{research_id}/query", json=request.model_dump())
    
    async def delete_document(
        doc_id: str,
        wait: bool = True,
        poll_interval: float = 1.0,
        timeout: float = 300.0
    ) -> TaskStatus:
        """Delete a document"""
        response = await client.post(f"/document/{doc_id}/delete")
        task_status = TaskStatus(**response)
        
        if wait:
            return await poll_task_status_async(
                client,
                task_status.id,
                poll_interval=poll_interval,
                timeout=timeout
            )
        return task_status
    
    async def index_document(
        doc_id: str,
        wait: bool = True,
        poll_interval: float = 1.0,
        timeout: float = 300.0
    ) -> TaskStatus:
        """Index a document"""
        response = await client.post(f"/document/{doc_id}/index")
        task_status = TaskStatus(**response)
        
        if wait:
            return await poll_task_status_async(
                client,
                task_status.id,
                poll_interval=poll_interval,
                timeout=timeout
            )
        return task_status
    
    return {
        "list_documents": list_documents,
        "get_document_info": get_document_info,
        "query_document": query_document,
        "research_document": research_document,
        "query_research": query_research,
        "delete_document": delete_document,
        "index_document": index_document
    }

async def create_task_helpers_async(client):
    """Create asynchronous helper functions for task operations"""
    
    async def list_tasks(page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """List all tasks with pagination"""
        params = {"page": page, "per_page": per_page}
        return await client.get("/task/list", params=params)
    
    async def get_task_status(
        task_id: str,
        poll_interval: float = 1.0,
        timeout: float = 300.0
    ) -> TaskStatus:
        """Get the status of a task, optionally waiting for completion"""
        return await poll_task_status_async(
            client,
            task_id,
            poll_interval=poll_interval,
            timeout=timeout
        )
    
    return {
        "list_tasks": list_tasks,
        "get_task_status": get_task_status
    }

# Async versions (renamed from original functions)
create_index_helpers = create_index_helpers_async
create_document_helpers = create_document_helpers_async
create_task_helpers = create_task_helpers_async
poll_task_status = poll_task_status_async 