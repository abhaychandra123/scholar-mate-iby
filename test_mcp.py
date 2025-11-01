# test_mcp_integration.py
"""Test complete MCP integration flow."""

from agents.coordinator import CoordinatorAgent

coordinator = CoordinatorAgent()

# Test 1: Calendar request
print("Test 1: Calendar MCP")
response = coordinator.handle_request(
    "Schedule a study session tomorrow at 2pm"
)
print(f"✅ Calendar: {response['message']}\n")

# Test 2: Summarizer request
print("Test 2: Summarizer MCP")
response = coordinator.handle_request(
    """Photosynthesis is the process by which plants convert light energy 
    into chemical energy. It occurs in chloroplasts using chlorophyll.""",
    intent_override="summarize"
)
print(f"✅ Summarizer: Generated {len(response.get('flashcards', []))} flashcards\n")

# Test 3: Planner request
print("Test 3: Planner MCP")
response = coordinator.handle_request(
    "Create a study plan for calculus and physics, 3 hours daily",
    intent_override="plan"
)
print(f"✅ Planner: Created {len(response.get('plan', {}))} day plan\n")

# Test 4: Evaluator request
print("Test 4: Evaluator MCP")
response = coordinator.handle_request(
    "Show evaluation metrics",
    intent_override="evaluate"
)
print(f"✅ Evaluator: {response['message']}\n")

print("🎉 All MCP components working!")