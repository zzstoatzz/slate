# Slate Memory Server

A persistent memory MCP server powered by SlateDB for bottomless storage.

## What is this?

Slate Memory Server is an MCP (Model Context Protocol) server that provides persistent memory storage for AI assistants. Unlike traditional memory servers that use in-memory storage, this uses SlateDB to write directly to object storage (S3, GCS, MinIO), providing:

- **Bottomless storage capacity** - memories persist to object storage
- **High durability** - leverages object storage reliability
- **Persistence across sessions** - memories survive server restarts
- **Cost-effective** - batched writes reduce API costs

## Installation

```bash
uv add slatedb fastmcp
```

## Usage

Run the MCP server:

```bash
# Local storage (default)
uv run -m slate

# With S3 storage
export SLATE_S3_BUCKET=your-bucket-name
export SLATE_S3_PREFIX=your-prefix  # optional
uv run -m slate
```

### Using with Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "slate-memory": {
      "command": "uv",
      "args": ["run", "-m", "slate"],
      "cwd": "/path/to/slate"
    }
  }
}
```

Or install directly from GitHub:

```bash
claude mcp add slate-memory --uvx --with slatedb --with fastmcp git+https://github.com/zzstoatzz/slate.git@mcp-server -m slate
```

## Available Tools

### `store_memory`
Store a value in persistent memory.
- `key`: Unique identifier for this memory
- `value`: Any JSON-serializable data
- `metadata`: Optional metadata

### `retrieve_memory`
Retrieve a value from memory by key.
- `key`: The key to look up

### `search_memory`
Search for memories with optional prefix filter.
- `prefix`: Filter to keys starting with prefix
- `limit`: Maximum results to return

### `delete_memory`
Delete a memory entry by key.
- `key`: The key to delete

### `list_memory_keys`
List all memory keys.
- `prefix`: Optional prefix filter
- `limit`: Maximum keys to return

## Why SlateDB?

Traditional memory servers lose data on restart. SlateDB changes that by:

1. **Writing to object storage** - S3, GCS, or MinIO
2. **Unlimited capacity** - no memory constraints
3. **Built-in durability** - object storage handles replication
4. **Perfect for long-term memory** - memories persist indefinitely

## Example Usage

```python
# Store user preferences
store_memory("user:prefs", {"theme": "dark", "language": "en"})

# Store conversation context
store_memory("conversation:123", {"topic": "SlateDB", "started": "2024-01-01"})

# Search all user memories
search_memory("user:")

# List all conversation keys
list_memory_keys("conversation:")
```

## Production Considerations

### S3 Configuration

For production deployments (e.g., FastMCP Cloud), configure S3 storage via environment variables:

```bash
SLATE_S3_BUCKET=your-bucket-name
SLATE_S3_PREFIX=production  # optional, defaults to 'slate-memory'
```

AWS credentials are loaded automatically from:
1. IAM roles (EC2, ECS, Lambda, FastMCP Cloud)
2. ~/.aws/credentials file
3. AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables

### Supported Object Storage

SlateDB supports:
- AWS S3
- Google Cloud Storage  
- MinIO
- Any S3-compatible storage

This provides true "bottomless" memory for AI assistants!

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.