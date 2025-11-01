"""
Prompt Templates - Structured prompts for model inference.
Contains templates for summarization, flashcard generation, and planning.
"""


class PromptTemplates:
    """Collection of prompt templates for various tasks."""
    
    @staticmethod
    def get_summary_prompt(content: str) -> str:
        """
        Generate prompt for lecture summarization.
        
        Args:
            content: Lecture content to summarize
            
        Returns:
            Formatted prompt
        """
        return f"""You are an expert educational content summarizer. Your task is to create a concise, accurate summary of the following lecture content.

Guidelines:
- Extract only the most important concepts and key points
- Maintain factual accuracy
- Use clear, concise language
- Organize information logically
- Length: 3-5 sentences

Lecture Content:
{content}

Summary:"""
    
    @staticmethod
    def get_flashcard_prompt(content: str, summary: str = "") -> str:
        """
        Generate prompt for flashcard creation.
        
        Args:
            content: Lecture content
            summary: Optional summary for context
            
        Returns:
            Formatted prompt
        """
        context_section = f"\n\nSummary:\n{summary}" if summary else ""
        
        return f"""You are an expert educational content creator. Generate high-quality flashcards from the following lecture content.

Guidelines:
- Create clear, specific questions
- Provide complete, accurate answers
- Focus on key concepts, definitions, and relationships
- Mix different question types (definitions, applications, comparisons)
- Format: Return as JSON array with 'question', 'answer', and 'category' fields

Lecture Content:
{content}{context_section}

Flashcards (JSON format):
["""
    
    @staticmethod
    def get_planning_prompt(goals: str, constraints: str) -> str:
        """
        Generate prompt for study planning.
        
        Args:
            goals: Study goals and objectives
            constraints: Time and resource constraints
            
        Returns:
            Formatted prompt
        """
        return f"""You are an expert study planner. Create an effective, personalized study schedule.

Study Goals:
{goals}

Constraints:
{constraints}

Create a day-by-day study plan that:
- Distributes topics effectively across available time
- Includes regular review sessions
- Balances different subjects
- Incorporates breaks
- Adapts to difficulty levels

Study Plan:"""
    
    @staticmethod
    def get_evaluation_prompt(content: str, reference: str) -> str:
        """
        Generate prompt for content evaluation.
        
        Args:
            content: Content to evaluate
            reference: Reference or ground truth
            
        Returns:
            Formatted prompt
        """
        return f"""Evaluate the following generated content against the reference.

Rate on a scale of 0-1 for:
1. Accuracy: Factual correctness
2. Completeness: Coverage of key points
3. Clarity: Readability and comprehension
4. Relevance: Focus on important information

Generated Content:
{content}

Reference:
{reference}

Evaluation (JSON format):
{{"""
    
    @staticmethod
    def get_intent_detection_prompt(user_input: str) -> str:
        """
        Generate prompt for intent detection.
        
        Args:
            user_input: User's natural language input
            
        Returns:
            Formatted prompt for intent classification
        """
        return f"""You are an AI assistant that classifies user requests into specific intents.

Possible intents:
- calendar: Scheduling, creating events, viewing calendar
- summarize: Summarizing content, generating notes, creating flashcards
- plan: Creating study plans, organizing learning schedule
- evaluate: Assessing quality, checking performance metrics
- general: General questions or unclear intent

User Input:
{user_input}

Classify the intent. Respond with only one word from the list above:"""
    
    @staticmethod
    def get_topic_extraction_prompt(text: str) -> str:
        """
        Generate prompt for extracting study topics from text.
        
        Args:
            text: Text containing topic information
            
        Returns:
            Formatted prompt for topic extraction
        """
        return f"""Extract the main study topics or subjects from the following text.

Instructions:
- List only the core academic subjects or topics
- Use standard subject names (e.g., "Calculus", "Physics", "History")
- Return as a comma-separated list
- If no clear topics, return "General Study"

Text:
{text}

Topics (comma-separated):"""
    
    @staticmethod
    def get_deadline_extraction_prompt(text: str) -> str:
        """
        Generate prompt for extracting deadlines from text.
        
        Args:
            text: Text containing deadline information
            
        Returns:
            Formatted prompt for deadline extraction
        """
        return f"""Extract deadline or due date information from the following text.

Instructions:
- Identify any time references (dates, relative times like "next week")
- Convert to specific date format if possible
- If no deadline mentioned, return "None"

Text:
{text}

Deadline:"""
    
    @staticmethod
    def get_difficulty_assessment_prompt(content: str) -> str:
        """
        Generate prompt for assessing content difficulty.
        
        Args:
            content: Educational content to assess
            
        Returns:
            Formatted prompt for difficulty assessment
        """
        return f"""Assess the difficulty level of the following educational content.

Rate from 1-10 where:
1-3: Beginner (basic concepts, introductory material)
4-6: Intermediate (moderate complexity, some prerequisites)
7-10: Advanced (complex concepts, significant prerequisites)

Content:
{content}

Provide only a number from 1-10:"""
    
    @staticmethod
    def get_event_parsing_prompt(user_input: str) -> str:
        """
        Generate prompt for parsing calendar event details.
        
        Args:
            user_input: Natural language event description
            
        Returns:
            Formatted prompt for structured event extraction
        """
        return f"""Parse the following natural language event description into structured data.

Extract:
- title: Event name/description
- date: Date of event (YYYY-MM-DD format or relative like "tomorrow")
- time: Time of event (HH:MM format or "all day")
- duration: Length of event (e.g., "1 hour", "30 minutes")
- description: Additional details

Input:
{user_input}

Return as JSON:
{{"""
    
    @staticmethod
    def get_study_time_estimation_prompt(topic: str, current_level: str) -> str:
        """
        Generate prompt for estimating study time needed.
        
        Args:
            topic: Subject or topic name
            current_level: Current knowledge level (beginner/intermediate/advanced)
            
        Returns:
            Formatted prompt for time estimation
        """
        return f"""Estimate the study time needed to master the following topic.

Topic: {topic}
Current Level: {current_level}

Consider:
- Complexity of the topic
- Typical learning curve
- Current knowledge level

Provide estimation in hours (integer):"""
    
    @staticmethod
    def get_flashcard_quality_prompt(question: str, answer: str) -> str:
        """
        Generate prompt for evaluating flashcard quality.
        
        Args:
            question: Flashcard question
            answer: Flashcard answer
            
        Returns:
            Formatted prompt for quality assessment
        """
        return f"""Evaluate the quality of this flashcard.

Question: {question}
Answer: {answer}

Rate from 0-1 for:
- Clarity: Is the question clear and unambiguous?
- Completeness: Is the answer complete and accurate?
- Educational Value: Does it effectively test understanding?

Return as JSON:
{{"""
    
    @staticmethod
    def get_summary_refinement_prompt(original_summary: str, feedback: str) -> str:
        """
        Generate prompt for refining a summary based on feedback.
        
        Args:
            original_summary: Initial summary
            feedback: User feedback or requirements
            
        Returns:
            Formatted prompt for summary improvement
        """
        return f"""Refine the following summary based on the feedback provided.

Original Summary:
{original_summary}

Feedback:
{feedback}

Improved Summary:"""
    
    @staticmethod
    def get_study_goal_clarification_prompt(vague_goal: str) -> str:
        """
        Generate prompt for clarifying vague study goals.
        
        Args:
            vague_goal: User's initial goal description
            
        Returns:
            Formatted prompt for goal clarification
        """
        return f"""The user has provided a study goal, but it needs clarification.

User's Goal: {vague_goal}

Generate 3-5 clarifying questions to better understand:
- Specific topics to study
- Timeline and deadlines
- Current knowledge level
- Available study time
- Learning objectives

Questions:"""
    
    @staticmethod
    def get_spaced_repetition_prompt(topic: str, last_reviewed: str, performance: str) -> str:
        """
        Generate prompt for spaced repetition scheduling.
        
        Args:
            topic: Subject or topic
            last_reviewed: Date last reviewed
            performance: Performance score (poor/fair/good/excellent)
            
        Returns:
            Formatted prompt for next review scheduling
        """
        return f"""Determine the optimal next review date for spaced repetition learning.

Topic: {topic}
Last Reviewed: {last_reviewed}
Performance: {performance}

Using spaced repetition principles:
- Poor: Review in 1 day
- Fair: Review in 3 days
- Good: Review in 7 days
- Excellent: Review in 14 days

Next Review Date:"""
    
    @staticmethod
    def get_learning_style_prompt(user_preferences: str) -> str:
        """
        Generate prompt for identifying learning style preferences.
        
        Args:
            user_preferences: Description of study preferences
            
        Returns:
            Formatted prompt for learning style analysis
        """
        return f"""Analyze the following study preferences to identify the primary learning style.

User Preferences:
{user_preferences}

Learning Styles:
- Visual: Prefers diagrams, charts, visual aids
- Auditory: Prefers lectures, discussions, verbal explanations
- Reading/Writing: Prefers text-based learning, notes
- Kinesthetic: Prefers hands-on, practical application

Primary Learning Style:"""
    
    @staticmethod
    def get_concept_connection_prompt(topic1: str, topic2: str) -> str:
        """
        Generate prompt for finding connections between topics.
        
        Args:
            topic1: First topic
            topic2: Second topic
            
        Returns:
            Formatted prompt for concept connection
        """
        return f"""Identify connections and relationships between these two topics.

Topic 1: {topic1}
Topic 2: {topic2}

Describe:
- How they relate to each other
- Shared concepts or principles
- How understanding one helps understand the other
- Practical applications that involve both

Connections:"""
    
    @staticmethod
    def get_prerequisite_identification_prompt(topic: str) -> str:
        """
        Generate prompt for identifying topic prerequisites.
        
        Args:
            topic: Main topic to study
            
        Returns:
            Formatted prompt for prerequisite identification
        """
        return f"""Identify the prerequisite knowledge needed to study this topic effectively.

Topic: {topic}

List the foundational concepts or subjects that should be learned first:
- Core prerequisites (essential)
- Recommended background (helpful but not essential)

Prerequisites:"""
    
    @staticmethod
    def get_practice_problem_prompt(topic: str, difficulty: str) -> str:
        """
        Generate prompt for creating practice problems.
        
        Args:
            topic: Subject topic
            difficulty: Difficulty level (easy/medium/hard)
            
        Returns:
            Formatted prompt for problem generation
        """
        return f"""Create a practice problem for the following topic.

Topic: {topic}
Difficulty: {difficulty}

Generate:
- A clear problem statement
- Step-by-step solution
- Key concepts being tested

Problem:"""
    
    @staticmethod
    def get_progress_tracking_prompt(completed_tasks: str, remaining_tasks: str) -> str:
        """
        Generate prompt for progress analysis.
        
        Args:
            completed_tasks: Description of completed work
            remaining_tasks: Description of remaining work
            
        Returns:
            Formatted prompt for progress assessment
        """
        return f"""Analyze study progress and provide motivational feedback.

Completed:
{completed_tasks}

Remaining:
{remaining_tasks}

Provide:
- Progress percentage estimate
- Encouraging feedback
- Recommendations for maintaining momentum

Progress Analysis:"""
    
    @staticmethod
    def build_system_prompt() -> str:
        """
        Build the system prompt for the AI assistant.
        
        Returns:
            Comprehensive system prompt
        """
        return """You are ScholarMate, an AI-powered academic assistant designed to help students succeed.

Your capabilities:
- Summarizing lecture notes and educational content
- Generating study flashcards from any topic
- Creating personalized study schedules
- Managing academic calendars and deadlines
- Evaluating learning progress
- Providing study recommendations

Your principles:
- Accuracy: Provide factually correct information
- Clarity: Use clear, student-friendly language
- Personalization: Adapt to individual learning needs
- Encouragement: Support and motivate students
- Efficiency: Respect students' time

When interacting:
- Be concise but thorough
- Ask clarifying questions when needed
- Provide actionable advice
- Use examples when helpful
- Stay focused on educational goals"""
    
    @staticmethod
    def get_context_aware_prompt(user_input: str, context: dict) -> str:
        """
        Generate context-aware prompt incorporating user history.
        
        Args:
            user_input: Current user request
            context: Dictionary with user context (history, preferences, etc.)
            
        Returns:
            Enhanced prompt with context
        """
        context_info = []
        
        if context.get('recent_topics'):
            context_info.append(f"Recent topics studied: {', '.join(context['recent_topics'])}")
        
        if context.get('study_preferences'):
            context_info.append(f"Study preferences: {context['study_preferences']}")
        
        if context.get('upcoming_deadlines'):
            context_info.append(f"Upcoming deadlines: {context['upcoming_deadlines']}")
        
        context_section = "\n".join(context_info) if context_info else "No additional context available."
        
        return f"""User Context:
{context_section}

Current Request:
{user_input}

Provide a personalized response considering the user's context:"""