from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON
import uuid
from enum import Enum


class RecurrencePattern(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class RecurringTaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: str = Field(default="medium")  # Using string since we'll reference TaskPriority
    tags: List[str] = Field(default=[], sa_column=Column(JSON))
    recurrence_pattern: RecurrencePattern = Field(...)
    custom_interval: Optional[int] = Field(default=None)  # For CUSTOM pattern (in days)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)
    max_instances: int = Field(default=10)  # Max future instances to create


class RecurringTask(RecurringTaskBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class RecurringTaskCreate(RecurringTaskBase):
    pass


class RecurringTaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: Optional[str] = Field(default=None)  # Using string since we'll reference TaskPriority
    tags: Optional[List[str]] = Field(default=None)
    recurrence_pattern: Optional[RecurrencePattern] = None
    custom_interval: Optional[int] = Field(default=None)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    is_active: Optional[bool] = None
    max_instances: Optional[int] = Field(default=None)


class RecurringTaskRead(RecurringTaskBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime