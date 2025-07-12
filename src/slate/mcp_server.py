"""MCP memory server using SlateDB for persistent storage."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import slatedb
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("slate-memory")


class SlateDBMemory:
    """Memory store backed by SlateDB for persistent, bottomless storage."""

    def __init__(self, db_path: str = "./slate_memory"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)
        self.db = slatedb.SlateDB(str(self.db_path))

    def store(
        self, key: str, value: Any, metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Store a value with optional metadata."""
        entry = {
            "key": key,
            "value": value,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        # Check if key exists to preserve created_at
        existing = self.retrieve(key)
        if existing and existing.get("entry"):
            entry["created_at"] = existing["entry"]["created_at"]

        self.db.put(key.encode(), json.dumps(entry).encode())
        return entry

    def retrieve(self, key: str) -> dict[str, Any]:
        """Retrieve a value by key."""
        result = self.db.get(key.encode())
        if result:
            return {"found": True, "entry": json.loads(result.decode())}
        return {"found": False, "entry": None}

    def delete(self, key: str) -> bool:
        """Delete a value by key."""
        if self.db.get(key.encode()):
            self.db.delete(key.encode())
            return True
        return False

    def search(self, prefix: str = "", limit: int = 100) -> list[dict[str, Any]]:
        """Search for entries with optional prefix filter."""
        entries = []
        start_key = prefix.encode() if prefix else b"\x00"

        for key, value in self.db.scan(start_key):
            key_str = key.decode()

            # If we have a prefix, check if key matches
            if prefix and not key_str.startswith(prefix):
                break

            entry = json.loads(value.decode())
            entries.append(entry)

            if len(entries) >= limit:
                break

        return entries

    def close(self):
        """Close the database connection."""
        self.db.close()


# Create global memory store instance
memory = SlateDBMemory()


@mcp.tool()
def store_memory(
    key: str, value: Any, metadata: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Store a value in persistent memory.

    Args:
        key: Unique identifier for this memory
        value: The value to store (any JSON-serializable data)
        metadata: Optional metadata about this memory

    Returns:
        The stored memory entry with timestamps
    """
    try:
        entry = memory.store(key, value, metadata)
        return {
            "success": True,
            "message": f"Stored memory with key: {key}",
            "entry": entry,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def retrieve_memory(key: str) -> dict[str, Any]:
    """
    Retrieve a value from memory by key.

    Args:
        key: The key to look up

    Returns:
        The memory entry if found
    """
    result = memory.retrieve(key)
    if result["found"]:
        return {"success": True, "entry": result["entry"]}
    else:
        return {"success": False, "error": f"No memory found with key: {key}"}


@mcp.tool()
def search_memory(prefix: str = "", limit: int = 50) -> dict[str, Any]:
    """
    Search for memories with optional prefix filter.

    Args:
        prefix: Filter results to keys starting with this prefix
        limit: Maximum number of results to return

    Returns:
        List of matching memory entries
    """
    try:
        entries = memory.search(prefix, limit)
        return {"success": True, "count": len(entries), "entries": entries}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def delete_memory(key: str) -> dict[str, Any]:
    """
    Delete a memory entry by key.

    Args:
        key: The key to delete

    Returns:
        Success status
    """
    if memory.delete(key):
        return {"success": True, "message": f"Deleted memory with key: {key}"}
    else:
        return {"success": False, "error": f"No memory found with key: {key}"}


@mcp.tool()
def list_memory_keys(prefix: str = "", limit: int = 100) -> dict[str, Any]:
    """
    List all memory keys with optional prefix filter.

    Args:
        prefix: Filter results to keys starting with this prefix
        limit: Maximum number of keys to return

    Returns:
        List of memory keys
    """
    try:
        entries = memory.search(prefix, limit)
        keys = [entry["key"] for entry in entries]
        return {"success": True, "count": len(keys), "keys": keys}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # Run the MCP server
    import asyncio

    asyncio.run(mcp.run())
