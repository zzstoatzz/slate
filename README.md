# SlateDB Event Logger Demo

A simple distributed event logging system built with SlateDB to demonstrate its cloud-native storage capabilities.

## What is SlateDB?

SlateDB is an embedded storage engine that writes directly to object storage (S3, GCS, MinIO). It provides:
- Bottomless storage capacity
- High durability through object storage
- Easy replication
- Cost-effective batched writes

Perfect for applications that need scalable, cloud-native storage with trade-offs for slightly higher latency.

## This Demo

The Event Logger showcases SlateDB's strengths by implementing a distributed event tracking system where multiple services can log events that are stored in object storage.

### Features

- Log events from multiple services
- Query events by service name
- Filter events by type
- Simple CLI interface

### Installation

```bash
uv add slatedb click
```

### Usage

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

### Why SlateDB for Event Logging?

1. **Unlimited Storage**: Events can accumulate indefinitely in object storage
2. **Durability**: Object storage provides excellent data durability
3. **Cost-Effective**: Batched writes reduce API costs
4. **Distributed**: Multiple instances can write to the same object storage backend

### Production Considerations

In production, you'd configure SlateDB to use actual object storage:
- AWS S3
- Google Cloud Storage
- MinIO
- Any S3-compatible storage

This provides true "bottomless" storage for your event logs!