import asyncio
import json
from datetime import datetime, timezone
from typing import Any
from pathlib import Path

import slatedb


class EventLogger:
    def __init__(self, db_path: str = "./event_logs"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)
        
        self.db = slatedb.SlateDB(str(self.db_path))
    
    def log_event(self, service: str, event_type: str, data: dict[str, Any]) -> str:
        timestamp = datetime.now(timezone.utc)
        event_id = f"{service}:{timestamp.isoformat()}:{event_type}"
        
        event = {
            "id": event_id,
            "service": service,
            "type": event_type,
            "timestamp": timestamp.isoformat(),
            "data": data
        }
        
        self.db.put(event_id.encode(), json.dumps(event).encode())
        return event_id
    
    def get_event(self, event_id: str) -> dict[str, Any] | None:
        result = self.db.get(event_id.encode())
        if result:
            return json.loads(result.decode())
        return None
    
    def get_service_events(self, service: str, limit: int = 100) -> list[dict[str, Any]]:
        events = []
        prefix = f"{service}:"
        
        # Scan from the service prefix
        for key, value in self.db.scan(prefix.encode()):
            key_str = key.decode()
            if not key_str.startswith(prefix):
                break  # Stop when we're past our prefix
                
            event = json.loads(value.decode())
            events.append(event)
            if len(events) >= limit:
                break
        
        return events
    
    def get_events_by_type(self, event_type: str, limit: int = 100) -> list[dict[str, Any]]:
        events = []
        
        # Scan from beginning - use a minimal non-empty key
        for key, value in self.db.scan(b"\x00"):
            event = json.loads(value.decode())
            if event.get("type") == event_type:
                events.append(event)
                if len(events) >= limit:
                    break
        
        return events
    
    def close(self):
        self.db.close()


async def demo():
    logger = EventLogger()
    
    print("🚀 SlateDB Event Logger Demo\n")
    
    print("📝 Logging events from different services...")
    events = [
        ("auth-service", "user_login", {"user_id": "12345", "ip": "192.168.1.1"}),
        ("api-gateway", "request", {"path": "/api/users", "method": "GET", "status": 200}),
        ("auth-service", "user_logout", {"user_id": "12345", "session_duration": 3600}),
        ("payment-service", "transaction", {"amount": 99.99, "currency": "USD", "status": "success"}),
        ("api-gateway", "request", {"path": "/api/orders", "method": "POST", "status": 201}),
        ("auth-service", "user_login", {"user_id": "67890", "ip": "10.0.0.1"}),
    ]
    
    event_ids = []
    for service, event_type, data in events:
        event_id = logger.log_event(service, event_type, data)
        event_ids.append(event_id)
        print(f"  ✅ Logged: {service} - {event_type}")
        await asyncio.sleep(0.1)
    
    print("\n🔍 Retrieving specific event...")
    event = logger.get_event(event_ids[0])
    if event:
        print(f"  Found: {event['service']} - {event['type']} at {event['timestamp']}")
    
    print("\n📊 Getting all auth-service events...")
    auth_events = logger.get_service_events("auth-service")
    for event in auth_events:
        print(f"  - {event['type']}: user_id={event['data'].get('user_id')}")
    
    print("\n🔎 Finding all 'request' events...")
    request_events = logger.get_events_by_type("request")
    for event in request_events:
        data = event['data']
        print(f"  - {data['method']} {data['path']} -> {data['status']}")
    
    print("\n✨ SlateDB Demo Complete!")
    print("💡 In production, this would write to S3/GCS for unlimited storage!")
    
    logger.close()


if __name__ == "__main__":
    asyncio.run(demo())