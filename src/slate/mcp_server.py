"""MCP server for distributed event logging using SlateDB."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import slatedb
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("SlateDB Event Logger")


class SlateDBEventStore:
    """Event store backed by SlateDB for bottomless storage."""
    
    def __init__(self, db_path: str = "./mcp_event_logs"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)
        self.db = slatedb.SlateDB(str(self.db_path))
    
    def create_event_id(self, service: str, event_type: str) -> str:
        """Create a unique event ID."""
        timestamp = datetime.now(timezone.utc)
        return f"{service}:{timestamp.isoformat()}:{event_type}"
    
    def store_event(self, service: str, event_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """Store an event and return the complete event object."""
        event_id = self.create_event_id(service, event_type)
        
        event = {
            "id": event_id,
            "service": service,
            "type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data
        }
        
        # Store in SlateDB
        import json
        self.db.put(event_id.encode(), json.dumps(event).encode())
        
        return event
    
    def get_event(self, event_id: str) -> dict[str, Any] | None:
        """Retrieve a specific event by ID."""
        import json
        result = self.db.get(event_id.encode())
        if result:
            return json.loads(result.decode())
        return None
    
    def scan_events(self, prefix: str = "", limit: int = 100) -> list[dict[str, Any]]:
        """Scan events with optional prefix filter."""
        import json
        events = []
        
        # Use minimal key if no prefix
        start_key = prefix.encode() if prefix else b"\x00"
        
        for key, value in self.db.scan(start_key):
            key_str = key.decode()
            
            # If we have a prefix, check if key matches
            if prefix and not key_str.startswith(prefix):
                break
                
            event = json.loads(value.decode())
            events.append(event)
            
            if len(events) >= limit:
                break
                
        return events
    
    def close(self):
        """Close the database connection."""
        self.db.close()


# Create global event store instance
event_store = SlateDBEventStore()


@mcp.tool()
def log_event(service: str, event_type: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Log an event to SlateDB storage.
    
    Args:
        service: Name of the service logging the event
        event_type: Type of event (e.g., 'user_login', 'request', 'error')
        data: Optional event data as a dictionary
    
    Returns:
        The complete event object with generated ID and timestamp
    """
    if data is None:
        data = {}
    
    event = event_store.store_event(service, event_type, data)
    return {
        "status": "success",
        "event": event
    }


@mcp.tool()
def get_event(event_id: str) -> dict[str, Any]:
    """
    Retrieve a specific event by its ID.
    
    Args:
        event_id: The unique event ID
    
    Returns:
        The event object if found, or an error message
    """
    event = event_store.get_event(event_id)
    
    if event:
        return {
            "status": "success",
            "event": event
        }
    else:
        return {
            "status": "error",
            "message": f"Event not found: {event_id}"
        }


@mcp.tool()
def list_events(
    service: str | None = None,
    event_type: str | None = None,
    limit: int = 50
) -> dict[str, Any]:
    """
    List events with optional filtering.
    
    Args:
        service: Filter by service name (optional)
        event_type: Filter by event type (optional)
        limit: Maximum number of events to return (default: 50)
    
    Returns:
        List of matching events
    """
    # If filtering by service, use prefix scan
    if service:
        prefix = f"{service}:"
        events = event_store.scan_events(prefix, limit)
    else:
        # Scan all events
        events = event_store.scan_events("", limit * 2)  # Get more to filter
    
    # Apply event_type filter if specified
    if event_type:
        events = [e for e in events if e.get("type") == event_type][:limit]
    else:
        events = events[:limit]
    
    return {
        "status": "success",
        "count": len(events),
        "events": events
    }


@mcp.tool()
def get_event_stats() -> dict[str, Any]:
    """
    Get statistics about stored events.
    
    Returns:
        Statistics including service counts and event type distribution
    """
    # Scan all events for statistics
    all_events = event_store.scan_events("", 1000)
    
    service_counts: dict[str, int] = {}
    type_counts: dict[str, int] = {}
    
    for event in all_events:
        service = event.get("service", "unknown")
        event_type = event.get("type", "unknown")
        
        service_counts[service] = service_counts.get(service, 0) + 1
        type_counts[event_type] = type_counts.get(event_type, 0) + 1
    
    return {
        "status": "success",
        "total_events": len(all_events),
        "services": service_counts,
        "event_types": type_counts
    }


@mcp.tool()
def clear_events(service: str | None = None) -> dict[str, Any]:
    """
    Clear events from the store.
    
    Args:
        service: If specified, only clear events from this service
    
    Returns:
        Status and count of cleared events
    """
    # Note: SlateDB doesn't have bulk delete, so we'd need to track keys
    # For this demo, we'll just report what would be cleared
    
    if service:
        prefix = f"{service}:"
        events = event_store.scan_events(prefix, 1000)
        message = f"Would clear {len(events)} events from service '{service}'"
    else:
        events = event_store.scan_events("", 1000)
        message = f"Would clear all {len(events)} events"
    
    # In production, you'd iterate and delete each key
    # For demo purposes, we'll just return the count
    
    return {
        "status": "info",
        "message": message,
        "note": "Bulk delete not implemented in this demo"
    }


# Note: FastMCP handles cleanup automatically
# If needed in the future, we could add cleanup hooks


if __name__ == "__main__":
    # Run the MCP server
    import asyncio
    asyncio.run(mcp.run())