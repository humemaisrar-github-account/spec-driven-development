# Data Model for Phase V Part A – Intermediate & Advanced Features

## Task Model Enhancements

### Task Entity
```python
class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: TaskStatus = Field(default=TaskStatus.PENDING)  # PENDING, IN_PROGRESS, COMPLETED
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)  # LOW, MEDIUM, HIGH
    tags: List[str] = Field(sa_column=Column(JSON))  # Max 5 tags, stored as JSON
    due_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
    
    # Relationship to recurring task if this is an instance of a recurring task
    recurring_task_id: Optional[UUID] = Field(default=None, foreign_key="recurringtask.id")
```

### Enums
```python
class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
```

## Recurring Task Model

### RecurringTask Entity
```python
class RecurringTask(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    tags: List[str] = Field(sa_column=Column(JSON))  # Max 5 tags
    recurrence_pattern: RecurrencePattern = Field(...)  # DAILY, WEEKLY, MONTHLY, CUSTOM
    custom_interval: Optional[int] = Field(default=None)  # For CUSTOM pattern (in days)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    max_instances: int = Field(default=10)  # Max future instances to create
```

### RecurrencePattern Enum
```python
class RecurrencePattern(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"
```

## Event Models

### TaskEvent Schema
```python
class TaskEvent(BaseModel):
    """Schema for task-related events published to the event stream"""
    event_id: UUID = Field(default_factory=uuid4)
    event_type: TaskEventType
    task_id: UUID
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: Dict[str, Any]  # Contains task data relevant to the event
    
class TaskEventType(Enum):
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    TASK_DELETED = "task.deleted"
    TASK_REMINDER_SCHEDULED = "task.reminder.scheduled"
    TASK_REMINDER_TRIGGERED = "task.reminder.triggered"
    RECURRING_TASK_CREATED = "recurring.task.created"
    RECURRING_TASK_INSTANCE_CREATED = "recurring.task.instance.created"
```

## Validation Rules

### Task Validation
- Title: Required, 1-255 characters
- Description: Optional, max 1000 characters
- Tags: Max 5 tags per task
- Due date: Cannot be in the past when setting/updating
- Priority: Must be one of LOW, MEDIUM, HIGH

### RecurringTask Validation
- Title: Required, 1-255 characters
- Description: Optional, max 1000 characters
- Tags: Max 5 tags per recurring task
- Recurrence pattern: Must be one of DAILY, WEEKLY, MONTHLY, CUSTOM
- Custom interval: Required when pattern is CUSTOM, positive integer
- Start date: Cannot be in the past when creating
- End date: If provided, must be after start date
- Max instances: Default 10, maximum 10 future instances allowed

## Indexes for Performance

### Task Table Indexes
- `idx_task_priority`: Index on priority field for sorting/filtering
- `idx_task_due_date`: Index on due_date field for due date filtering
- `idx_task_created_at`: Index on created_at for chronological sorting
- `idx_task_tags`: GIN index on tags array for tag-based filtering
- `idx_task_status`: Index on status for filtering by completion status

### RecurringTask Table Indexes
- `idx_recurring_task_pattern`: Index on recurrence_pattern for querying by pattern
- `idx_recurring_task_active`: Index on is_active for filtering active recurring tasks

## State Transitions

### Task State Transitions
- PENDING → IN_PROGRESS: When user starts working on task
- IN_PROGRESS → PENDING: When user pauses task
- IN_PROGRESS → COMPLETED: When user completes task
- PENDING → COMPLETED: When user completes task directly
- COMPLETED → PENDING: When user reopens completed task

### RecurringTask State Transitions
- ACTIVE → INACTIVE: When user pauses recurring task
- INACTIVE → ACTIVE: When user resumes recurring task