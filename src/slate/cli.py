import asyncio
import json
from datetime import datetime, timezone
import click

from .event_logger import EventLogger


@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = EventLogger()


@cli.command()
@click.option('--service', '-s', required=True, help='Service name')
@click.option('--type', '-t', 'event_type', required=True, help='Event type')
@click.option('--data', '-d', help='Event data as JSON string', default='{}')
@click.pass_obj
def log(logger: EventLogger, service: str, event_type: str, data: str):
    try:
        event_data = json.loads(data)
    except json.JSONDecodeError:
        click.echo("❌ Invalid JSON data", err=True)
        return
    
    event_id = logger.log_event(service, event_type, event_data)
    click.echo(f"✅ Event logged: {event_id}")


@cli.command()
@click.argument('event_id')
@click.pass_obj
def get(logger: EventLogger, event_id: str):
    event = logger.get_event(event_id)
    if event:
        click.echo(json.dumps(event, indent=2))
    else:
        click.echo(f"❌ Event not found: {event_id}", err=True)


@cli.command()
@click.option('--service', '-s', required=True, help='Service name')
@click.option('--limit', '-l', default=10, help='Maximum events to return')
@click.pass_obj
def list_service(logger: EventLogger, service: str, limit: int):
    events = logger.get_service_events(service, limit)
    
    if not events:
        click.echo(f"No events found for service: {service}")
        return
    
    click.echo(f"\n📊 Events for {service} (limit: {limit}):\n")
    for event in events:
        timestamp = event['timestamp']
        event_type = event['type']
        data = json.dumps(event['data'], separators=(',', ':'))
        click.echo(f"  [{timestamp}] {event_type}: {data}")


@cli.command()
@click.option('--type', '-t', 'event_type', required=True, help='Event type to filter')
@click.option('--limit', '-l', default=10, help='Maximum events to return')
@click.pass_obj
def list_type(logger: EventLogger, event_type: str, limit: int):
    events = logger.get_events_by_type(event_type, limit)
    
    if not events:
        click.echo(f"No events found of type: {event_type}")
        return
    
    click.echo(f"\n🔎 Events of type '{event_type}' (limit: {limit}):\n")
    for event in events:
        service = event['service']
        timestamp = event['timestamp']
        data = json.dumps(event['data'], separators=(',', ':'))
        click.echo(f"  [{service}] {timestamp}: {data}")


@cli.command()
@click.pass_obj
def demo(logger: EventLogger):
    asyncio.run(_run_demo())


async def _run_demo():
    from .event_logger import demo
    await demo()


@cli.command()
@click.pass_obj
def simulate(logger: EventLogger):
    import random
    
    services = ["auth-service", "api-gateway", "payment-service", "notification-service"]
    event_types = {
        "auth-service": ["user_login", "user_logout", "password_reset", "token_refresh"],
        "api-gateway": ["request", "rate_limit", "error"],
        "payment-service": ["transaction", "refund", "subscription", "payment_failed"],
        "notification-service": ["email_sent", "sms_sent", "push_notification"]
    }
    
    click.echo("🎲 Simulating random events...\n")
    
    for _ in range(20):
        service = random.choice(services)
        event_type = random.choice(event_types[service])
        
        data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "random_id": random.randint(1000, 9999)
        }
        
        if service == "auth-service":
            data["user_id"] = f"user_{random.randint(100, 999)}"
        elif service == "api-gateway":
            data["path"] = random.choice(["/api/users", "/api/orders", "/api/products"])
            data["method"] = random.choice(["GET", "POST", "PUT", "DELETE"])
            data["status"] = random.choice([200, 201, 400, 401, 404, 500])
        elif service == "payment-service":
            data["amount"] = round(random.uniform(10, 1000), 2)
            data["currency"] = random.choice(["USD", "EUR", "GBP"])
        
        event_id = logger.log_event(service, event_type, data)
        click.echo(f"  ✅ {service}: {event_type}")
    
    click.echo("\n✨ Simulation complete! Use 'list-service' or 'list-type' to query events.")


if __name__ == '__main__':
    cli()