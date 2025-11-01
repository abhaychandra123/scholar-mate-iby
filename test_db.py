# test_database_mcp.py
from mcp.database_tool import DatabaseTool

db = DatabaseTool()

# Test flashcard storage
flashcard = {
    'question': 'What is MCP?',
    'answer': 'Model Context Protocol',
}
card_id = db.save_flashcard(flashcard)
print(f"✅ Flashcard saved with ID: {card_id}")

# Test event storage
event = {
    'title': 'Test Event',
    'date': '2024-12-15',
    'time': '14:00',
    'duration': '1 hour'
}
event_id = db.save_event(event)
print(f"✅ Event saved with ID: {event_id}")

# Test retrieval
cards = db.get_recent_flashcards(5)
print(f"✅ Retrieved {len(cards)} flashcards")

db.close()
print("✅ Database MCP working correctly!")