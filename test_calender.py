"""Test Google Calendar MCP integration."""

from mcp.google_calendar_client import GoogleCalendarClient

def test_calendar():
    client = GoogleCalendarClient()
    
    if client.calendar_available:
        print("✅ Google Calendar connected successfully!")
        
        # Test event creation
        event_details = {
            'title': 'Test Event',
            'date': '2024-12-15',
            'time': '14:00',
            'duration': '1 hour',
            'description': 'Testing ScholarMate calendar integration'
        }
        
        result = client.create_event(event_details)
        print(f"Event creation: {result}")
    else:
        print("❌ Google Calendar not available")
        print("Using local-only mode")

if __name__ == "__main__":
    test_calendar()