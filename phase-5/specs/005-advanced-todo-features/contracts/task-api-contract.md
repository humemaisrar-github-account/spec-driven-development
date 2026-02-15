# Task API Contracts for Advanced Features

## Task Operations with Advanced Features

### GET /tasks
**Description**: Retrieve tasks with optional filtering, sorting, and search capabilities
**Parameters**:
- `priority` (optional): Filter by priority level (low, medium, high)
- `tags` (optional): Filter by tags (comma-separated list)
- `due_date_from` (optional): Filter tasks with due date >= this date
- `due_date_to` (optional): Filter tasks with due date <= this date
- `without_due_date` (optional): Filter tasks without due dates (true/false)
- `search` (optional): Full-text search on title and description
- `sort_by` (optional): Sort by field (due_date, priority, created_at, title)
- `sort_order` (optional): Sort order (asc, desc)
- `page` (optional): Page number for pagination
- `size` (optional): Page size for pagination

**Response**: 
```json
{
  "tasks": [
    {
      "id": "uuid",
      "title": "string",
      "description": "string",
      "status": "pending|in_progress|completed",
      "priority": "low|medium|high",
      "tags": ["string"],
      "due_date": "datetime",
      "created_at": "datetime",
      "updated_at": "datetime",
      "completed_at": "datetime"
    }
  ],
  "pagination": {
    "page": "int",
    "size": "int",
    "total": "int",
    "pages": "int"
  }
}
```

### POST /tasks
**Description**: Create a new task with advanced features
**Request Body**:
```json
{
  "title": "string (required)",
  "description": "string (optional)",
  "priority": "low|medium|high (default: medium)",
  "tags": ["string (max 5)"],
  "due_date": "datetime (optional)"
}
```

**Response**:
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "status": "pending",
  "priority": "low|medium|high",
  "tags": ["string"],
  "due_date": "datetime",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### PUT /tasks/{task_id}
**Description**: Update an existing task with advanced features
**Request Body**:
```json
{
  "title": "string (optional)",
  "description": "string (optional)",
  "priority": "low|medium|high (optional)",
  "tags": ["string (max 5) (optional)"],
  "due_date": "datetime (optional)",
  "status": "pending|in_progress|completed (optional)"
}
```

**Response**:
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "status": "pending|in_progress|completed",
  "priority": "low|medium|high",
  "tags": ["string"],
  "due_date": "datetime",
  "created_at": "datetime",
  "updated_at": "datetime",
  "completed_at": "datetime"
}
```

## Recurring Task Operations

### GET /recurring-tasks
**Description**: Retrieve recurring tasks
**Parameters**:
- `is_active` (optional): Filter by active/inactive status (true/false)
- `recurrence_pattern` (optional): Filter by pattern (daily, weekly, monthly, custom)

**Response**:
```json
{
  "recurring_tasks": [
    {
      "id": "uuid",
      "title": "string",
      "description": "string",
      "priority": "low|medium|high",
      "tags": ["string"],
      "recurrence_pattern": "daily|weekly|monthly|custom",
      "custom_interval": "integer (days, for custom pattern)",
      "start_date": "datetime",
      "end_date": "datetime",
      "created_at": "datetime",
      "updated_at": "datetime",
      "is_active": "boolean",
      "max_instances": "integer"
    }
  ]
}
```

### POST /recurring-tasks
**Description**: Create a new recurring task
**Request Body**:
```json
{
  "title": "string (required)",
  "description": "string (optional)",
  "priority": "low|medium|high (default: medium)",
  "tags": ["string (max 5)"],
  "recurrence_pattern": "daily|weekly|monthly|custom",
  "custom_interval": "integer (required if pattern is custom)",
  "start_date": "datetime (optional)",
  "end_date": "datetime (optional)",
  "max_instances": "integer (default: 10)"
}
```

**Response**:
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "priority": "low|medium|high",
  "tags": ["string"],
  "recurrence_pattern": "daily|weekly|monthly|custom",
  "custom_interval": "integer",
  "start_date": "datetime",
  "end_date": "datetime",
  "created_at": "datetime",
  "updated_at": "datetime",
  "is_active": "boolean",
  "max_instances": "integer"
}
```

### PUT /recurring-tasks/{recurring_task_id}
**Description**: Update an existing recurring task
**Request Body**:
```json
{
  "title": "string (optional)",
  "description": "string (optional)",
  "priority": "low|medium|high (optional)",
  "tags": ["string (max 5) (optional)"],
  "recurrence_pattern": "daily|weekly|monthly|custom (optional)",
  "custom_interval": "integer (optional)",
  "start_date": "datetime (optional)",
  "end_date": "datetime (optional)",
  "is_active": "boolean (optional)",
  "max_instances": "integer (optional)"
}
```

**Response**:
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "priority": "low|medium|high",
  "tags": ["string"],
  "recurrence_pattern": "daily|weekly|monthly|custom",
  "custom_interval": "integer",
  "start_date": "datetime",
  "end_date": "datetime",
  "created_at": "datetime",
  "updated_at": "datetime",
  "is_active": "boolean",
  "max_instances": "integer"
}
```

### DELETE /recurring-tasks/{recurring_task_id}
**Description**: Delete a recurring task (soft delete - marks as inactive)
**Response**: 204 No Content