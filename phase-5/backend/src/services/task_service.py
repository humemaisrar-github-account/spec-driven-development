import logging
from datetime import datetime
from typing import List, Optional
from sqlmodel import Session, select
from src.models.task import Task, TaskCreate, TaskUpdate, TaskPriority, TaskStatus
from src.database.database import engine

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskService:
    def create_task(self, task_data: TaskCreate) -> Task:
        """Create a new task with priority, tags, and due date"""
        logger.info(f"Creating task with title: {task_data.title}, priority: {task_data.priority}, tags: {task_data.tags}")
        
        with Session(engine) as session:
            # Validate max 5 tags
            if len(task_data.tags) > 5:
                logger.warning(f"Attempted to create task with more than 5 tags: {len(task_data.tags)} tags provided")
                raise ValueError("Maximum 5 tags allowed per task")
            
            # Set default priority if not provided
            if not task_data.priority:
                task_data.priority = TaskPriority.MEDIUM
                logger.info("Default priority MEDIUM applied to task")
            
            db_task = Task.model_validate(task_data)
            session.add(db_task)
            session.commit()
            session.refresh(db_task)
            logger.info(f"Task created successfully with ID: {db_task.id}")
            return db_task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by ID"""
        with Session(engine) as session:
            statement = select(Task).where(Task.id == task_id)
            return session.exec(statement).first()

    def get_tasks(
        self, 
        priority: Optional[TaskPriority] = None, 
        tags: Optional[List[str]] = None, 
        due_date_from: Optional[datetime] = None,
        due_date_to: Optional[datetime] = None,
        without_due_date: Optional[bool] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """Retrieve tasks with optional filtering, sorting, and search capabilities"""
        logger.info(f"Retrieving tasks with filters: priority={priority}, tags={tags}, search='{search}', sort_by={sort_by}")
        
        with Session(engine) as session:
            statement = select(Task)
            
            # Apply filters
            if priority:
                statement = statement.where(Task.priority == priority)
            
            # Filter by tags (using PostgreSQL JSON operators)
            if tags:
                for tag in tags:
                    statement = statement.where(Task.tags.op('?')(tag))
            
            if due_date_from:
                statement = statement.where(Task.due_date >= due_date_from)
                
            if due_date_to:
                statement = statement.where(Task.due_date <= due_date_to)
                
            if without_due_date:
                statement = statement.where(Task.due_date.is_(None))
            
            # Apply search (basic implementation - would need full-text search in real implementation)
            if search:
                statement = statement.where(
                    Task.title.contains(search) | Task.description.contains(search)
                )
            
            # Apply sorting
            if sort_by == "due_date":
                if sort_order == "desc":
                    statement = statement.order_by(Task.due_date.desc())
                else:
                    statement = statement.order_by(Task.due_date.asc())
            elif sort_by == "priority":
                if sort_order == "desc":
                    statement = statement.order_by(Task.priority.desc())
                else:
                    statement = statement.order_by(Task.priority.asc())
            elif sort_by == "created_at":
                if sort_order == "desc":
                    statement = statement.order_by(Task.created_at.desc())
                else:
                    statement = statement.order_by(Task.created_at.asc())
            elif sort_by == "title":
                if sort_order == "desc":
                    statement = statement.order_by(Task.title.desc())
                else:
                    statement = statement.order_by(Task.title.asc())
            else:
                # Default sorting by creation date descending
                statement = statement.order_by(Task.created_at.desc())
            
            statement = statement.offset(skip).limit(limit)
            results = session.exec(statement).all()
            logger.info(f"Retrieved {len(results)} tasks")
            return results

    def update_task(self, task_id: str, task_data: TaskUpdate) -> Optional[Task]:
        """Update an existing task with priority, tags, and due date"""
        logger.info(f"Updating task {task_id} with priority and tags")
        
        with Session(engine) as session:
            db_task = session.get(Task, task_id)
            if not db_task:
                logger.warning(f"Attempted to update non-existent task: {task_id}")
                return None
            
            # Validate max 5 tags if updating tags
            if task_data.tags is not None and len(task_data.tags) > 5:
                logger.warning(f"Attempted to update task {task_id} with more than 5 tags: {len(task_data.tags)} tags provided")
                raise ValueError("Maximum 5 tags allowed per task")
            
            # Log changes to priority and tags
            if task_data.priority is not None and task_data.priority != db_task.priority:
                logger.info(f"Priority changed from {db_task.priority} to {task_data.priority} for task {task_id}")
            
            if task_data.tags is not None and task_data.tags != db_task.tags:
                logger.info(f"Tags changed from {db_task.tags} to {task_data.tags} for task {task_id}")
            
            # Update fields
            update_data = task_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_task, field, value)
            
            # Update timestamps
            db_task.updated_at = datetime.utcnow()
            if db_task.status == TaskStatus.COMPLETED and not db_task.completed_at:
                db_task.completed_at = datetime.utcnow()
            elif db_task.status != TaskStatus.COMPLETED:
                db_task.completed_at = None  # Reset if task is reopened
            
            session.add(db_task)
            session.commit()
            session.refresh(db_task)
            logger.info(f"Task {task_id} updated successfully")
            return db_task

    def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID"""
        with Session(engine) as session:
            db_task = session.get(Task, task_id)
            if not db_task:
                return False
            
            session.delete(db_task)
            session.commit()
            return True

    def mark_task_completed(self, task_id: str) -> Optional[Task]:
        """Mark a task as completed"""
        with Session(engine) as session:
            db_task = session.get(Task, task_id)
            if not db_task:
                return None
            
            db_task.status = TaskStatus.COMPLETED
            db_task.completed_at = datetime.utcnow()
            db_task.updated_at = datetime.utcnow()
            
            session.add(db_task)
            session.commit()
            session.refresh(db_task)
            return db_task