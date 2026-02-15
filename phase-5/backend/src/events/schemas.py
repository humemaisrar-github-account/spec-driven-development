from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum
import uuid


class TaskEventType(str, Enum):
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    TASK_DELETED = "task.deleted"
    TASK_REMINDER_SCHEDULED = "task.reminder.scheduled"
    TASK_REMINDER_TRIGGERED = "task.reminder.triggered"
    RECURRING_TASK_CREATED = "recurring.task.created"
    RECURRING_TASK_INSTANCE_CREATED = "recurring.task.instance.created"


class TaskEvent(BaseModel):
    """Schema for task-related events published to the event stream"""
    event_id: uuid.UUID
    event_type: TaskEventType
    task_id: uuid.UUID
    timestamp: datetime = datetime.utcnow()
    payload: Dict[str, Any]  # Contains task data relevant to the event


class RecurringTaskEvent(BaseModel):
    """Schema for recurring task-related events"""
    event_id: uuid.UUID
    event_type: TaskEventType
    recurring_task_id: uuid.UUID
    timestamp: datetime = datetime.utcnow()
    payload: Dict[str, Any]  # Contains recurring task data relevant to the event