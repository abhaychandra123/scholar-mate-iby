"""
Scheduler Utilities - Helper functions for study plan optimization.
Implements scheduling algorithms and optimization strategies.
"""

import logging
from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)


class SchedulerUtils:
    """
    Utility functions for study schedule optimization.
    """
    
    @staticmethod
    def optimize_topic_distribution(
        topics: List[str],
        available_days: int,
        daily_hours: int
    ) -> Dict[str, List[Tuple[str, int]]]:
        """
        Distribute topics across available days optimally.
        
        Args:
            topics: List of topics to study
            available_days: Number of days available
            daily_hours: Hours available per day
            
        Returns:
            Dictionary mapping day to list of (topic, hours) tuples
        """
        schedule = {}
        
        # Calculate total hours and hours per topic
        total_hours = available_days * daily_hours
        hours_per_topic = max(1, total_hours // len(topics))
        
        # Distribute topics
        current_day = 0
        hours_remaining_today = daily_hours
        
        for topic in topics:
            topic_hours = hours_per_topic
            
            while topic_hours > 0:
                day_key = f"Day {current_day + 1}"
                
                if day_key not in schedule:
                    schedule[day_key] = []
                
                # Allocate hours for this day
                hours_to_allocate = min(topic_hours, hours_remaining_today)
                
                if hours_to_allocate > 0:
                    schedule[day_key].append((topic, hours_to_allocate))
                    topic_hours -= hours_to_allocate
                    hours_remaining_today -= hours_to_allocate
                
                # Move to next day if current day is full
                if hours_remaining_today <= 0:
                    current_day += 1
                    hours_remaining_today = daily_hours
                    
                    if current_day >= available_days:
                        break
            
            if current_day >= available_days:
                break
        
        return schedule
    
    @staticmethod
    def apply_spaced_repetition(
        schedule: Dict[str, List[Any]],
        topics: List[str]
    ) -> Dict[str, List[Any]]:
        """
        Apply spaced repetition principle to schedule.
        
        Adds review sessions at optimal intervals (1 day, 3 days, 7 days).
        """
        enhanced_schedule = schedule.copy()
        days = sorted(schedule.keys())
        
        # Track when each topic was first studied
        topic_first_appearance = {}
        
        for day in days:
            sessions = schedule[day]
            for session in sessions:
                if isinstance(session, dict):
                    topic = session.get('topic')
                elif isinstance(session, tuple):
                    topic = session[0]
                else:
                    continue
                
                if topic not in topic_first_appearance:
                    topic_first_appearance[topic] = day
        
        # Add review sessions
        for topic, first_day in topic_first_appearance.items():
            # Calculate review days (1, 3, 7 days after first study)
            review_intervals = [1, 3, 7]
            
            for interval in review_intervals:
                review_day_idx = days.index(first_day) + interval
                
                if review_day_idx < len(days):
                    review_day = days[review_day_idx]
                    
                    # Add review session
                    review_session = {
                        'time': '20:00',
                        'activity': f'Review {topic}',
                        'duration': '30 minutes',
                        'topic': topic,
                        'session_type': 'review'
                    }
                    
                    if review_day in enhanced_schedule:
                        enhanced_schedule[review_day].append(review_session)
        
        return enhanced_schedule
    
    @staticmethod
    def balance_cognitive_load(
        schedule: Dict[str, List[Any]],
        topic_difficulty: Dict[str, float]
    ) -> Dict[str, List[Any]]:
        """
        Balance cognitive load across days.
        
        Ensures difficult topics are spread out and not clustered together.
        
        Args:
            schedule: Current schedule
            topic_difficulty: Dictionary mapping topics to difficulty (0-1)
        """
        balanced_schedule = {}
        
        for day, sessions in schedule.items():
            day_sessions = []
            easy_sessions = []
            hard_sessions = []
            
            # Separate by difficulty
            for session in sessions:
                if isinstance(session, dict):
                    topic = session.get('topic', '')
                else:
                    continue
                
                difficulty = topic_difficulty.get(topic, 0.5)
                
                if difficulty > 0.7:
                    hard_sessions.append(session)
                else:
                    easy_sessions.append(session)
            
            # Interleave hard and easy sessions
            while hard_sessions or easy_sessions:
                if hard_sessions:
                    day_sessions.append(hard_sessions.pop(0))
                if easy_sessions:
                    day_sessions.append(easy_sessions.pop(0))
            
            balanced_schedule[day] = day_sessions
        
        return balanced_schedule
    
    @staticmethod
    def add_breaks(
        schedule: Dict[str, List[Any]],
        break_interval: int = 120  # minutes
    ) -> Dict[str, List[Any]]:
        """
        Add break sessions between study sessions.
        
        Args:
            schedule: Current schedule
            break_interval: Minutes between breaks
        """
        schedule_with_breaks = {}
        
        for day, sessions in schedule.items():
            enhanced_sessions = []
            
            for i, session in enumerate(sessions):
                enhanced_sessions.append(session)
                
                # Add break after study sessions (not after breaks themselves)
                if (isinstance(session, dict) and 
                    session.get('session_type') in ['focused_study', 'review'] and
                    i < len(sessions) - 1):  # Not last session
                    
                    break_session = {
                        'time': SchedulerUtils._add_minutes_to_time(session.get('time', '09:00'), break_interval),
                        'activity': 'Break',
                        'duration': '15 minutes',
                        'topic': 'Rest',
                        'session_type': 'break'
                    }
                    enhanced_sessions.append(break_session)
            
            schedule_with_breaks[day] = enhanced_sessions
        
        return schedule_with_breaks
    
    @staticmethod
    def _add_minutes_to_time(time_str: str, minutes: int) -> str:
        """Add minutes to time string."""
        try:
            time_obj = datetime.strptime(time_str, '%H:%M')
            new_time = time_obj + timedelta(minutes=minutes)
            return new_time.strftime('%H:%M')
        except:
            return time_str
    
    @staticmethod
    def prioritize_by_deadline(
        topics: List[str],
        deadlines: Dict[str, datetime]
    ) -> List[str]:
        """
        Sort topics by deadline urgency.
        
        Args:
            topics: List of topics
            deadlines: Dictionary mapping topics to deadline dates
            
        Returns:
            Sorted list of topics (most urgent first)
        """
        now = datetime.now()
        
        def urgency_score(topic):
            deadline = deadlines.get(topic)
            if not deadline:
                return float('inf')  # No deadline = lowest priority
            
            days_until = (deadline - now).days
            return days_until
        
        return sorted(topics, key=urgency_score)
    
    @staticmethod
    def calculate_optimal_session_length(
        difficulty: float,
        time_of_day: str
    ) -> int:
        """
        Calculate optimal study session length based on difficulty and time.
        
        Args:
            difficulty: Topic difficulty (0-1)
            time_of_day: Time string (e.g., '09:00')
            
        Returns:
            Recommended session length in minutes
        """
        base_length = 60  # Base session length in minutes
        
        # Adjust for difficulty
        if difficulty > 0.7:
            base_length = 45  # Shorter for difficult topics
        elif difficulty < 0.3:
            base_length = 90  # Longer for easier topics
        
        # Adjust for time of day
        try:
            hour = int(time_of_day.split(':')[0])
            
            # Morning (6-12): Optimal for difficult tasks
            if 6 <= hour < 12:
                base_length = int(base_length * 1.1)
            
            # Afternoon (12-18): Good for moderate tasks
            elif 12 <= hour < 18:
                base_length = base_length
            
            # Evening (18-22): Better for review
            elif 18 <= hour < 22:
                base_length = int(base_length * 0.9)
        except:
            pass
        
        return base_length
    
    @staticmethod
    def generate_time_slots(
        start_time: str,
        end_time: str,
        slot_duration: int
    ) -> List[str]:
        """
        Generate list of time slots between start and end time.
        
        Args:
            start_time: Start time (HH:MM)
            end_time: End time (HH:MM)
            slot_duration: Duration of each slot in minutes
            
        Returns:
            List of time strings
        """
        slots = []
        
        try:
            current = datetime.strptime(start_time, '%H:%M')
            end = datetime.strptime(end_time, '%H:%M')
            
            while current < end:
                slots.append(current.strftime('%H:%M'))
                current += timedelta(minutes=slot_duration)
        except Exception as e:
            logger.error(f"Error generating time slots: {e}")
        
        return slots
    
    @staticmethod
    def estimate_study_hours_needed(
        topic: str,
        difficulty: float,
        current_knowledge: float = 0.0
    ) -> int:
        """
        Estimate hours needed to master a topic.
        
        Args:
            topic: Topic name
            difficulty: Difficulty level (0-1)
            current_knowledge: Current knowledge level (0-1)
            
        Returns:
            Estimated hours needed
        """
        base_hours = 10  # Base hours for average topic
        
        # Adjust for difficulty
        difficulty_multiplier = 0.5 + (difficulty * 1.5)
        
        # Adjust for current knowledge
        knowledge_gap = 1.0 - current_knowledge
        
        estimated_hours = int(base_hours * difficulty_multiplier * knowledge_gap)
        
        return max(1, estimated_hours)  # At least 1 hour