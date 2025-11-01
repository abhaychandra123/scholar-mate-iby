"""
Coordinator Agent - Entry point for all user requests.
Routes requests to appropriate specialized agents based on intent detection.
"""

import re
from typing import Dict, Any, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CoordinatorAgent:
    """
    Central coordinator that analyzes user input and routes to appropriate agents.
    Implements intent detection and response aggregation.
    """
    
    def __init__(self):
        """Initialize coordinator with agent registry."""
        self.agents = {}
        self._initialize_agents()
        
        # Intent patterns for routing
        self.intent_patterns = {
            'calendar': [
                r'schedule', r'calendar', r'event', r'meeting', r'appointment',
                r'remind', r'book', r'reserve', r'plan.*time'
            ],
            'summarize': [
                r'summarize', r'summary', r'flashcard', r'notes', r'lecture',
                r'study.*material', r'key.*points', r'review'
            ],
            'plan': [
                r'study.*plan', r'schedule.*study', r'organize.*study',
                r'learning.*plan', r'preparation.*schedule'
            ],
            'evaluate': [
                r'evaluate', r'assessment', r'quality', r'performance',
                r'metrics', r'score'
            ]
        }
    
    def _initialize_agents(self):
        """Lazy load agents to avoid circular imports."""
        try:
            from agents.calendar_agent import CalendarAgent
            from agents.summarizer_agent import SummarizerAgent
            from agents.planner_agent import PlannerAgent
            from agents.evaluator_agent import EvaluatorAgent
            
            self.agents['calendar'] = CalendarAgent()
            self.agents['summarize'] = SummarizerAgent()
            self.agents['plan'] = PlannerAgent()
            self.agents['evaluate'] = EvaluatorAgent()
            
            logger.info("All agents initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing agents: {e}")
    
    def detect_intent(self, user_input: str) -> str:
        """
        Detect user intent from natural language input.
        
        Args:
            user_input: Raw user text
            
        Returns:
            Intent category: 'calendar', 'summarize', 'plan', 'evaluate', or 'general'
        """
        user_input_lower = user_input.lower()
        
        # Score each intent
        intent_scores = {}
        for intent, patterns in self.intent_patterns.items():
            score = sum(1 for pattern in patterns if re.search(pattern, user_input_lower))
            intent_scores[intent] = score
        
        # Return highest scoring intent
        if max(intent_scores.values()) > 0:
            detected_intent = max(intent_scores, key=intent_scores.get)
            logger.info(f"Detected intent: {detected_intent} for input: {user_input[:50]}...")
            return detected_intent
        
        logger.info(f"No specific intent detected for: {user_input[:50]}...")
        return 'general'
    
    def handle_request(
        self,
        user_input: str,
        intent_override: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for handling user requests.
        
        Args:
            user_input: User's natural language request
            intent_override: Force specific intent (for UI buttons)
            context: Additional context data
            
        Returns:
            Response dictionary with results and metadata
        """
        try:
            # Detect or use provided intent
            intent = intent_override if intent_override else self.detect_intent(user_input)
            
            logger.info(f"Processing request with intent: {intent}")
            
            # Route to appropriate agent
            if intent == 'calendar':
                response = self._handle_calendar(user_input, context)
            elif intent == 'summarize':
                response = self._handle_summarize(user_input, context)
            elif intent == 'plan':
                response = self._handle_plan(user_input, context)
            elif intent == 'evaluate':
                response = self._handle_evaluate(user_input, context)
            else:
                response = self._handle_general(user_input)
            
            # Add metadata
            response['intent'] = intent
            response['timestamp'] = datetime.now().isoformat()
            response['input'] = user_input
            
            # Log interaction
            self._log_interaction(user_input, intent, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                'success': False,
                'message': f'Error processing request: {str(e)}',
                'error': str(e)
            }
    
    def _handle_calendar(self, user_input: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Route to Calendar Agent."""
        try:
            agent = self.agents.get('calendar')
            if not agent:
                return {'success': False, 'message': 'Calendar agent not available'}
            
            result = agent.process_calendar_request(user_input, context)
            return result
        except Exception as e:
            logger.error(f"Calendar agent error: {e}")
            return {'success': False, 'message': f'Calendar error: {str(e)}'}
    
    def _handle_summarize(self, user_input: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Route to Summarizer Agent."""
        try:
            agent = self.agents.get('summarize')
            if not agent:
                return {'success': False, 'message': 'Summarizer agent not available'}
            
            result = agent.generate_summary_and_flashcards(user_input, context)
            return result
        except Exception as e:
            logger.error(f"Summarizer agent error: {e}")
            return {'success': False, 'message': f'Summarizer error: {str(e)}'}
    
    def _handle_plan(self, user_input: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Route to Planner Agent."""
        try:
            agent = self.agents.get('plan')
            if not agent:
                return {'success': False, 'message': 'Planner agent not available'}
            
            result = agent.generate_study_plan(user_input, context)
            return result
        except Exception as e:
            logger.error(f"Planner agent error: {e}")
            return {'success': False, 'message': f'Planner error: {str(e)}'}
    
    def _handle_evaluate(self, user_input: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Route to Evaluator Agent."""
        try:
            agent = self.agents.get('evaluate')
            if not agent:
                return {'success': False, 'message': 'Evaluator agent not available'}
            
            result = agent.evaluate_output(user_input, context)
            return result
        except Exception as e:
            logger.error(f"Evaluator agent error: {e}")
            return {'success': False, 'message': f'Evaluator error: {str(e)}'}
    
    def _handle_general(self, user_input: str) -> Dict[str, Any]:
        """Handle general queries without specific agent."""
        return {
            'success': True,
            'message': f"I received your message: '{user_input}'. Could you please be more specific about what you'd like me to help with? I can help with scheduling, summarizing lectures, creating study plans, or evaluating content.",
            'suggestions': [
                "Schedule a meeting",
                "Summarize these notes",
                "Create a study plan",
                "Show evaluation metrics"
            ]
        }
    
    def _log_interaction(self, user_input: str, intent: str, response: Dict[str, Any]):
        """Log interaction for evaluation and debugging."""
        try:
            from mcp.database_tool import DatabaseTool
            db = DatabaseTool()
            
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'input': user_input[:200],  # Truncate for storage
                'intent': intent,
                'success': response.get('success', False),
                'action': response.get('message', '')[:200]
            }
            
            db.log_interaction(log_entry)
        except Exception as e:
            logger.warning(f"Failed to log interaction: {e}")
    
    def get_agent_status(self) -> Dict[str, bool]:
        """Check status of all agents."""
        return {
            agent_name: agent is not None
            for agent_name, agent in self.agents.items()
        }