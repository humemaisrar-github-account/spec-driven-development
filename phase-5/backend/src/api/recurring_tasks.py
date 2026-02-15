from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlmodel import Session
from src.database.database import get_session
from src.models.recurring_task import (
    RecurringTask, 
    RecurringTaskCreate, 
    RecurringTaskUpdate, 
    RecurringTaskRead, 
    RecurrencePattern
)
from src.services.recurring_service import RecurringTaskService

router = APIRouter(prefix="/recurring-tasks", tags=["recurring-tasks"])
recurring_service = RecurringTaskService()


@router.get("/", response_model=dict)
def get_recurring_tasks(
    is_active: Optional[bool] = Query(None),
    recurrence_pattern: Optional[RecurrencePattern] = Query(None),
    session: Session = Depends(get_session)
):
    """
    Retrieve recurring tasks with optional filtering
    """
    recurring_tasks = recurring_service.get_recurring_tasks(
        is_active=is_active,
        recurrence_pattern=recurrence_pattern
    )
    
    return {
        "recurring_tasks": recurring_tasks
    }


@router.post("/", response_model=RecurringTaskRead)
def create_recurring_task(
    recurring_task_data: RecurringTaskCreate, 
    session: Session = Depends(get_session)
):
    """
    Create a new recurring task
    """
    try:
        return recurring_service.create_recurring_task(recurring_task_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{recurring_task_id}", response_model=RecurringTaskRead)
def get_recurring_task(recurring_task_id: str, session: Session = Depends(get_session)):
    """
    Retrieve a specific recurring task by ID
    """
    recurring_task = recurring_service.get_recurring_task(recurring_task_id)
    if not recurring_task:
        raise HTTPException(status_code=404, detail="Recurring task not found")
    return recurring_task


@router.put("/{recurring_task_id}", response_model=RecurringTaskRead)
def update_recurring_task(
    recurring_task_id: str, 
    recurring_task_data: RecurringTaskUpdate, 
    session: Session = Depends(get_session)
):
    """
    Update an existing recurring task
    """
    updated_recurring_task = recurring_service.update_recurring_task(
        recurring_task_id, 
        recurring_task_data
    )
    if not updated_recurring_task:
        raise HTTPException(status_code=404, detail="Recurring task not found")
    return updated_recurring_task


@router.delete("/{recurring_task_id}")
def delete_recurring_task(recurring_task_id: str, session: Session = Depends(get_session)):
    """
    Delete a recurring task (soft delete - marks as inactive)
    """
    success = recurring_service.delete_recurring_task(recurring_task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recurring task not found")
    return {"message": "Recurring task marked as inactive"}