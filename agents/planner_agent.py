"""
Planner Agent - Generates adaptive study schedules.
Creates personalized study plans based on deadlines, topics, and user preferences.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class PlannerAgent:
    """
    Handles study plan generation and optimization.
    Creates adaptive schedules based on:
    - Upcoming deadlines
    - Topic difficulty
    - Available study time
    - Past performance
    """
    
    def __init__(self):
        """Initialize planner with default settings."""
        self.default_session_duration = 60  # minutes
        self.default_break_duration = 15  # minutes
        self.max_daily_hours = 8  # Maximum study hours per day
        
        logger.info("Planner agent initialized")
    
    def generate_study_plan(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized study plan.
        
        Args:
            user_input: Natural language description of study goals
            context: Additional context (courses, deadlines, preferences)
            
        Returns:
            Dictionary with structured study plan
        """
        try:
            # Parse study goals and constraints
            study_info = self._parse_study_request(user_input, context)
            
            if not study_info.get('topics'):
                return {
                    'success': False,
                    'message': 'Could not identify study topics. Please specify what you need to study.'
                }
            
            # Generate schedule
            plan = self._create_study_schedule(study_info)
            
            # Optimize plan
            optimized_plan = self._optimize_schedule(plan, study_info)
            
            # Sync with calendar if requested
            if study_info.get('sync_calendar', True):
                self._sync_to_calendar(optimized_plan)
            
            # Save plan
            self._save_plan(optimized_plan, study_info)
            
            return {
                'success': True,
                'message': f'Generated {len(optimized_plan)} day study plan',
                'plan': optimized_plan,
                'summary': self._generate_plan_summary(optimized_plan)
            }
            
        except Exception as e:
            logger.error(f"Error generating study plan: {e}")
            return {'success': False, 'message': f'Planning error: {str(e)}'}
    
    def _parse_study_request(self, user_input: str, context: Optional[Dict]) -> Dict[str, Any]:
        """
        Parse study request from natural language.
        
        Extracts:
        - Topics/subjects
        - Deadlines
        - Available time per day
        - Difficulty preferences
        """
        import re
        
        study_info = {
            'topics': [],
            'deadlines': {},
            'daily_hours': 3,  # default
            'start_date': datetime.now(),
            'sync_calendar': True
        }
        
        # Extract topics
        topics = self._extract_topics(user_input)
        study_info['topics'] = topics
        
        # Extract time availability
        time_match = re.search(r'(\d+)\s*hours?\s*(?:per\s*day|daily|each\s*day)', user_input.lower())
        if time_match:
            study_info['daily_hours'] = int(time_match.group(1))
        
        # Extract deadline
        deadline = self._extract_deadline(user_input)
        if deadline:
            study_info['deadline'] = deadline
            # Assign same deadline to all topics for now
            for topic in topics:
                study_info['deadlines'][topic] = deadline
        
        # Add context information
        if context:
            if 'topics' in context:
                study_info['topics'].extend(context['topics'])
            if 'daily_hours' in context:
                study_info['daily_hours'] = context['daily_hours']
        
        return study_info
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract study topics from text."""
        import re
        
        topics = []
        
        # Look for common academic subjects
        common_subjects = [
            'math', 'calculus', 'algebra', 'geometry', 'statistics',
            'physics', 'chemistry', 'biology', 'anatomy',
            'history', 'geography', 'literature', 'english',
            'computer science', 'programming', 'algorithms',
            'economics', 'psychology', 'sociology'
        ]
        
        text_lower = text.lower()
        for subject in common_subjects:
            if subject in text_lower:
                topics.append(subject.title())
        
        # Look for quoted or explicit topics
        quoted = re.findall(r'["\']([^"\']+)["\']', text)
        topics.extend(quoted)
        
        # If no topics found, try to extract from 'study X' pattern
        study_pattern = r'study\s+([a-zA-Z\s]{3,30})(?:\s+and|\s+for|\s+exam|$)'
        matches = re.findall(study_pattern, text_lower)
        for match in matches:
            topic = match.strip().title()
            if topic and topic not in topics:
                topics.append(topic)
        
        # Remove duplicates
        topics = list(set(topics))
        
        return topics if topics else ['General Study']
    
    def _extract_deadline(self, text: str) -> Optional[datetime]:
        """Extract deadline from natural language."""
        import re
        
        today = datetime.now()
        text_lower = text.lower()
        
        # Check for explicit dates
        if 'next week' in text_lower:
            return today + timedelta(days=7)
        elif 'two weeks' in text_lower:
            return today + timedelta(days=14)
        elif match := re.search(r'in\s+(\d+)\s+days?', text_lower):
            days = int(match.group(1))
            return today + timedelta(days=days)
        elif match := re.search(r'in\s+(\d+)\s+weeks?', text_lower):
            weeks = int(match.group(1))
            return today + timedelta(weeks=weeks)
        elif 'tomorrow' in text_lower:
            return today + timedelta(days=1)
        elif 'exam' in text_lower or 'test' in text_lower:
            # Default: assume exam is in 7 days
            return today + timedelta(days=7)
        
        return None
    
    def _create_study_schedule(self, study_info: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """
        Create initial study schedule.
        
        Distributes topics across available days.
        """
        topics = study_info['topics']
        daily_hours = study_info['daily_hours']
        start_date = study_info['start_date']
        deadline = study_info.get('deadline')
        
        # Calculate number of days available
        if deadline:
            days_available = (deadline - start_date).days
        else:
            days_available = 7  # Default to 1 week
        
        days_available = max(1, min(days_available, 14))  # Between 1-14 days
        
        # Calculate total study hours needed
        total_hours = len(topics) * 5  # 5 hours per topic (rough estimate)
        
        # Distribute across days
        schedule = {}
        current_date = start_date
        topic_index = 0
        hours_per_topic = total_hours / len(topics)
        
        for day in range(days_available):
            date_key = (current_date + timedelta(days=day)).strftime('%Y-%m-%d')
            day_name = (current_date + timedelta(days=day)).strftime('%A')
            
            daily_sessions = []
            remaining_hours = daily_hours
            
            # Morning session (9 AM)
            if remaining_hours >= 2:
                topic = topics[topic_index % len(topics)]
                daily_sessions.append({
                    'time': '09:00',
                    'activity': f'Study {topic}',
                    'duration': '2 hours',
                    'topic': topic,
                    'session_type': 'focused_study'
                })
                remaining_hours -= 2
            
            # Afternoon session (2 PM)
            if remaining_hours >= 2:
                topic = topics[(topic_index + 1) % len(topics)]
                daily_sessions.append({
                    'time': '14:00',
                    'activity': f'Study {topic}',
                    'duration': '2 hours',
                    'topic': topic,
                    'session_type': 'focused_study'
                })
                remaining_hours -= 2
                topic_index += 1
            
            # Evening review (7 PM)
            if remaining_hours >= 1:
                daily_sessions.append({
                    'time': '19:00',
                    'activity': 'Review and practice problems',
                    'duration': '1 hour',
                    'topic': 'Mixed Review',
                    'session_type': 'review'
                })
            
            schedule[day_name] = daily_sessions
        
        return schedule
    
    def _optimize_schedule(self, plan: Dict[str, List[Dict]], study_info: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """
        Optimize study schedule using principles:
        - Space repetition (review topics multiple times)
        - Mix topics to avoid cognitive fatigue
        - Include breaks
        - Prioritize difficult topics early in day
        """
        optimized = {}
        
        for day, sessions in plan.items():
            optimized_sessions = []
            
            for session in sessions:
                optimized_sessions.append(session)
                
                # Add break after each study session
                if session['session_type'] == 'focused_study':
                    optimized_sessions.append({
                        'time': self._add_minutes_to_time(session['time'], 120),
                        'activity': 'Break',
                        'duration': '15 minutes',
                        'topic': 'Rest',
                        'session_type': 'break'
                    })
            
            optimized[day] = optimized_sessions
        
        return optimized
    
    def _add_minutes_to_time(self, time_str: str, minutes: int) -> str:
        """Add minutes to time string (HH:MM format)."""
        try:
            time_obj = datetime.strptime(time_str, '%H:%M')
            new_time = time_obj + timedelta(minutes=minutes)
            return new_time.strftime('%H:%M')
        except:
            return time_str
    
    def _sync_to_calendar(self, plan: Dict[str, List[Dict]]):
        """Sync study plan to calendar via Calendar Agent."""
        try:
            from agents.calendar_agent import CalendarAgent
            calendar_agent = CalendarAgent()
            
            for day, sessions in plan.items():
                for session in sessions:
                    if session['session_type'] in ['focused_study', 'review']:
                        # Create calendar event
                        event_description = f"{session['activity']} - {day}"
                        calendar_agent.process_calendar_request(
                            f"Schedule {event_description} at {session['time']}",
                            context={'duration': session['duration']}
                        )
            
            logger.info("Study plan synced to calendar")
            
        except Exception as e:
            logger.warning(f"Failed to sync to calendar: {e}")
    
    def _save_plan(self, plan: Dict[str, List[Dict]], study_info: Dict[str, Any]):
        """Save study plan to database."""
        try:
            from mcp.database_tool import DatabaseTool
            db = DatabaseTool()
            
            plan_data = {
                'plan': plan,
                'study_info': study_info,
                'created_at': datetime.now().isoformat(),
                'status': 'active'
            }
            
            db.save_study_plan(plan_data)
            logger.info("Study plan saved to database")
            
        except Exception as e:
            logger.warning(f"Failed to save plan: {e}")
    
    def _generate_plan_summary(self, plan: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Generate summary statistics for the plan."""
        total_sessions = sum(len(sessions) for sessions in plan.values())
        study_sessions = sum(
            1 for sessions in plan.values()
            for session in sessions
            if session['session_type'] in ['focused_study', 'review']
        )
        
        topics_covered = set()
        for sessions in plan.values():
            for session in sessions:
                if session.get('topic') and session['topic'] != 'Rest':
                    topics_covered.add(session['topic'])
        
        return {
            'total_days': len(plan),
            'total_sessions': total_sessions,
            'study_sessions': study_sessions,
            'topics_covered': list(topics_covered),
            'estimated_hours': study_sessions * 2  # Rough estimate
        }