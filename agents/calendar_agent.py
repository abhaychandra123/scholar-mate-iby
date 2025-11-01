"""
Calendar Agent - Manages Google Calendar integration via MCP.
Converts natural language to structured calendar events.
"""

import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CalendarAgent:
    """
    Handles calendar operations including event creation, updates, and retrieval.
    Uses MCP to communicate with Google Calendar API.
    """
    
    def __init__(self):
        """Initialize calendar agent with MCP client."""
        try:
            from mcp.google_calendar_client import GoogleCalendarClient
            self.calendar_client = GoogleCalendarClient()
            logger.info("Calendar agent initialized with MCP client")
        except Exception as e:
            logger.error(f"Failed to initialize calendar client: {e}")
            self.calendar_client = None
    
    def process_calendar_request(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process calendar-related requests.
        
        Args:
            user_input: Natural language calendar request
            context: Additional context (user preferences, timezone, etc.)
            
        Returns:
            Response dictionary with event details or error message
        """
        try:
            # Parse intent type (create, list, update, delete)
            action = self._detect_calendar_action(user_input)
            
            if action == 'create':
                return self._create_event(user_input, context)
            elif action == 'list':
                return self._list_events(user_input, context)
            elif action == 'update':
                return self._update_event(user_input, context)
            elif action == 'delete':
                return self._delete_event(user_input, context)
            else:
                return {
                    'success': False,
                    'message': 'Could not determine calendar action. Please specify create, list, update, or delete.'
                }
                
        except Exception as e:
            logger.error(f"Error processing calendar request: {e}")
            return {'success': False, 'message': f'Calendar error: {str(e)}'}
    
    def _detect_calendar_action(self, user_input: str) -> str:
        """Detect the type of calendar action requested."""
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ['create', 'schedule', 'add', 'book', 'set up']):
            return 'create'
        elif any(word in user_input_lower for word in ['list', 'show', 'view', 'what', 'upcoming']):
            return 'list'
        elif any(word in user_input_lower for word in ['update', 'change', 'modify', 'reschedule']):
            return 'update'
        elif any(word in user_input_lower for word in ['delete', 'remove', 'cancel']):
            return 'delete'
        
        return 'create'  # Default to create
    
    def _create_event(self, user_input: str, context: Optional[Dict]) -> Dict[str, Any]:
        """
        Create a new calendar event from natural language.
        
        Extracts: title, date, time, duration, description
        """
        try:
            # Parse event details from natural language
            event_details = self._parse_event_details(user_input)
            
            if not event_details.get('title'):
                return {
                    'success': False,
                    'message': 'Could not extract event title. Please specify what you want to schedule.'
                }
            
            # Create event via MCP
            if self.calendar_client:
                result = self.calendar_client.create_event(event_details)
                
                if result.get('success'):
                    # Also save to local database
                    from mcp.database_tool import DatabaseTool
                    db = DatabaseTool()
                    db.save_event(event_details)
                    
                    return {
                        'success': True,
                        'message': f"✅ Created event: {event_details['title']} on {event_details['date']} at {event_details.get('time', 'all day')}",
                        'event': event_details,
                        'event_id': result.get('event_id')
                    }
                else:
                    return result
            else:
                # Fallback to local storage only
                from mcp.database_tool import DatabaseTool
                db = DatabaseTool()
                event_id = db.save_event(event_details)
                
                return {
                    'success': True,
                    'message': f"✅ Created local event: {event_details['title']}",
                    'event': event_details,
                    'event_id': event_id,
                    'note': 'Calendar sync unavailable - stored locally only'
                }
                
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            return {'success': False, 'message': f'Failed to create event: {str(e)}'}
    
    def _parse_event_details(self, user_input: str) -> Dict[str, Any]:
        """
        Parse event details from natural language.
        
        Returns:
            Dictionary with: title, date, time, duration, description
        """
        details = {}
        
        # Extract title (everything before time/date keywords)
        title_match = re.match(r'^(?:schedule|create|add|book)?\s*(?:a|an)?\s*([^:]+?)(?:\s+on|\s+at|\s+for|\s+tomorrow|\s+today|\s+next)', user_input, re.IGNORECASE)
        if title_match:
            details['title'] = title_match.group(1).strip()
        else:
            # Fallback: take first 5 words
            words = user_input.split()[:5]
            details['title'] = ' '.join(words)
        
        # Extract date
        date_info = self._extract_date(user_input)
        details['date'] = date_info['date']
        details['date_str'] = date_info['date_str']
        
        # Extract time
        time_info = self._extract_time(user_input)
        details['time'] = time_info['time']
        details['time_str'] = time_info['time_str']
        
        # Extract duration
        duration = self._extract_duration(user_input)
        details['duration'] = duration
        
        # Description (optional)
        desc_match = re.search(r'(?:about|regarding|for)\s+(.+)$', user_input, re.IGNORECASE)
        if desc_match:
            details['description'] = desc_match.group(1).strip()
        else:
            details['description'] = ''
        
        return details
    
    def _extract_date(self, text: str) -> Dict[str, str]:
        """Extract date from natural language."""
        today = datetime.now()
        text_lower = text.lower()
        
        # Check for relative dates
        if 'today' in text_lower:
            target_date = today
        elif 'tomorrow' in text_lower:
            target_date = today + timedelta(days=1)
        elif 'next week' in text_lower:
            target_date = today + timedelta(days=7)
        elif match := re.search(r'in (\d+) days?', text_lower):
            days = int(match.group(1))
            target_date = today + timedelta(days=days)
        elif match := re.search(r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', text_lower):
            weekday_name = match.group(1)
            weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            target_weekday = weekdays.index(weekday_name)
            current_weekday = today.weekday()
            days_ahead = (target_weekday - current_weekday) % 7
            if days_ahead == 0:
                days_ahead = 7  # Next occurrence
            target_date = today + timedelta(days=days_ahead)
        else:
            # Default to today
            target_date = today
        
        return {
            'date': target_date.strftime('%Y-%m-%d'),
            'date_str': target_date.strftime('%A, %B %d, %Y')
        }
    
    def _extract_time(self, text: str) -> Dict[str, str]:
        """Extract time from natural language."""
        # Match patterns like "3pm", "3:30pm", "15:00", "at 2"
        time_pattern = r'(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*([ap]m?)?'
        match = re.search(time_pattern, text.lower())
        
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            period = match.group(3)
            
            # Convert to 24-hour format
            if period and 'p' in period and hour != 12:
                hour += 12
            elif period and 'a' in period and hour == 12:
                hour = 0
            
            time_obj = datetime.strptime(f"{hour:02d}:{minute:02d}", '%H:%M')
            return {
                'time': time_obj.strftime('%H:%M'),
                'time_str': time_obj.strftime('%I:%M %p')
            }
        
        return {
            'time': None,
            'time_str': 'All day'
        }
    
    def _extract_duration(self, text: str) -> str:
        """Extract duration from natural language."""
        # Match patterns like "for 2 hours", "1 hour", "30 minutes"
        duration_pattern = r'for\s+(\d+)\s*(hour|hr|minute|min)s?'
        match = re.search(duration_pattern, text.lower())
        if match:
            amount = int(match.group(1))
            unit = match.group(2)
            
            if 'hour' in unit or 'hr' in unit:
                return f"{amount} hour{'s' if amount > 1 else ''}"
            else:
                return f"{amount} minute{'s' if amount > 1 else ''}"
        
        # Default duration
        return "1 hour"

    def _list_events(self, user_input: str, context: Optional[Dict]) -> Dict[str, Any]:
        """List calendar events."""
        try:
            from mcp.database_tool import DatabaseTool
            db = DatabaseTool()
            
            # Determine time range
            if 'today' in user_input.lower():
                events = db.get_events_for_date(datetime.now().strftime('%Y-%m-%d'))
            elif 'week' in user_input.lower():
                events = db.get_upcoming_events(days=7)
            elif 'month' in user_input.lower():
                events = db.get_upcoming_events(days=30)
            else:
                events = db.get_upcoming_events(days=7)  # Default to week
            
            if events:
                return {
                    'success': True,
                    'message': f'Found {len(events)} upcoming event(s)',
                    'events': events
                }
            else:
                return {
                    'success': True,
                    'message': 'No upcoming events found',
                    'events': []
                }
                
        except Exception as e:
            logger.error(f"Error listing events: {e}")
            return {'success': False, 'message': f'Failed to list events: {str(e)}'}

    def _update_event(self, user_input: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Update an existing calendar event."""
        try:
            from mcp.database_tool import DatabaseTool
            db = DatabaseTool()
            
            # Extract event identifier and new details
            # This is simplified - in production, you'd have a more sophisticated parser
            event_id = context.get('event_id') if context else None
            
            if not event_id:
                return {
                    'success': False,
                    'message': 'Please specify which event to update'
                }
            
            # Parse new details
            new_details = self._parse_event_details(user_input)
            
            # Update in database
            success = db.update_event(event_id, new_details)
            
            if success:
                return {
                    'success': True,
                    'message': f'✅ Updated event',
                    'event': new_details
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to update event'
                }
                
        except Exception as e:
            logger.error(f"Error updating event: {e}")
            return {'success': False, 'message': f'Failed to update event: {str(e)}'}

    def _delete_event(self, user_input: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Delete a calendar event."""
        try:
            from mcp.database_tool import DatabaseTool
            db = DatabaseTool()
            
            event_id = context.get('event_id') if context else None
            
            if not event_id:
                return {
                    'success': False,
                    'message': 'Please specify which event to delete'
                }
            
            success = db.delete_event(event_id)
            
            if success:
                return {
                    'success': True,
                    'message': '✅ Event deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to delete event'
                }
                
        except Exception as e:
            logger.error(f"Error deleting event: {e}")
            return {'success': False, 'message': f'Failed to delete event: {str(e)}'}