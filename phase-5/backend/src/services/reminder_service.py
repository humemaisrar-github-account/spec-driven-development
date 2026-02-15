import logging
from datetime import datetime, timedelta
from typing import Optional
from dapr.ext.workflow import WorkflowRuntime
from dapr.clients import DaprClient
from src.models.task import Task
from src.services.task_service import TaskService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReminderService:
    def __init__(self):
        self.task_service = TaskService()
        # In a real implementation, we would initialize Dapr clients
        # For now, using a mock implementation

    def schedule_reminder(self, task_id: str, reminder_offset: str = "1h") -> bool:
        """
        Schedule a reminder for a task based on the reminder offset
        reminder_offset: e.g., "5m", "1h", "1d" for 5 minutes, 1 hour, 1 day
        """
        # Parse the reminder offset
        try:
            offset_value = int(reminder_offset[:-1])
            offset_unit = reminder_offset[-1]
        except (ValueError, IndexError):
            raise ValueError(f"Invalid reminder offset format: {reminder_offset}. Expected format: e.g., '5m', '1h', '1d'")
        
        # Calculate the reminder time based on due date
        task = self.task_service.get_task(task_id)
        if not task or not task.due_date:
            logger.warning(f"Cannot schedule reminder for task {task_id}: task not found or no due date set")
            return False
        
        # Calculate reminder time
        if offset_unit == 'm':
            reminder_time = task.due_date - timedelta(minutes=offset_value)
        elif offset_unit == 'h':
            reminder_time = task.due_date - timedelta(hours=offset_value)
        elif offset_unit == 'd':
            reminder_time = task.due_date - timedelta(days=offset_value)
        else:
            raise ValueError(f"Invalid reminder offset unit: {offset_unit}. Use 'm' for minutes, 'h' for hours, 'd' for days")
        
        # In a real implementation, we would use Dapr Jobs API to schedule the reminder
        # For now, we'll just return True to indicate scheduling was successful
        logger.info(f"Scheduled reminder for task {task_id} at {reminder_time}")
        return True

    def trigger_reminder(self, task_id: str) -> bool:
        """Trigger a reminder for a task (called by Dapr Jobs API)"""
        logger.info(f"Triggering reminder for task {task_id}")
        
        # In a real implementation, this would send the reminder to the user
        # For now, we'll just print a message
        task = self.task_service.get_task(task_id)
        if not task:
            logger.warning(f"Could not trigger reminder for non-existent task: {task_id}")
            return False
        
        # In a real implementation, this would send the reminder to the chat interface
        # For now, we'll log the reminder that would be sent
        reminder_message = f"⏰ Reminder: Task '{task.title}' is due soon!"
        logger.info(f"Reminder triggered for task '{task.title}' (ID: {task_id}): {reminder_message}")
        
        # In a real implementation, we would send this message to the chat interface
        # send_to_chat_interface(task.user_id, reminder_message)
        
        return True

    def get_reminder_offset_config(self) -> dict:
        """Return available reminder offset configurations"""
        return {
            "options": ["5m", "15m", "30m", "1h", "2h", "6h", "1d", "2d"],
            "defaults": {
                "email": "1h",
                "push": "15m",
                "sms": "30m"
            }
        }

    def snooze_reminder(self, task_id: str, snooze_duration: str = "10m") -> bool:
        """Snooze a reminder for a specified duration"""
        logger.info(f"Snoozing reminder for task {task_id} for {snooze_duration}")
        
        # Cancel the current reminder
        # Reschedule with the new time
        # For now, just return True
        logger.info(f"Snoozed reminder for task {task_id} for {snooze_duration}")
        return True

    def dismiss_reminder(self, task_id: str) -> bool:
        """Dismiss a reminder for a task"""
        logger.info(f"Dismissing reminder for task {task_id}")
        
        # Cancel the reminder
        # For now, just return True
        logger.info(f"Dismissed reminder for task {task_id}")
        return True

    def check_overdue_tasks(self) -> list:
        """Check for overdue tasks and return them"""
        logger.info("Checking for overdue tasks")
        
        # In a real implementation, this would query the database for overdue tasks
        # For now, returning an empty list
        overdue_tasks = []  # Would be populated with actual overdue tasks in a real implementation
        logger.info(f"Found {len(overdue_tasks)} overdue tasks")
        return overdue_tasks

    def handle_task_completion_with_reminder_logic(self, task_id: str) -> bool:
        """Handle task completion and any associated reminder logic"""
        logger.info(f"Handling task completion for {task_id} with reminder logic")
        
        # If the task has a recurring pattern, create the next instance
        # For now, just return True
        logger.info(f"Handled task completion for {task_id}")
        return True