"""
Google Calendar MCP Client - Handles Google Calendar API integration.
Implements Model Context Protocol for calendar operations.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)


class GoogleCalendarClient:
    """
    MCP client for Google Calendar integration.
    Handles authentication and CRUD operations for calendar events.
    """
    
    def __init__(self):
        """Initialize Google Calendar client."""
        self.calendar_available = False
        self.service = None
        
        try:
            self._initialize_calendar_service()
        except Exception as e:
            logger.warning(f"Google Calendar not available: {e}")
            logger.info("Using local storage fallback for calendar operations")
    
    def _initialize_calendar_service(self):
        """
        Initialize Google Calendar API service.
        Requires credentials and authentication.
        """
        try:
            # Check for credentials
            credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
            token_path = os.getenv('GOOGLE_TOKEN_PATH', 'token.json')
            
            if not os.path.exists(credentials_path):
                logger.warning(f"Credentials file not found: {credentials_path}")
                return
            
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            
            SCOPES = ['https://www.googleapis.com/auth/calendar']
            
            creds = None
            
            # Load existing token
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            
            # Refresh or obtain new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('calendar', 'v3', credentials=creds)
            self.calendar_available = True
            logger.info("Google Calendar service initialized successfully")
            
        except ImportError:
            logger.warning("Google Calendar libraries not installed. Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        except Exception as e:
            logger.error(f"Failed to initialize Google Calendar: {e}")
    
    def create_event(self, event_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a calendar event.
        
        Args:
            event_details: Dictionary with title, date, time, duration, description
            
        Returns:
            Success status and event ID
        """
        try:
            if not self.calendar_available:
                return {
                    'success': False,
                    'message': 'Google Calendar not available - using local storage',
                    'local_only': True
                }
            
            # Build event object
            event = self._build_event_object(event_details)
            
            # Create event via API
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            logger.info(f"Created calendar event: {created_event.get('id')}")
            
            return {
                'success': True,
                'message': 'Event created successfully',
                'event_id': created_event.get('id'),
                'link': created_event.get('htmlLink')
            }
            
        except Exception as e:
            logger.error(f"Error creating calendar event: {e}")
            return {
                'success': False,
                'message': f'Failed to create event: {str(e)}'
            }
    
    def _build_event_object(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Build Google Calendar event object from details."""
        title = details.get('title', 'Untitled Event')
        date_str = details.get('date')
        time_str = details.get('time')
        duration = details.get('duration', '1 hour')
        description = details.get('description', '')
        
        # Parse start datetime
        if time_str:
            start_datetime = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
        else:
            start_datetime = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Calculate end datetime
        duration_hours = self._parse_duration(duration)
        end_datetime = start_datetime + timedelta(hours=duration_hours)
        
        # Build event
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'IST',
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'IST',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 30},
                ],
            },
        }
        
        return event
    
    def _parse_duration(self, duration_str: str) -> float:
        """Parse duration string to hours (float)."""
        import re
        
        # Match patterns like "2 hours", "90 minutes", "1.5 hours"
        hour_match = re.search(r'([\d.]+)\s*hours?', duration_str)
        if hour_match:
            return float(hour_match.group(1))
        
        minute_match = re.search(r'(\d+)\s*minutes?', duration_str)
        if minute_match:
            return float(minute_match.group(1)) / 60
        
        # Default to 1 hour
        return 1.0
    
    def list_events(self, start_date: Optional[datetime] = None, max_results: int = 10) -> Dict[str, Any]:
        """
        List calendar events.
        
        Args:
            start_date: Start date for event listing (defaults to now)
            max_results: Maximum number of events to return
            
        Returns:
            List of events
        """
        try:
            if not self.calendar_available:
                return {
                    'success': False,
                    'message': 'Google Calendar not available',
                    'events': []
                }
            
            if not start_date:
                start_date = datetime.utcnow()
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_date.isoformat() + 'Z',
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            return {
                'success': True,
                'events': events,
                'count': len(events)
            }
            
        except Exception as e:
            logger.error(f"Error listing events: {e}")
            return {
                'success': False,
                'message': str(e),
                'events': []
            }
    
    def update_event(self, event_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing calendar event.
        
        Args:
            event_id: Google Calendar event ID
            updates: Dictionary of fields to update
            
        Returns:
            Success status
        """
        try:
            if not self.calendar_available:
                return {
                    'success': False,
                    'message': 'Google Calendar not available'
                }
            
            # Get existing event
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            # Apply updates
            if 'title' in updates:
                event['summary'] = updates['title']
            if 'description' in updates:
                event['description'] = updates['description']
            
            # Update event
            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            return {
                'success': True,
                'message': 'Event updated successfully',
                'event_id': updated_event.get('id')
            }
            
        except Exception as e:
            logger.error(f"Error updating event: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def delete_event(self, event_id: str) -> Dict[str, Any]:
        """
        Delete a calendar event.
        
        Args:
            event_id: Google Calendar event ID
            
        Returns:
            Success status
        """
        try:
            if not self.calendar_available:
                return {
                    'success': False,
                    'message': 'Google Calendar not available'
                }
            
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            logger.info(f"Deleted event: {event_id}")
            
            return {
                'success': True,
                'message': 'Event deleted successfully'
            }
            
        except Exception as e:
            logger.error(f"Error deleting event: {e}")
            return {
                'success': False,
                'message': str(e)
            }