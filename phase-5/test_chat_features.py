import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.src.chat_parser import ChatParser
from backend.src.chat_responses import ChatResponses

def test_chat_parser():
    """Test the chat parser functionality"""
    parser = ChatParser()
    responses = ChatResponses()
    
    print("Testing Chat Parser and Responses for Phase V Advanced Features\n")
    
    # Test commands for the new features
    test_commands = [
        "Add presentation prep with high priority #work #urgent due Friday at 5pm",
        "Remind me to take medication every day at 8am, remind me 1 hour before",
        "Show me all #personal tasks due this week",
        "Change grocery shopping to low priority",
        "Find tasks about meeting",
        "Create recurring task: water plants every Tuesday",
        "Sort tasks by due date"
    ]
    
    for i, command in enumerate(test_commands, 1):
        print(f"Test {i}: {command}")
        parsed_data = parser.parse_command(command)
        print(f"  Parsed data: {parsed_data}")
        
        # Generate appropriate response based on the command type
        if 'Add' in command or 'Create' in command:
            response = f"Task '{parsed_data['title']}' has been created successfully with ID: 12345"
        elif 'Change' in command or 'Update' in command:
            changes = []
            if 'priority' in parsed_data:
                changes.append(f"priority set to {parsed_data['priority']}")
            if 'tags' in parsed_data:
                changes.append(f"tags updated to {', '.join(parsed_data['tags'])}")
            response = f"Task 12345 updated: {', '.join(changes) if changes else 'no changes'}"
        elif 'Show' in command or 'Find' in command:
            response = f"Found 3 tasks matching '{parsed_data.get('search_query', 'tasks')}'"
        elif 'Sort' in command:
            sort_by = parsed_data.get('sort_params', {}).get('by', 'due_date')
            response = f"Tasks sorted by {sort_by}"
        else:
            response = f"Processed command: {command}"
        
        print(f"  Response: {response}\n")

if __name__ == "__main__":
    test_chat_parser()