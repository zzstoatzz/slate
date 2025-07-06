# SlateDB Event Logger

A distributed event logging system built with SlateDB, available as both a CLI tool and an MCP (Model Context Protocol) server.

## What is SlateDB?

SlateDB is an embedded storage engine that writes directly to object storage (S3, GCS, MinIO). It provides:
- Bottomless storage capacity
- High durability through object storage
- Easy replication
- Cost-effective batched writes

Perfect for applications that need scalable, cloud-native storage with trade-offs for slightly higher latency.

## Features

The Event Logger showcases SlateDB's strengths by implementing a distributed event tracking system where multiple services can log events that are stored in object storage.

- Log events from multiple services
- Query events by service name or type
- Get event statistics
- Available as CLI or MCP server

## Installation

```bash
uv add slatedb click fastmcp
```

## Usage

### CLI Mode

Run the interactive demo:
```bash
uv run -m slate demo
```

Or use individual commands:

```bash
# Log an event
uv run -m slate log -s auth-service -t user_login -d '{"user_id": "12345"}'

# Get a specific event
uv run -m slate get "auth-service:2025-07-01T15:00:00:user_login"

# List events from a service
uv run -m slate list-service -s auth-service

# List events by type
uv run -m slate list-type -t transaction

# Simulate random events
uv run -m slate simulate
```

### MCP Server Mode

Run as an MCP server that AI assistants can use:

```bash
uv run -m slate --mcp
```

#### Available MCP Tools

- `log_event(service, event_type, data)` - Log an event
- `get_event(event_id)` - Retrieve a specific event
- `list_events(service?, event_type?, limit?)` - List events with filters
- `get_event_stats()` - Get statistics about stored events
- `clear_events(service?)` - Clear events (demo only)

#### Using with Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "slate-events": {
      "command": "uv",
      "args": ["run", "-m", "slate", "--mcp"],
      "cwd": "/path/to/slate"
    }
  }
}
```

## Why SlateDB for Event Logging?

1. **Unlimited Storage**: Events can accumulate indefinitely in object storage
2. **Durability**: Object storage provides excellent data durability
3. **Cost-Effective**: Batched writes reduce API costs
4. **Distributed**: Multiple instances can write to the same object storage backend

## Production Considerations

In production, you'd configure SlateDB to use actual object storage:
- AWS S3
- Google Cloud Storage
- MinIO
- Any S3-compatible storage

This provides true "bottomless" storage for your event logs!