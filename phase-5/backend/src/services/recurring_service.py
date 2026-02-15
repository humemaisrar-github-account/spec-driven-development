import logging
from datetime import datetime
from typing import List, Optional
from sqlmodel import Session, select
from src.models.recurring_task import (
    RecurringTask, 
    RecurringTaskCreate, 
    RecurringTaskUpdate, 
    RecurrencePattern
)
from src.database.database import engine

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecurringTaskService:
    def create_recurring_task(self, recurring_task_data: RecurringTaskCreate) -> RecurringTask:
        """Create a new recurring task"""
        logger.info(f"Creating recurring task with title: {recurring_task_data.title}, pattern: {recurring_task_data.recurrence_pattern}")
        
        with Session(engine) as session:
            # Validate max 5 tags
            if len(recurring_task_data.tags) > 5:
                logger.warning(f"Attempted to create recurring task with more than 5 tags: {len(recurring_task_data.tags)} tags provided")
                raise ValueError("Maximum 5 tags allowed per recurring task")
            
            # Validate custom interval if pattern is CUSTOM
            if (recurring_task_data.recurrence_pattern == RecurrencePattern.CUSTOM and 
                not recurring_task_data.custom_interval):
                logger.error("Custom interval is required for CUSTOM recurrence pattern")
                raise ValueError("Custom interval is required for CUSTOM recurrence pattern")
            
            db_recurring_task = RecurringTask.model_validate(recurring_task_data)
            session.add(db_recurring_task)
            session.commit()
            session.refresh(db_recurring_task)
            logger.info(f"Recurring task created successfully with ID: {db_recurring_task.id}")
            return db_recurring_task

    def get_recurring_task(self, recurring_task_id: str) -> Optional[RecurringTask]:
        """Retrieve a recurring task by ID"""
        with Session(engine) as session:
            statement = select(RecurringTask).where(RecurringTask.id == recurring_task_id)
            return session.exec(statement).first()

    def get_recurring_tasks(
        self, 
        is_active: Optional[bool] = None, 
        recurrence_pattern: Optional[RecurrencePattern] = None
    ) -> List[RecurringTask]:
        """Retrieve recurring tasks with optional filtering"""
        with Session(engine) as session:
            statement = select(RecurringTask)
            
            # Apply filters
            if is_active is not None:
                statement = statement.where(RecurringTask.is_active == is_active)
                
            if recurrence_pattern:
                statement = statement.where(RecurringTask.recurrence_pattern == recurrence_pattern)
            
            return session.exec(statement).all()

    def update_recurring_task(
        self, 
        recurring_task_id: str, 
        recurring_task_data: RecurringTaskUpdate
    ) -> Optional[RecurringTask]:
        """Update an existing recurring task"""
        logger.info(f"Updating recurring task {recurring_task_id}")
        
        with Session(engine) as session:
            db_recurring_task = session.get(RecurringTask, recurring_task_id)
            if not db_recurring_task:
                logger.warning(f"Attempted to update non-existent recurring task: {recurring_task_id}")
                return None
            
            # Validate max 5 tags if updating tags
            if (recurring_task_data.tags is not None and 
                len(recurring_task_data.tags) > 5):
                logger.warning(f"Attempted to update recurring task {recurring_task_id} with more than 5 tags: {len(recurring_task_data.tags)} tags provided")
                raise ValueError("Maximum 5 tags allowed per recurring task")
            
            # Validate custom interval if updating pattern to CUSTOM
            if (recurring_task_data.recurrence_pattern == RecurrencePattern.CUSTOM and 
                not recurring_task_data.custom_interval):
                logger.error(f"Custom interval is required for CUSTOM recurrence pattern when updating recurring task {recurring_task_id}")
                raise ValueError("Custom interval is required for CUSTOM recurrence pattern")
            
            # Update fields
            update_data = recurring_task_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_recurring_task, field, value)
            
            # Update timestamps
            db_recurring_task.updated_at = datetime.utcnow()
            
            session.add(db_recurring_task)
            session.commit()
            session.refresh(db_recurring_task)
            logger.info(f"Recurring task {recurring_task_id} updated successfully")
            return db_recurring_task

    def delete_recurring_task(self, recurring_task_id: str) -> bool:
        """Soft delete a recurring task (mark as inactive)"""
        with Session(engine) as session:
            db_recurring_task = session.get(RecurringTask, recurring_task_id)
            if not db_recurring_task:
                return False
            
            db_recurring_task.is_active = False
            db_recurring_task.updated_at = datetime.utcnow()
            
            session.add(db_recurring_task)
            session.commit()
            return True

    def create_next_instance(self, recurring_task_id: str) -> Optional[str]:
        """Create the next instance of a recurring task based on its pattern"""
        from src.models.task import TaskCreate, TaskPriority, TaskStatus
        from src.services.task_service import TaskService
        from sqlmodel import select
        from src.models.task import Task
        from src.database.database import Session, engine
        import datetime
        
        logger.info(f"Creating next instance for recurring task {recurring_task_id}")
        
        # Get the recurring task
        recurring_task = self.get_recurring_task(recurring_task_id)
        if not recurring_task:
            logger.error(f"Cannot create next instance: recurring task {recurring_task_id} not found")
            return None
        
        # Count existing future instances for this recurring task
        with Session(engine) as session:
            # Count tasks that are linked to this recurring task and have a due date in the future
            future_instances_count = session.exec(
                select(Task)
                .where(Task.recurring_task_id == recurring_task_id)
                .where(Task.due_date > datetime.datetime.now())
            ).count()
            
            # Check if we've reached the max instances
            if future_instances_count >= recurring_task.max_instances:
                logger.warning(f"Max instances ({recurring_task.max_instances}) reached for recurring task {recurring_task_id}")
                return None
        
        # Calculate the next due date based on the recurrence pattern
        import datetime
        next_due_date = None
        
        if recurring_task.recurrence_pattern == RecurrencePattern.DAILY:
            next_due_date = datetime.datetime.now() + datetime.timedelta(days=1)
        elif recurring_task.recurrence_pattern == RecurrencePattern.WEEKLY:
            next_due_date = datetime.datetime.now() + datetime.timedelta(weeks=1)
        elif recurring_task.recurrence_pattern == RecurrencePattern.MONTHLY:
            # For simplicity, just add 30 days
            next_due_date = datetime.datetime.now() + datetime.timedelta(days=30)
        elif recurring_task.recurrence_pattern == RecurrencePattern.CUSTOM and recurring_task.custom_interval:
            next_due_date = datetime.datetime.now() + datetime.timedelta(days=recurring_task.custom_interval)
        
        # Create a new task based on the recurring task
        task_service = TaskService()
        new_task_data = TaskCreate(
            title=recurring_task.title,
            description=recurring_task.description,
            priority=recurring_task.priority,
            tags=recurring_task.tags,
            due_date=next_due_date,
            status=TaskStatus.PENDING
        )
        
        try:
            new_task = task_service.create_task(new_task_data)
            logger.info(f"Created next instance of recurring task {recurring_task_id} with new task ID: {new_task.id}")
            return str(new_task.id)
        except Exception as e:
            logger.error(f"Failed to create next instance for recurring task {recurring_task_id}: {str(e)}")
            return None