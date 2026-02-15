---
name: async-dapr-client-service-coder
description: Generate Python code snippets for Dapr integration including HTTP calls, Pydantic models, async FastAPI endpoints, and microservice skeletons. Create production-ready async Python code that leverages Dapr for pubsub, state management, service invocation, and Jobs API.
---

# Async Dapr Client & Service Coder

## Overview
Generate Python code snippets for Dapr integration including HTTP calls, Pydantic models, async FastAPI endpoints, and microservice skeletons for Phase 5 event-driven microservices applications.

## Core Components

### 1. Dapr HTTP Client Module
Async client for interacting with Dapr sidecar.

```python
# services/common/dapr_client.py
import httpx
import json
from typing import Any, Dict, Optional
from pydantic import BaseModel


class DaprClient:
    def __init__(self, dapr_http_port: int = 3500, dapr_host: str = "localhost"):
        self.dapr_base_url = f"http://{dapr_host}:{dapr_http_port}"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def publish_event(self, pubsub_name: str, topic_name: str, data: Dict[str, Any]) -> None:
        """Publish an event to a Dapr pubsub topic."""
        url = f"{self.dapr_base_url}/v1.0/publish/{pubsub_name}/{topic_name}"
        response = await self.client.post(url, json=data)
        response.raise_for_status()

    async def save_state(self, store_name: str, key: str, value: Any) -> None:
        """Save state to a Dapr state store."""
        url = f"{self.dapr_base_url}/v1.0/state/{store_name}"
        state_item = {
            "key": key,
            "value": value
        }
        response = await self.client.post(url, json=[state_item])
        response.raise_for_status()

    async def get_state(self, store_name: str, key: str) -> Any:
        """Get state from a Dapr state store."""
        url = f"{self.dapr_base_url}/v1.0/state/{store_name}/{key}"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def delete_state(self, store_name: str, key: str) -> None:
        """Delete state from a Dapr state store."""
        url = f"{self.dapr_base_url}/v1.0/state/{store_name}/{key}"
        response = await self.client.delete(url)
        response.raise_for_status()

    async def invoke_service(self, app_id: str, method: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """Invoke a method on another Dapr-enabled service."""
        url = f"{self.dapr_base_url}/v1.0/invoke/{app_id}/method/{method}"
        if data:
            response = await self.client.post(url, json=data)
        else:
            response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def schedule_job(self, job_name: str, due_time: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Schedule a job using Dapr Jobs API."""
        url = f"{self.dapr_base_url}/v1.0-alpha1/jobs/{job_name}"
        payload = {
            "dueTime": due_time,
            "data": data
        }
        response = await self.client.post(url, json=payload)
        response.raise_for_status()

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
```

### 2. Pydantic Models for Events
Data models for consistent event structures.

```python
# common/events.py
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel


class TaskEventType(str, Enum):
    CREATED = "task_created"
    UPDATED = "task_updated"
    COMPLETED = "task_completed"
    DELETED = "task_deleted"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskEvent(BaseModel):
    event_type: TaskEventType
    task_id: str
    user_id: str
    timestamp: datetime
    task_data: Dict[str, Any]


class ReminderEvent(BaseModel):
    task_id: str
    title: str
    due_at: datetime
    remind_at: datetime
    user_id: str
    priority: Priority = Priority.MEDIUM
    tags: Optional[list[str]] = None
```

### 3. Async FastAPI Endpoints
Example endpoints for Dapr integration.

```python
# services/api/endpoints.py
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import asyncio
from common.events import TaskEvent, ReminderEvent, TaskEventType
from services.common.dapr_client import DaprClient

router = APIRouter()


@router.post("/api/jobs/trigger")
async def handle_job_trigger(data: Dict[str, Any]):
    """Handle Dapr Jobs API callback."""
    # Process the scheduled job
    job_name = data.get("job_name", "unknown")
    job_data = data.get("data", {})
    
    # Example: Process reminder notification
    if job_name == "reminder_notification":
        reminder_event = ReminderEvent(**job_data)
        # Send notification logic here
        print(f"Processing reminder for task {reminder_event.task_id}")
        
    return {"status": "processed", "job": job_name}


@router.post("/api/tasks")
async def create_task(task_data: Dict[str, Any]):
    """Create a new task and publish event."""
    dapr_client = DaprClient()
    
    try:
        # Create task event
        task_event = TaskEvent(
            event_type=TaskEventType.CREATED,
            task_id=task_data.get("id"),
            user_id=task_data.get("user_id"),
            timestamp=datetime.utcnow(),
            task_data=task_data
        )
        
        # Publish to pubsub
        await dapr_client.publish_event("pubsub-kafka", "task-events", task_event.dict())
        
        # Save to state store
        await dapr_client.save_state("state-postgresql", f"task:{task_data.get('id')}", task_data)
        
        return {"status": "created", "task_id": task_data.get("id")}
    finally:
        await dapr_client.close()


@router.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """Get a task from state store."""
    dapr_client = DaprClient()
    
    try:
        task_data = await dapr_client.get_state("state-postgresql", f"task:{task_id}")
        return {"task": task_data}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    finally:
        await dapr_client.close()
```

