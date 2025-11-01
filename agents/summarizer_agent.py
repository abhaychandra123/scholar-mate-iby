"""
Summarizer Agent - Generates lecture summaries and flashcards.
Uses fine-tuned LoRA model for high-quality educational content generation.
"""

import logging
from typing import Dict, Any, Optional, List
import json
import re
import os

logger = logging.getLogger(__name__)


class SummarizerAgent:
    """
    Handles lecture summarization and flashcard generation.
    Uses fine-tuned model for educational content processing.
    """
    
    def __init__(self):
        """Initialize summarizer with model inference."""
        try:
            from models.inference import ModelInference
            self.model = ModelInference()
            logger.info("Summarizer agent initialized with fine-tuned model")
        except Exception as e:
            logger.warning(f"Model not available, using fallback: {e}")
            self.model = None
    
    def generate_summary_and_flashcards(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate summary and flashcards from lecture content.
        
        Args:
            user_input: Lecture text or file path
            context: Additional context (subject, difficulty level, etc.)
            
        Returns:
            Dictionary with summary and flashcards
        """
        try:
            # Extract lecture content
            lecture_content = self._extract_content(user_input, context)
            
            if not lecture_content:
                return {
                    'success': False,
                    'message': 'No content found to summarize'
                }
            
            # Check content length
            word_count = len(lecture_content.split())
            if word_count < 50:
                return {
                    'success': False,
                    'message': f'Content too short ({word_count} words). Please provide at least 50 words.'
                }
            
            # Generate summary
            summary = self._generate_summary(lecture_content)
            
            # Generate flashcards
            flashcards = self._generate_flashcards(lecture_content, summary)
            
            # Save to database
            self._save_results(summary, flashcards, lecture_content)
            
            return {
                'success': True,
                'message': f'Generated summary and {len(flashcards)} flashcards',
                'summary': summary,
                'flashcards': flashcards,
                'word_count': word_count,
                'original_length': word_count,
                'summary_length': len(summary.split())
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {'success': False, 'message': f'Summarization error: {str(e)}'}
    
    def _extract_content(self, user_input: str, context: Optional[Dict]) -> str:
        """
        Extract lecture content from input.
        
        Handles:
        - Direct text input
        - File paths (PDF, TXT, DOCX)
        - URLs (future enhancement)
        """
        # Check if input is a file path
        if user_input.startswith('Summarize file:'):
            file_path = user_input.replace('Summarize file:', '').strip()
            return self._read_file(file_path)
        
        # Check if input looks like a file path
        if os.path.exists(user_input):
            return self._read_file(user_input)
        
        # Otherwise, treat as direct text
        return user_input.strip()
    
    def _read_file(self, file_path: str) -> str:
        """Read content from various file formats."""
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif file_extension == '.pdf':
                from mcp.pdf_parser_tool import PDFParser
                parser = PDFParser()
                return parser.extract_text(file_path)
            
            elif file_extension in ['.docx', '.doc']:
                # Simple docx reading
                try:
                    import docx
                    doc = docx.Document(file_path)
                    return '\n'.join([para.text for para in doc.paragraphs])
                except ImportError:
                    logger.warning("docx library not available")
                    return ""
            
            else:
                logger.warning(f"Unsupported file type: {file_extension}")
                return ""
                
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return ""
    
    def _generate_summary(self, content: str) -> str:
        """
        Generate concise summary of lecture content.
        
        Uses fine-tuned model if available, otherwise uses rule-based approach.
        """
        if self.model:
            try:
                prompt = self._build_summary_prompt(content)
                summary = self.model.generate_summary(prompt)
                return summary
            except Exception as e:
                logger.error(f"Model generation failed: {e}")
                return self._fallback_summary(content)
        else:
            return self._fallback_summary(content)
    
    def _build_summary_prompt(self, content: str) -> str:
        """Build prompt for model inference."""
        from utils.prompts import PromptTemplates
        return PromptTemplates.get_summary_prompt(content)
    
    def _fallback_summary(self, content: str) -> str:
        """
        Rule-based summarization fallback.
        
        Extracts key sentences based on:
        - Position (first sentences of paragraphs)
        - Keywords (important, key, main, significant)
        - Sentence length
        """
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # Score sentences
        scored_sentences = []
        keywords = ['important', 'key', 'main', 'significant', 'critical', 
                   'essential', 'fundamental', 'primary', 'crucial']
        
        for idx, sentence in enumerate(sentences):
            score = 0
            
            # Position score (first sentences are often important)
            if idx < 3:
                score += 2
            
            # Keyword score
            for keyword in keywords:
                if keyword in sentence.lower():
                    score += 1
            
            # Length score (prefer medium-length sentences)
            word_count = len(sentence.split())
            if 10 <= word_count <= 30:
                score += 1
            
            scored_sentences.append((score, sentence))
        
        # Select top sentences
        scored_sentences.sort(reverse=True, key=lambda x: x[0])
        summary_sentences = [s[1] for s in scored_sentences[:5]]
        
        # Reconstruct summary
        summary = '. '.join(summary_sentences)
        if not summary.endswith('.'):
            summary += '.'
        
        return summary
    
    def _generate_flashcards(self, content: str, summary: str) -> List[Dict[str, str]]:
        """
        Generate flashcards from lecture content.
        
        Creates Q&A pairs focusing on:
        - Definitions
        - Key concepts
        - Relationships
        - Examples
        """
        if self.model:
            try:
                prompt = self._build_flashcard_prompt(content, summary)
                flashcards = self.model.generate_flashcards(prompt)
                return flashcards
            except Exception as e:
                logger.error(f"Model flashcard generation failed: {e}")
                return self._fallback_flashcards(content)
        else:
            return self._fallback_flashcards(content)
    
    def _build_flashcard_prompt(self, content: str, summary: str) -> str:
        """Build prompt for flashcard generation."""
        from utils.prompts import PromptTemplates
        return PromptTemplates.get_flashcard_prompt(content, summary)
    
    def _fallback_flashcards(self, content: str) -> List[Dict[str, str]]:
        """
        Rule-based flashcard generation fallback.
        
        Extracts definitions, terms, and concepts.
        """
        flashcards = []
        
        # Pattern 1: "X is Y" or "X: Y" (definitions)
        definition_patterns = [
            r'([A-Z][a-zA-Z\s]{2,30})\s+is\s+([^.!?]{10,100})',
            r'([A-Z][a-zA-Z\s]{2,30}):\s+([^.!?]{10,100})',
            r'([A-Z][a-zA-Z\s]{2,30})\s+refers to\s+([^.!?]{10,100})',
            r'([A-Z][a-zA-Z\s]{2,30})\s+means\s+([^.!?]{10,100})'
        ]
        
        for pattern in definition_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                term = match.group(1).strip()
                definition = match.group(2).strip()
                
                flashcards.append({
                    'question': f'What is {term}?',
                    'answer': definition,
                    'category': 'definition'
                })
        
        # Pattern 2: Extract questions from content
        question_pattern = r'(What|How|Why|When|Where|Who)[^?]{5,80}\?'
        questions = re.finditer(question_pattern, content)
        
        for match in questions[:3]:  # Limit to 3 questions
            question = match.group(0).strip()
            # Try to find answer in following text
            answer = self._extract_answer_near_question(content, match.end())
            
            if answer:
                flashcards.append({
                    'question': question,
                    'answer': answer,
                    'category': 'comprehension'
                })
        
        # Pattern 3: Key terms (capitalized words that appear multiple times)
        words = re.findall(r'\b[A-Z][a-z]{2,}\b', content)
        word_freq = {}
        for word in words:
            if word not in ['The', 'This', 'That', 'These', 'Those']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Create flashcards for frequent terms
        important_terms = [word for word, freq in word_freq.items() if freq >= 2]
        for term in important_terms[:5]:  # Limit to 5 terms
            # Find sentence containing the term
            pattern = re.compile(rf'\b{re.escape(term)}\b[^.!?]*[.!?]')
            match = pattern.search(content)
            if match:
                context = match.group(0).strip()
                flashcards.append({
                    'question': f'Explain the concept of {term}',
                    'answer': context,
                    'category': 'concept'
                })
        
        # Ensure we have at least a few flashcards
        if len(flashcards) < 3:
            # Generate generic flashcards from first few sentences
            sentences = re.split(r'[.!?]+', content)
            for i, sentence in enumerate(sentences[:3]):
                if len(sentence.split()) > 10:
                    flashcards.append({
                        'question': f'What is discussed in point {i+1}?',
                        'answer': sentence.strip(),
                        'category': 'general'
                    })
        
        # Remove duplicates and limit total
        unique_flashcards = []
        seen_questions = set()
        
        for card in flashcards:
            q_normalized = card['question'].lower().strip()
            if q_normalized not in seen_questions:
                seen_questions.add(q_normalized)
                unique_flashcards.append(card)
        
        return unique_flashcards[:10]  # Max 10 flashcards
    
    def _extract_answer_near_question(self, content: str, position: int) -> str:
        """Extract potential answer following a question."""
        # Get next 200 characters
        following_text = content[position:position + 200]
        
        # Extract first complete sentence
        sentence_match = re.search(r'^[^.!?]*[.!?]', following_text)
        if sentence_match:
            return sentence_match.group(0).strip()
        
        return ""
    
    def _save_results(self, summary: str, flashcards: List[Dict], original_content: str):
        """Save summary and flashcards to database."""
        try:
            from mcp.database_tool import DatabaseTool
            db = DatabaseTool()
            
            # Save summary
            db.save_summary({
                'content': summary,
                'original_length': len(original_content.split()),
                'summary_length': len(summary.split()),
                'timestamp': None  # Will be auto-generated
            })
            
            # Save flashcards
            for card in flashcards:
                db.save_flashcard(card)
            
            logger.info(f"Saved summary and {len(flashcards)} flashcards")
            
        except Exception as e:
            logger.warning(f"Failed to save results: {e}")
    
    def evaluate_flashcard_quality(self, flashcards: List[Dict]) -> Dict[str, Any]:
        """
        Evaluate quality of generated flashcards.
        
        Metrics:
        - Clarity (question clarity)
        - Completeness (answer completeness)
        - Relevance (topic relevance)
        """
        if not flashcards:
            return {'average_score': 0, 'metrics': {}}
        
        scores = []
        
        for card in flashcards:
            question_score = self._score_question(card['question'])
            answer_score = self._score_answer(card['answer'])
            
            total_score = (question_score + answer_score) / 2
            scores.append(total_score)
        
        return {
            'average_score': sum(scores) / len(scores),
            'num_flashcards': len(flashcards),
            'metrics': {
                'clarity': sum(scores) / len(scores),
                'completeness': 0.8,  # Placeholder
                'relevance': 0.85  # Placeholder
            }
        }
    
    def _score_question(self, question: str) -> float:
        """Score question quality (0-1)."""
        score = 0.5  # Base score
        
        # Has question word
        if any(word in question.lower() for word in ['what', 'how', 'why', 'when', 'where', 'who']):
            score += 0.2
        
        # Ends with question mark
        if question.strip().endswith('?'):
            score += 0.1
        
        # Appropriate length
        word_count = len(question.split())
        if 5 <= word_count <= 20:
            score += 0.2
        
        return min(score, 1.0)
    
    def _score_answer(self, answer: str) -> float:
        """Score answer quality (0-1)."""
        score = 0.5  # Base score
        
        # Appropriate length
        word_count = len(answer.split())
        if 5 <= word_count <= 50:
            score += 0.3
        elif word_count > 50:
            score += 0.2
        
        # Has proper punctuation
        if answer.strip().endswith('.'):
            score += 0.2
        
        return min(score, 1.0)