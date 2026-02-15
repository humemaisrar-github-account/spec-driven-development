from typing import Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatResponses:
    """
    Generates appropriate chat responses for the advanced features.
    """
    
    @staticmethod
    def task_created(task_id: str, title: str) -> str:
        """Generate response when a task is created."""
        response = f"✅ Task '{title}' has been created successfully with ID: {task_id}"
        logger.info(response)
        return response

    @staticmethod
    def task_updated(task_id: str, updates: Dict[str, Any]) -> str:
        """Generate response when a task is updated."""
        changes = []
        if 'priority' in updates:
            changes.append(f"priority set to {updates['priority']}")
        if 'tags' in updates:
            changes.append(f"tags updated to {', '.join(updates['tags'])}")
        if 'due_date' in updates:
            changes.append(f"due date set to {updates['due_date']}")
        
        if changes:
            changes_str = ", ".join(changes)
            response = f"🔄 Task {task_id} updated: {changes_str}"
        else:
            response = f"🔄 Task {task_id} updated"
        
        logger.info(response)
        return response

    @staticmethod
    def task_completed(task_id: str) -> str:
        """Generate response when a task is completed."""
        response = f"🎉 Task {task_id} marked as completed!"
        logger.info(response)
        return response

    @staticmethod
    def recurring_task_created(recurring_task_id: str, title: str) -> str:
        """Generate response when a recurring task is created."""
        response = f"🔄 Recurring task '{title}' has been created with ID: {recurring_task_id}. Future instances will be automatically generated."
        logger.info(response)
        return response

    @staticmethod
    def reminder_scheduled(task_id: str, reminder_time: str) -> str:
        """Generate response when a reminder is scheduled."""
        response = f"⏰ Reminder scheduled for task {task_id} at {reminder_time}"
        logger.info(response)
        return response

    @staticmethod
    def reminder_snoozed(task_id: str, duration: str) -> str:
        """Generate response when a reminder is snoozed."""
        response = f"⏸️ Reminder for task {task_id} snoozed for {duration}"
        logger.info(response)
        return response

    @staticmethod
    def reminder_dismissed(task_id: str) -> str:
        """Generate response when a reminder is dismissed."""
        response = f"❌ Reminder for task {task_id} dismissed"
        logger.info(response)
        return response

    @staticmethod
    def search_results(query: str, count: int) -> str:
        """Generate response for search results."""
        if count == 0:
            response = f"🔍 No tasks found matching '{query}'"
        elif count == 1:
            response = f"🔍 Found 1 task matching '{query}'"
        else:
            response = f"🔍 Found {count} tasks matching '{query}'"
        
        logger.info(response)
        return response

    @staticmethod
    def filter_results(filters: Dict[str, Any], count: int) -> str:
        """Generate response for filtered results."""
        filter_parts = []
        if 'priority' in filters:
            filter_parts.append(f"priority {filters['priority']}")
        if 'tags' in filters:
            filter_parts.append(f"tags {', '.join(filters['tags'])}")
        if 'due_date_range' in filters:
            filter_parts.append(f"due date {filters['due_date_range']}")
        
        if filter_parts:
            filters_str = " and ".join(filter_parts)
            if count == 0:
                response = f"🔍 No tasks found with {filters_str}"
            elif count == 1:
                response = f"🔍 Found 1 task with {filters_str}"
            else:
                response = f"🔍 Found {count} tasks with {filters_str}"
        else:
            response = f"🔍 Showing {count} tasks"
        
        logger.info(response)
        return response

    @staticmethod
    def sort_confirmation(sort_field: str, sort_order: str) -> str:
        """Generate response when tasks are sorted."""
        order_text = "descending" if sort_order == "desc" else "ascending"
        response = f"📊 Tasks sorted by {sort_field} in {order_text} order"
        logger.info(response)
        return response

    @staticmethod
    def error_response(error_message: str) -> str:
        """Generate error response."""
        response = f"❌ Error: {error_message}"
        logger.error(response)
        return response

    @staticmethod
    def help_response() -> str:
        """Generate help response with available commands."""
        response = """
🤖 Available commands:
• Add a task: "Add task title #tag1 #tag2 with high priority due tomorrow"
• Set priority: "Set task priority to high"
• Add tags: "Add #work #urgent tags to task"
• Set due date: "Set due date to Friday at 5pm"
• Create recurring task: "Create recurring task daily at 9am"
• Schedule reminder: "Remind me 1 hour before due date"
• Search tasks: "Find tasks about meeting"
• Filter tasks: "Show high priority tasks"
• Sort tasks: "Sort tasks by due date"
• Complete task: "Complete task 123"
"""
        logger.info("Providing help information")
        return response