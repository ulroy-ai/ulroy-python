import asyncio
import os
from ulroy import AsyncUlroyClient
import json
from pathlib import Path

async def test_index_and_document_apis():
    # Initialize client
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidHlwZSI6ImFjY2Vzc190b2tlbiIsImlhdCI6MTc0NjE5MTIzMSwiZXhwIjoxNzQ4NzgzMjMxfQ.-nQgFd7Ep6VY0B3j1-t_yuHG6Ayt_lDgK_KX5qNZ7SE"
    if not api_key:
        raise ValueError("Please set ULROY_API_KEY environment variable")
    
    async with AsyncUlroyClient(api_key=api_key, base_url="http://localhost:8000/api/v1") as client:
        # Test index creation
        print("\n=== Testing Index Creation ===")
        index_name = "test_index"
        index_config = {
            "name": index_name,
            "description": "Test index for API testing",
            "settings": {
                "similarity": "cosine"
            }
        }
        
        try:
            # Create index
            print("Creating index...")
            index_id = await client.index.create(index_config)
            print(f"Index created with ID: {index_id}")
            
            # List indexes
            print("\nListing indexes...")
            list_response = await client.index.list()
            print(f"Available indexes: {list_response}")
            
            # Get index details
            print("\nGetting index details...")
            get_response = await client.index.get(index_id)
            print(f"Index details: {get_response}")
            
            # Test document operations
            print("\n=== Testing Document Operations ===")
            document = {
                "id": "doc1",
                "content": "This is a test document",
                "metadata": {
                    "source": "test",
                    "timestamp": "2024-05-01"
                }
            }
            
            # Add document
            print("Adding document...")
            add_response = await client.document.add(index_id, document)
            print(f"Document added: {add_response}")
            
            # Get document
            print("\nGetting document...")
            get_doc_response = await client.document.get(index_id, "doc1")
            print(f"Document retrieved: {get_doc_response}")
            
            # Search documents
            print("\nSearching documents...")
            search_response = await client.document.search(index_id, query="test document")
            print(f"Search results: {search_response}")
            
            # Update document
            print("\nUpdating document...")
            updated_doc = {
                "id": "doc1",
                "content": "This is an updated test document",
                "metadata": {
                    "source": "test",
                    "timestamp": "2024-05-01",
                    "updated": True
                }
            }
            update_response = await client.document.update(index_id, updated_doc)
            print(f"Document updated: {update_response}")
            
            # Delete document
            print("\nDeleting document...")
            delete_response = await client.document.delete(index_id, "doc1")
            print(f"Document deleted: {delete_response}")
            
        finally:
            # Clean up - delete index
            print("\nCleaning up - deleting index...")
            try:
                delete_index_response = await client.index.delete(index_id)
                print(f"Index deleted: {delete_index_response}")
            except Exception as e:
                print(f"Error deleting index: {e}")

async def test_document_processing():
    # Initialize client
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidHlwZSI6ImFjY2Vzc190b2tlbiIsImlhdCI6MTc0NjE5MTIzMSwiZXhwIjoxNzQ4NzgzMjMxfQ.-nQgFd7Ep6VY0B3j1-t_yuHG6Ayt_lDgK_KX5qNZ7SE"
    if not api_key:
        raise ValueError("Please set ULROY_API_KEY environment variable")
    
    async with AsyncUlroyClient(api_key=api_key, base_url="http://localhost:8000/api/v1") as client:
        try:
            # Create a sample document file
            sample_doc_path = Path("sample_document.txt")
            sample_content = """This is a sample document for testing the Ulroy API.
It contains multiple paragraphs of text that can be processed and indexed.

The document includes various topics and concepts that can be used for testing
the search and research capabilities of the system.

This is the third paragraph, demonstrating that the document has enough content
to be meaningfully processed and analyzed by the system."""
            
            # Write the sample document
            with open(sample_doc_path, "w") as f:
                f.write(sample_content)
            
            # Prepare metadata
            metadata = {
                "title": "Sample Test Document",
                "author": "Test User",
                "category": "Test",
                "description": "A sample document for testing the Ulroy API",
                "tags": ["test", "sample", "document"]
            }
            
            # Note: In a real implementation, you would need to implement file upload
            # For now, we'll just test the other document operations
            
            # List documents
            print("\nListing documents...")
            list_response = await client.document.list()
            print(f"Documents: {list_response}")
            
            # Create a test document ID (in real usage, this would come from the create response)
            test_doc_id = "test_doc_123"
            
            # Index the document
            print("\nIndexing document...")
            index_response = await client.document.index(test_doc_id)
            print(f"Index response: {index_response}")
            
            # Query the document
            print("\nQuerying document...")
            query_response = await client.document.search(test_doc_id, query="sample document")
            print(f"Query results: {query_response}")
            
            # Research the document
            print("\nResearching document...")
            research_response = await client.document.research(test_doc_id, query="system capabilities")
            print(f"Research response: {research_response}")
            
            # Get document info
            print("\nGetting document info...")
            info_response = await client.document.get(None, test_doc_id)  # index_id is not used in get
            print(f"Document info: {info_response}")
            
            # Delete the document
            print("\nDeleting document...")
            delete_response = await client.document.delete(None, test_doc_id)  # index_id is not used in delete
            print(f"Delete response: {delete_response}")
            
        finally:
            # Clean up - remove the sample document file
            if sample_doc_path.exists():
                sample_doc_path.unlink()
            print("\nCleaned up sample document file")

if __name__ == "__main__":
    asyncio.run(test_index_and_document_apis())
    asyncio.run(test_document_processing()) 