## Microservice Skeletons

### 1. RecurringTaskService Skeleton

```python
# services/recurring/main.py
import asyncio
import logging
from datetime import datetime, timedelta
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
from common.events import TaskEvent, TaskEventType, ReminderEvent
from services.common.dapr_client import DaprClient


app = FastAPI(title="RecurringTaskService", version="1.0.0")
logger = logging.getLogger(__name__)


class RecurringTaskRequest(BaseModel):
    original_task_id: str
    user_id: str
    recurrence_pattern: str  # daily, weekly, monthly
    next_due_date: datetime


@app.post("/api/recurring/process-completion")
async def process_task_completion(event: TaskEvent):
    """Process task completion and create next instance if recurring."""
    if event.event_type != TaskEventType.COMPLETED:
        return {"status": "ignored", "reason": "not a completion event"}
    
    # Check if task is recurring
    dapr_client = DaprClient()
    try:
        task_state = await dapr_client.get_state("state-postgresql", f"task:{event.task_id}")
        
        if task_state.get("is_recurring"):
            # Create next instance
            next_task = create_next_instance(task_state)
            
            # Publish event for new task
            new_task_event = TaskEvent(
                event_type=TaskEventType.CREATED,
                task_id=next_task["id"],
                user_id=event.user_id,
                timestamp=datetime.utcnow(),
                task_data=next_task
            )
            
            await dapr_client.publish_event("pubsub-kafka", "task-events", new_task_event.dict())
            
            # Schedule reminder if needed
            if next_task.get("remind_at"):
                reminder_event = ReminderEvent(
                    task_id=next_task["id"],
                    title=next_task["title"],
                    due_at=next_task["due_at"],
                    remind_at=next_task["remind_at"],
                    user_id=event.user_id
                )
                
                await dapr_client.schedule_job(
                    f"reminder-{next_task['id']}",
                    due_time=next_task["remind_at"].isoformat(),
                    data=reminder_event.dict()
                )
            
            logger.info(f"Created next instance for recurring task {event.task_id}")
            return {"status": "next_instance_created", "new_task_id": next_task["id"]}
        else:
            return {"status": "non_recurring", "task_id": event.task_id}
    finally:
        await dapr_client.close()


def create_next_instance(original_task: Dict[str, Any]) -> Dict[str, Any]:
    """Create the next instance of a recurring task."""
    recurrence_pattern = original_task.get("recurrence_pattern", "daily")
    current_due_date = original_task.get("due_at")
    
    if recurrence_pattern == "daily":
        next_due_date = current_due_date + timedelta(days=1)
    elif recurrence_pattern == "weekly":
        next_due_date = current_due_date + timedelta(weeks=1)
    elif recurrence_pattern == "monthly":
        # Simple monthly calculation (same day next month)
        next_due_date = current_due_date + timedelta(days=30)
    else:
        # Default to daily
        next_due_date = current_due_date + timedelta(days=1)
    
    # Create new task with incremented ID
    new_task_id = f"{original_task['id']}-next-{int(datetime.utcnow().timestamp())}"
    
    new_task = original_task.copy()
    new_task["id"] = new_task_id
    new_task["due_at"] = next_due_date
    new_task["completed"] = False
    new_task["created_at"] = datetime.utcnow()
    
    return new_task


@app.on_event('startup')
async def startup_event():
    logging.basicConfig(level=logging.INFO)
    logger.info("RecurringTaskService started")


@app.on_event('shutdown')
async def shutdown_event():
    logger.info("RecurringTaskService shutting down")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "RecurringTaskService"}
```

```txt
# services/recurring/requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.2
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
dapr==1.11.0
```

### 2. NotificationService Skeleton

