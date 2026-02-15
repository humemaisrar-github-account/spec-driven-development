from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlmodel import Session
from src.database.database import get_session
from src.models.task import Task, TaskCreate, TaskUpdate, TaskRead, TaskPriority, TaskStatus
from src.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])
task_service = TaskService()


@router.get("/", response_model=dict)
def get_tasks(
    priority: Optional[TaskPriority] = Query(None),
    tags: Optional[List[str]] = Query(None),
    due_date_from: Optional[str] = Query(None),
    due_date_to: Optional[str] = Query(None),
    without_due_date: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    sort_order: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(100),
    session: Session = Depends(get_session)
):
    """
    Retrieve tasks with optional filtering, sorting, and search capabilities
    """
    from datetime import datetime
    
    # Convert date strings to datetime objects if provided
    due_date_from_dt = datetime.fromisoformat(due_date_from) if due_date_from else None
    due_date_to_dt = datetime.fromisoformat(due_date_to) if due_date_to else None
    
    tasks = task_service.get_tasks(
        priority=priority,
        tags=tags,
        due_date_from=due_date_from_dt,
        due_date_to=due_date_to_dt,
        without_due_date=without_due_date,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit
    )
    
    # Simple pagination implementation
    total = len(tasks)  # In a real implementation, this would be a count query
    pages = (total + limit - 1) // limit
    
    return {
        "tasks": tasks,
        "pagination": {
            "page": skip // limit + 1,
            "size": limit,
            "total": total,
            "pages": pages
        }
    }


@router.post("/", response_model=TaskRead)
def create_task(task_data: TaskCreate, session: Session = Depends(get_session)):
    """
    Create a new task with advanced features
    """
    try:
        return task_service.create_task(task_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: str, session: Session = Depends(get_session)):
    """
    Retrieve a specific task by ID
    """
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskRead)
def update_task(task_id: str, task_data: TaskUpdate, session: Session = Depends(get_session)):
    """
    Update an existing task with advanced features
    """
    updated_task = task_service.update_task(task_id, task_data)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task


@router.delete("/{task_id}")
def delete_task(task_id: str, session: Session = Depends(get_session)):
    """
    Delete a task by ID
    """
    success = task_service.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}


@router.patch("/{task_id}/complete", response_model=TaskRead)
def mark_task_complete(task_id: str, session: Session = Depends(get_session)):
    """
    Mark a task as completed
    """
    task = task_service.mark_task_completed(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task