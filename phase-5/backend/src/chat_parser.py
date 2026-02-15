import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
from src.models.task import TaskPriority
from src.models.recurring_task import RecurrencePattern

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatParser:
    """
    Parses natural language commands from the chat interface to extract task information
    including priority, tags, due dates, and recurring patterns.
    """
    
    def __init__(self):
        # Priority patterns
        self.priority_patterns = {
            'high': r'\b(high|top|critical|urgent|important)\b',
            'medium': r'\b(medium|normal|regular)\b',
            'low': r'(low|bottom|least|minor)\b'
        }
        
        # Tag patterns (hashtags)
        self.tag_pattern = r'#([a-zA-Z0-9_]+)'
        
        # Due date patterns
        self.date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # MM/DD/YYYY or DD/MM/YYYY
            r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',    # YYYY-MM-DD
            r'today|tomorrow',                     # Today/tomorrow
            r'(next\s+(week|month|year))',         # Next week/month/year
            r'in\s+(\d+)\s+(minutes?|hours?|days?|weeks?|months?)'  # In X time units
        ]
        
        # Recurring patterns
        self.recurring_patterns = {
            'daily': r'\b(daily|every\s+day)\b',
            'weekly': r'\b(weekly|every\s+week|every\s+monday|every\s+tuesday|every\s+wednesday|every\s+thursday|every\s+friday|every\s+saturday|every\s+sunday)\b',
            'monthly': r'\b(monthly|every\s+month)\b',
            'custom': r'every\s+(\d+)\s+(days?|weeks?|months?)'  # Every X days/weeks/months
        }
        
        # Reminder patterns
        self.reminder_pattern = r'(remind\s+me\s+(in|at|before))'

    def parse_command(self, command: str) -> Dict:
        """
        Parse a natural language command and extract task information.
        
        Args:
            command: The user's natural language command
            
        Returns:
            Dictionary containing extracted information
        """
        logger.info(f"Parsing command: {command}")
        
        parsed_data = {
            'title': '',
            'priority': None,
            'tags': [],
            'due_date': None,
            'recurring_pattern': None,
            'custom_interval': None,
            'reminder_offset': None,
            'search_query': None,
            'filter_params': {},
            'sort_params': {}
        }
        
        # Extract title (everything that's not a specific directive)
        title = self._extract_title(command)
        parsed_data['title'] = title
        
        # Extract priority
        parsed_data['priority'] = self._extract_priority(command)
        
        # Extract tags
        parsed_data['tags'] = self._extract_tags(command)
        
        # Extract due date
        parsed_data['due_date'] = self._extract_due_date(command)
        
        # Extract recurring pattern
        recurring_info = self._extract_recurring_pattern(command)
        parsed_data['recurring_pattern'] = recurring_info['pattern']
        parsed_data['custom_interval'] = recurring_info['interval']
        
        # Extract reminder offset
        parsed_data['reminder_offset'] = self._extract_reminder_offset(command)
        
        # Check if this is a search/filter/sort command
        search_info = self._parse_search_commands(command)
        if search_info:
            parsed_data.update(search_info)
        
        logger.info(f"Parsed command data: {parsed_data}")
        return parsed_data

    def _extract_title(self, command: str) -> str:
        """Extract the main task title from the command."""
        # Remove known directives to isolate the title
        cleaned_command = command.lower()
        
        # Remove priority indicators
        for priority, pattern in self.priority_patterns.items():
            cleaned_command = re.sub(pattern, '', cleaned_command, flags=re.IGNORECASE)
        
        # Remove tag indicators
        cleaned_command = re.sub(self.tag_pattern, '', cleaned_command)
        
        # Remove recurring indicators
        for pattern in self.recurring_patterns.values():
            cleaned_command = re.sub(pattern, '', cleaned_command, flags=re.IGNORECASE)
        
        # Remove reminder indicators
        cleaned_command = re.sub(self.reminder_pattern, '', cleaned_command, flags=re.IGNORECASE)
        
        # Remove date indicators
        for pattern in self.date_patterns:
            cleaned_command = re.sub(pattern, '', cleaned_command, flags=re.IGNORECASE)
        
        # Clean up extra whitespace and return
        title = ' '.join(cleaned_command.split())
        return title.strip()

    def _extract_priority(self, command: str) -> Optional[str]:
        """Extract priority level from the command."""
        command_lower = command.lower()
        
        for priority, pattern in self.priority_patterns.items():
            if re.search(pattern, command_lower):
                return priority
        
        # Default to medium if no explicit priority mentioned
        return 'medium'

    def _extract_tags(self, command: str) -> List[str]:
        """Extract tags from the command."""
        tags = re.findall(self.tag_pattern, command)
        # Limit to 5 tags as per requirements
        return tags[:5]

    def _extract_due_date(self, command: str) -> Optional[datetime]:
        """Extract due date from the command."""
        command_lower = command.lower()
        
        # Handle simple cases
        if 'today' in command_lower:
            return datetime.today().replace(hour=23, minute=59, second=59)
        elif 'tomorrow' in command_lower:
            from datetime import timedelta
            return (datetime.today() + timedelta(days=1)).replace(hour=23, minute=59, second=59)
        
        # Handle more complex date patterns
        for pattern in self.date_patterns:
            match = re.search(pattern, command_lower)
            if match:
                date_str = match.group(1)
                try:
                    # Try different date formats
                    if '/' in date_str or '-' in date_str:
                        # Handle MM/DD/YYYY, DD/MM/YYYY, or YYYY-MM-DD
                        parts = re.split(r'[/-]', date_str)
                        if len(parts) == 3:
                            # If first part looks like year, it's YYYY-MM-DD
                            if int(parts[0]) > 31:
                                return datetime(int(parts[0]), int(parts[1]), int(parts[2]))
                            # Otherwise assume MM/DD/YYYY or DD/MM/YYYY
                            else:
                                return datetime(int(parts[2]), int(parts[0]), int(parts[1]))
                except (ValueError, IndexError):
                    continue  # If parsing fails, continue to next pattern
        
        return None

    def _extract_recurring_pattern(self, command: str) -> Dict:
        """Extract recurring pattern from the command."""
        command_lower = command.lower()
        
        for pattern_name, pattern in self.recurring_patterns.items():
            match = re.search(pattern, command_lower)
            if match:
                if pattern_name == 'custom':
                    # Extract the interval (number) and unit
                    interval_match = re.search(r'every\s+(\d+)\s+(days?|weeks?|months?)', command_lower)
                    if interval_match:
                        interval = int(interval_match.group(1))
                        unit = interval_match.group(2)
                        
                        # Convert to days for storage
                        if 'day' in unit:
                            return {'pattern': RecurrencePattern.CUSTOM, 'interval': interval}
                        elif 'week' in unit:
                            return {'pattern': RecurrencePattern.CUSTOM, 'interval': interval * 7}
                        elif 'month' in unit:
                            return {'pattern': RecurrencePattern.CUSTOM, 'interval': interval * 30}
                
                return {'pattern': getattr(RecurrencePattern, pattern_name.upper()), 'interval': None}
        
        return {'pattern': None, 'interval': None}

    def _extract_reminder_offset(self, command: str) -> Optional[str]:
        """Extract reminder offset from the command."""
        command_lower = command.lower()
        
        # Look for patterns like "remind me in 1 hour", "remind me 30 minutes before"
        match = re.search(r'(\d+)\s+(minutes?|hours?|days?)', command_lower)
        if match:
            amount = match.group(1)
            unit = match.group(2)
            
            # Convert to standard format (e.g., "1h", "30m", "1d")
            if 'minute' in unit:
                return f"{amount}m"
            elif 'hour' in unit:
                return f"{amount}h"
            elif 'day' in unit:
                return f"{amount}d"
        
        return None

    def _parse_search_commands(self, command: str) -> Optional[Dict]:
        """Parse search, filter, and sort commands."""
        command_lower = command.lower()
        
        # Check if this is a search command
        if any(word in command_lower for word in ['find', 'search', 'look for', 'show me']):
            # Extract search query
            search_match = re.search(r'(?:find|search|look for|show me)\s+(.+?)(?:\s+with|\s+by|\s+due|$)', command_lower)
            if search_match:
                return {
                    'search_query': search_match.group(1).strip(),
                    'filter_params': {},
                    'sort_params': {}
                }
        
        # Check if this is a filter command
        filter_params = {}
        if 'with' in command_lower or 'by' in command_lower:
            # Extract filters
            if any(pri in command_lower for pri in ['high', 'medium', 'low']):
                priority = self._extract_priority(command_lower)
                filter_params['priority'] = priority
            
            # Extract tags
            tags = self._extract_tags(command)
            if tags:
                filter_params['tags'] = tags
        
        # Check if this is a sort command
        sort_params = {}
        if 'sort' in command_lower or 'order' in command_lower:
            if 'due date' in command_lower:
                sort_params['by'] = 'due_date'
            elif 'priority' in command_lower:
                sort_params['by'] = 'priority'
            elif 'created' in command_lower:
                sort_params['by'] = 'created_at'
            elif 'title' in command_lower:
                sort_params['by'] = 'title'
            
            if 'asc' in command_lower or 'ascending' in command_lower:
                sort_params['order'] = 'asc'
            elif 'desc' in command_lower or 'descending' in command_lower:
                sort_params['order'] = 'desc'
        
        if filter_params or sort_params:
            return {
                'search_query': None,
                'filter_params': filter_params,
                'sort_params': sort_params
            }
        
        return None


# Example usage
if __name__ == "__main__":
    parser = ChatParser()
    
    # Test commands
    test_commands = [
        "Add presentation prep with high priority #work #urgent due Friday at 5pm",
        "Remind me to take medication every day at 8am, remind me 1 hour before",
        "Show me all #personal tasks due this week",
        "Change grocery shopping to low priority",
        "Find tasks about meeting"
    ]
    
    for cmd in test_commands:
        print(f"\nCommand: {cmd}")
        result = parser.parse_command(cmd)
        print(f"Parsed: {result}")