```python
# services/notification/main.py
import asyncio
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from typing import Dict, Any
from common.events import ReminderEvent
from services.common.dapr_client import DaprClient


app = FastAPI(title="NotificationService", version="1.0.0")
logger = logging.getLogger(__name__)


@app.post("/api/reminders/process")
async def process_reminder(reminder: ReminderEvent):
    """Process reminder and send notification."""
    try:
        # Simulate sending notification
        await send_notification(reminder)
        
        # Publish notification sent event
        dapr_client = DaprClient()
        try:
            notification_event = {
                "event_type": "notification_sent",
                "task_id": reminder.task_id,
                "user_id": reminder.user_id,
                "timestamp": datetime.utcnow(),
                "notification_type": "reminder",
                "title": reminder.title
            }
            
            await dapr_client.publish_event("pubsub-kafka", "task-updates", notification_event)
        finally:
            await dapr_client.close()
        
        logger.info(f"Sent reminder notification for task {reminder.task_id}")
        return {"status": "sent", "task_id": reminder.task_id}
    except Exception as e:
        logger.error(f"Failed to send reminder for task {reminder.task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def send_notification(reminder: ReminderEvent):
    """Send actual notification (email, SMS, push, etc.)."""
    # Placeholder for actual notification logic
    # This could send email, SMS, push notification, etc.
    print(f"Sending reminder: {reminder.title} for user {reminder.user_id}")
    
    # Simulate async notification sending
    await asyncio.sleep(0.1)


@app.post("/api/notifications/send")
async def send_custom_notification(notification_data: Dict[str, Any]):
    """Send custom notification."""
    try:
        # Process notification data
        user_id = notification_data.get("user_id")
        message = notification_data.get("message")
        notification_type = notification_data.get("type", "info")
        
        # Send notification
        await send_custom_notification_impl(user_id, message, notification_type)
        
        # Log notification
        dapr_client = DaprClient()
        try:
            notification_log = {
                "event_type": "custom_notification_sent",
                "user_id": user_id,
                "timestamp": datetime.utcnow(),
                "message": message,
                "type": notification_type
            }
            
            await dapr_client.publish_event("pubsub-kafka", "task-updates", notification_log)
        finally:
            await dapr_client.close()
        
        return {"status": "sent", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def send_custom_notification_impl(user_id: str, message: str, notification_type: str):
    """Implementation for sending custom notifications."""
    print(f"Sending {notification_type} notification to user {user_id}: {message}")
    await asyncio.sleep(0.1)  # Simulate async operation


@app.on_event('startup')
async def startup_event():
    logging.basicConfig(level=logging.INFO)
    logger.info("NotificationService started")


@app.on_event('shutdown')
async def shutdown_event():
    logger.info("NotificationService shutting down")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "NotificationService"}
```

```txt
# services/notification/requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.2
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
dapr==1.11.0
aiofiles==23.2.1
```

## Common Utilities

### 1. Async Context Manager for Dapr Client

```python
# services/common/dapr_context.py
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from services.common.dapr_client import DaprClient


@asynccontextmanager
async def dapr_client_context() -> AsyncGenerator[DaprClient, None]:
    """Async context manager for Dapr client."""
    client = DaprClient()
    try:
        yield client
    finally:
        await client.close()
```

### 2. Error Handling Utilities

```python
# services/common/errors.py
from typing import Optional
from fastapi import HTTPException


class DaprServiceError(Exception):
    """Base exception for Dapr service errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class StateNotFoundError(DaprServiceError):
    """Raised when state is not found in Dapr state store."""
    def __init__(self, key: str):
        super().__init__(f"State not found for key: {key}", 404)


class PubSubPublishError(DaprServiceError):
    """Raised when publishing to pubsub fails."""
    def __init__(self, topic: str, error_details: Optional[str] = None):
        message = f"Failed to publish to topic '{topic}'"
        if error_details:
            message += f": {error_details}"
        super().__init__(message, 500)
```

## Usage Examples

### 1. Using Dapr Client in Services

```python
# example_usage.py
from services.common.dapr_client import DaprClient
from common.events import TaskEvent, TaskEventType
import asyncio
from datetime import datetime


async def example_usage():
    dapr_client = DaprClient()
    
    try:
        # Publish a task event
        task_event = TaskEvent(
            event_type=TaskEventType.CREATED,
            task_id="task-123",
            user_id="user-456",
            timestamp=datetime.utcnow(),
            task_data={"title": "Sample Task", "priority": "high"}
        )
        
        await dapr_client.publish_event("pubsub-kafka", "task-events", task_event.dict())
        print("Published task event")
        
        # Save state
        await dapr_client.save_state("state-postgresql", "user:user-456", {"name": "John Doe"})
        print("Saved user state")
        
        # Get state
        user_data = await dapr_client.get_state("state-postgresql", "user:user-456")
        print(f"Retrieved user data: {user_data}")
        
        # Invoke another service
        result = await dapr_client.invoke_service("notification-service", "send-welcome-email", {
            "user_id": "user-456",
            "email": "john@example.com"
        })
        print(f"Service invocation result: {result}")
        
    finally:
        await dapr_client.close()


if __name__ == "__main__":
    asyncio.run(example_usage())
```

## Best Practices

### 1. Async Programming
- Always use `async def` for I/O-bound operations
- Use `await` for Dapr client calls
- Properly close HTTP clients to prevent resource leaks

### 2. Error Handling
- Wrap Dapr calls in try/finally blocks to ensure client closure
- Handle specific Dapr-related exceptions
- Implement retry logic for transient failures

### 3. Security
- Never hardcode credentials in code
- Use Dapr secrets for sensitive data
- Validate input data before processing

### 4. Performance
- Use connection pooling with httpx.AsyncClient
- Implement caching for frequently accessed data
- Use background tasks for non-blocking operations

## Testing Considerations

### 1. Mock Dapr Client for Unit Tests
```python
# test_dapr_client.py
import pytest
from unittest.mock import AsyncMock
from services.common.dapr_client import DaprClient


@pytest.fixture
def mock_dapr_client():
    client = DaprClient()
    client.client = AsyncMock()
    return client


@pytest.mark.asyncio
async def test_publish_event(mock_dapr_client):
    await mock_dapr_client.publish_event("pubsub", "topic", {"data": "test"})
    assert mock_dapr_client.client.post.called
```

This skill provides a complete foundation for building async Dapr-integrated microservices with proper error handling, testing considerations, and best practices.