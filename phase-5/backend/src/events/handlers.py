import logging
from datetime import datetime
from typing import Dict, Any
from dapr.ext.workflow import WorkflowRuntime
from dapr.clients import DaprClient
from src.events.schemas import TaskEvent, RecurringTaskEvent, TaskEventType
from src.services.task_service import TaskService
from src.services.recurring_service import RecurringTaskService
from src.services.reminder_service import ReminderService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventHandler:
    def __init__(self):
        self.task_service = TaskService()
        self.recurring_service = RecurringTaskService()
        self.reminder_service = ReminderService()
        # In a real implementation, we would initialize Dapr clients
        # For now, using a mock implementation

    def handle_task_event(self, task_event: TaskEvent) -> bool:
        """Handle incoming task events"""
        try:
            if task_event.event_type == TaskEventType.TASK_CREATED:
                return self.handle_task_created(task_event)
            elif task_event.event_type == TaskEventType.TASK_UPDATED:
                return self.handle_task_updated(task_event)
            elif task_event.event_type == TaskEventType.TASK_COMPLETED:
                return self.handle_task_completed(task_event)
            elif task_event.event_type == TaskEventType.TASK_DELETED:
                return self.handle_task_deleted(task_event)
            elif task_event.event_type == TaskEventType.TASK_REMINDER_SCHEDULED:
                return self.handle_reminder_scheduled(task_event)
            elif task_event.event_type == TaskEventType.TASK_REMINDER_TRIGGERED:
                return self.handle_reminder_triggered(task_event)
            else:
                print(f"Unknown task event type: {task_event.event_type}")
                return False
        except Exception as e:
            print(f"Error handling task event: {str(e)}")
            return False

    def handle_recurring_task_event(self, recurring_task_event: RecurringTaskEvent) -> bool:
        """Handle incoming recurring task events"""
        try:
            if recurring_task_event.event_type == TaskEventType.RECURRING_TASK_CREATED:
                return self.handle_recurring_task_created(recurring_task_event)
            elif recurring_task_event.event_type == TaskEventType.RECURRING_TASK_INSTANCE_CREATED:
                return self.handle_recurring_task_instance_created(recurring_task_event)
            else:
                print(f"Unknown recurring task event type: {recurring_task_event.event_type}")
                return False
        except Exception as e:
            print(f"Error handling recurring task event: {str(e)}")
            return False

    def handle_task_created(self, task_event: TaskEvent) -> bool:
        """Handle task created event"""
        print(f"Task created event received for task {task_event.task_id}")
        # Could trigger notifications, analytics, etc.
        return True

    def handle_task_updated(self, task_event: TaskEvent) -> bool:
        """Handle task updated event"""
        print(f"Task updated event received for task {task_event.task_id}")
        # Could trigger notifications if certain fields changed
        return True

    def handle_task_completed(self, task_event: TaskEvent) -> bool:
        """Handle task completed event"""
        logger.info(f"Task completed event received for task {task_event.task_id}")
        
        # Check if this task was an instance of a recurring task
        task = self.task_service.get_task(task_event.task_id)
        if task and task.recurring_task_id:
            # Create the next instance of the recurring task
            next_instance_id = self.recurring_service.create_next_instance(task.recurring_task_id)
            if next_instance_id:
                logger.info(f"Created next instance of recurring task: {next_instance_id}")
                
                # Publish event for the new instance
                new_event = TaskEvent(
                    event_id=task_event.event_id,
                    event_type=TaskEventType.RECURRING_TASK_INSTANCE_CREATED,
                    task_id=next_instance_id,
                    timestamp=datetime.utcnow(),
                    payload={"parent_recurring_task_id": task.recurring_task_id}
                )
                # In a real implementation, we would publish this event
                # self.publish_event(new_event)
        
        return True

    def handle_task_deleted(self, task_event: TaskEvent) -> bool:
        """Handle task deleted event"""
        print(f"Task deleted event received for task {task_event.task_id}")
        return True

    def handle_reminder_scheduled(self, task_event: TaskEvent) -> bool:
        """Handle reminder scheduled event"""
        print(f"Reminder scheduled event received for task {task_event.task_id}")
        return True

    def handle_reminder_triggered(self, task_event: TaskEvent) -> bool:
        """Handle reminder triggered event"""
        print(f"Reminder triggered event received for task {task_event.task_id}")
        return True

    def handle_recurring_task_created(self, recurring_task_event: RecurringTaskEvent) -> bool:
        """Handle recurring task created event"""
        print(f"Recurring task created event received for recurring task {recurring_task_event.recurring_task_id}")
        return True

    def handle_recurring_task_instance_created(self, recurring_task_event: RecurringTaskEvent) -> bool:
        """Handle recurring task instance created event"""
        print(f"Recurring task instance created event received for recurring task {recurring_task_event.recurring_task_id}")
        return True

    def publish_event(self, event: TaskEvent) -> bool:
        """Publish an event to the event stream"""
        # In a real implementation, this would publish the event via Dapr
        # For now, just return True
        print(f"Published event: {event.event_type} for task {event.task_id}")
        return True