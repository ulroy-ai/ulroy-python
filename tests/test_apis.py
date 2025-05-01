import asyncio
import os
from ulroy import AsyncUlroyClient

async def test_index_and_document_apis():
    # Initialize client
    api_key = os.getenv("ULROY_API_KEY")
    if not api_key:
        raise ValueError("Please set ULROY_API_KEY environment variable")
    
    async with AsyncUlroyClient(api_key=api_key) as client:
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
            create_response = await client.index.create(index_config)
            print(f"Index created: {create_response}")
            
            # List indexes
            print("\nListing indexes...")
            list_response = await client.index.list()
            print(f"Available indexes: {list_response}")
            
            # Get index details
            print("\nGetting index details...")
            get_response = await client.index.get(index_name)
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
            add_response = await client.document.add(index_name, document)
            print(f"Document added: {add_response}")
            
            # Get document
            print("\nGetting document...")
            get_doc_response = await client.document.get(index_name, "doc1")
            print(f"Document retrieved: {get_doc_response}")
            
            # Search documents
            print("\nSearching documents...")
            search_response = await client.document.search(index_name, query="test document")
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
            update_response = await client.document.update(index_name, updated_doc)
            print(f"Document updated: {update_response}")
            
            # Delete document
            print("\nDeleting document...")
            delete_response = await client.document.delete(index_name, "doc1")
            print(f"Document deleted: {delete_response}")
            
        finally:
            # Clean up - delete index
            print("\nCleaning up - deleting index...")
            try:
                delete_index_response = await client.index.delete(index_name)
                print(f"Index deleted: {delete_index_response}")
            except Exception as e:
                print(f"Error deleting index: {e}")

if __name__ == "__main__":
    asyncio.run(test_index_and_document_apis()) 