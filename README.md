# Ulroy Python Client

A Python client library for the Ulroy API, supporting both synchronous and asynchronous operations.

## Installation

```bash
pip install ulroy
```

## Usage

### Synchronous Client

```python
from ulroy.sync import UlroyClient

# Initialize the client
client = UlroyClient(api_key="your-api-key")

# List all indexes
indexes = client.index.list()

# Query a specific index
results = client.index.query(
    index_id="your-index-id",
    query="your search query",
    top_k=10
)

# List documents in an index
documents = client.document.list(index_id="your-index-id")

# Index a document and wait for completion
task = client.document.index(
    index_id="your-index-id",
    document_id="doc-123",
    content="Your document content",
    metadata={"source": "example"},
    wait=True,  # Wait for indexing to complete
    poll_interval=1.0,  # Check status every second
    timeout=300.0  # Timeout after 5 minutes
)

# Delete entries from an index and wait for completion
task = client.index.delete_entries(
    index_id="your-index-id",
    document_ids=["doc-123", "doc-456"],
    wait=True,
    poll_interval=1.0,
    timeout=300.0
)

# Delete a document and wait for completion
task = client.document.delete(
    index_id="your-index-id",
    document_id="doc-123",
    wait=True,
    poll_interval=1.0,
    timeout=300.0
)

# Get task status (with optional waiting)
status = client.task.get_status(
    task_id="task-123",
    wait=True,
    poll_interval=1.0,
    timeout=300.0
)
```

### Asynchronous Client

```python
import asyncio
from ulroy.async_client import AsyncUlroyClient

async def main():
    # Initialize the client
    client = AsyncUlroyClient(api_key="your-api-key")

    # List all indexes
    indexes = await client.index.list()

    # Query a specific index
    results = await client.index.query(
        index_id="your-index-id",
        query="your search query",
        top_k=10
    )

    # List documents in an index
    documents = await client.document.list(index_id="your-index-id")

    # Index a document and wait for completion
    task = await client.document.index(
        index_id="your-index-id",
        document_id="doc-123",
        content="Your document content",
        metadata={"source": "example"},
        wait=True,  # Wait for indexing to complete
        poll_interval=1.0,  # Check status every second
        timeout=300.0  # Timeout after 5 minutes
    )

    # Delete entries from an index and wait for completion
    task = await client.index.delete_entries(
        index_id="your-index-id",
        document_ids=["doc-123", "doc-456"],
        wait=True,
        poll_interval=1.0,
        timeout=300.0
    )

    # Delete a document and wait for completion
    task = await client.document.delete(
        index_id="your-index-id",
        document_id="doc-123",
        wait=True,
        poll_interval=1.0,
        timeout=300.0
    )

    # Get task status (with optional waiting)
    status = await client.task.get_status(
        task_id="task-123",
        wait=True,
        poll_interval=1.0,
        timeout=300.0
    )

    # Close the client
    await client.close()

asyncio.run(main())
```

## Task Polling

Both the synchronous and asynchronous clients support polling for long-running tasks. This is useful for operations like indexing documents or deleting entries. The polling functionality is built into the helper functions and can be controlled with the following parameters:

- `wait`: Whether to wait for the task to complete (default: `False`)
- `poll_interval`: How often to check the task status in seconds (default: `1.0`)
- `timeout`: Maximum time to wait for task completion in seconds (default: `300.0`)

When `wait=True`, the helper function will poll the task status until it completes or times out. If the task fails, an exception will be raised. If the task times out, a `TimeoutError` will be raised.

## Available Helper Functions

### Index Helpers

- `list()`: List all indexes
- `get(index_id)`: Get a specific index
- `create(name, description)`: Create a new index
- `delete(index_id)`: Delete an index
- `query(index_id, query, top_k)`: Query an index
- `delete_entries(index_id, document_ids, wait=False, poll_interval=1.0, timeout=300.0)`: Delete entries from an index

### Document Helpers

- `list(index_id)`: List documents in an index
- `get(index_id, document_id)`: Get a specific document
- `index(index_id, document_id, content, metadata, wait=False, poll_interval=1.0, timeout=300.0)`: Index a document
- `delete(index_id, document_id, wait=False, poll_interval=1.0, timeout=300.0)`: Delete a document

### Task Helpers

- `get_status(task_id, wait=False, poll_interval=1.0, timeout=300.0)`: Get the status of a task

## Documentation

For detailed documentation, please visit [our documentation site](https://ulroy-client.readthedocs.io).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 