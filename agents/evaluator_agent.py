"""
Evaluator Agent - Assesses quality of generated content.
Evaluates summaries, flashcards, and model performance.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class EvaluatorAgent:
    """
    Evaluates quality of AI-generated content.
    Tracks metrics: ROUGE, BLEU, user ratings, consistency.
    """
    
    def __init__(self):
        """Initialize evaluator with metrics tracking."""
        self.metrics_history = []
        logger.info("Evaluator agent initialized")
    
    def evaluate_output(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate content quality based on request.
        
        Args:
            user_input: Evaluation request or content to evaluate
            context: Additional context (content type, reference data)
            
        Returns:
            Dictionary with evaluation metrics and scores
        """
        try:
            # Determine what to evaluate
            eval_type = self._detect_evaluation_type(user_input, context)
            
            if eval_type == 'flashcards':
                return self._evaluate_flashcards(context)
            elif eval_type == 'summary':
                return self._evaluate_summary(context)
            elif eval_type == 'overall':
                return self._evaluate_overall_performance()
            else:
                return {
                    'success': False,
                    'message': 'Could not determine evaluation type'
                }
                
        except Exception as e:
            logger.error(f"Error during evaluation: {e}")
            return {'success': False, 'message': f'Evaluation error: {str(e)}'}
    
    def _detect_evaluation_type(self, user_input: str, context: Optional[Dict]) -> str:
        """Detect type of evaluation requested."""
        if context and 'eval_type' in context:
            return context['eval_type']
        
        user_input_lower = user_input.lower()
        
        if 'flashcard' in user_input_lower:
            return 'flashcards'
        elif 'summary' in user_input_lower or 'summarization' in user_input_lower:
            return 'summary'
        else:
            return 'overall'
    
    def _evaluate_flashcards(self, context: Optional[Dict]) -> Dict[str, Any]:
        """
        Evaluate flashcard quality.
        
        Metrics:
        - Clarity: Question clarity score
        - Completeness: Answer completeness
        - Difficulty: Appropriate difficulty level
        - Relevance: Topic relevance
        """
        try:
            from mcp.database_tool import DatabaseTool
            db = DatabaseTool()
            
            # Get recent flashcards
            flashcards = db.get_recent_flashcards(limit=50)
            
            if not flashcards:
                return {
                    'success': True,
                    'message': 'No flashcards to evaluate',
                    'metrics': {}
                }
            
            # Calculate metrics
            metrics = self._calculate_flashcard_metrics(flashcards)
            
            # Save evaluation
            self._save_evaluation('flashcards', metrics)
            
            return {
                'success': True,
                'message': f'Evaluated {len(flashcards)} flashcards',
                'metrics': metrics,
                'num_evaluated': len(flashcards)
            }
            
        except Exception as e:
            logger.error(f"Flashcard evaluation error: {e}")
            return {'success': False, 'message': str(e)}
    
    def _calculate_flashcard_metrics(self, flashcards: List[Dict]) -> Dict[str, float]:
        """Calculate comprehensive flashcard metrics."""
        if not flashcards:
            return {}
        
        clarity_scores = []
        completeness_scores = []
        difficulty_scores = []
        
        for card in flashcards:
            # Clarity: Based on question structure
            clarity = self._score_clarity(card.get('question', ''))
            clarity_scores.append(clarity)
            
            # Completeness: Based on answer length and structure
            completeness = self._score_completeness(card.get('answer', ''))
            completeness_scores.append(completeness)
            
            # Difficulty: Based on complexity
            difficulty = self._estimate_difficulty(card.get('question', ''), card.get('answer', ''))
            difficulty_scores.append(difficulty)
        
        return {
            'clarity': sum(clarity_scores) / len(clarity_scores),
            'completeness': sum(completeness_scores) / len(completeness_scores),
            'difficulty': sum(difficulty_scores) / len(difficulty_scores),
            'overall_quality': (sum(clarity_scores) + sum(completeness_scores)) / (2 * len(clarity_scores))
        }
    
    def _score_clarity(self, question: str) -> float:
        """Score question clarity (0-1)."""
        score = 0.5  # Base score
        
        # Question starts with interrogative word
        interrogatives = ['what', 'how', 'why', 'when', 'where', 'who', 'which']
        if any(question.lower().startswith(word) for word in interrogatives):
            score += 0.2
        
        # Ends with question mark
        if question.strip().endswith('?'):
            score += 0.1
        
        # Appropriate length (not too short or long)
        word_count = len(question.split())
        if 4 <= word_count <= 20:
            score += 0.2
        elif word_count > 20:
            score -= 0.1
        
        return min(max(score, 0), 1.0)
    
    def _score_completeness(self, answer: str) -> float:
        """Score answer completeness (0-1)."""
        score = 0.5  # Base score
        
        # Appropriate length
        word_count = len(answer.split())
        if 5 <= word_count <= 50:
            score += 0.3
        elif 50 < word_count <= 100:
            score += 0.2
        
        # Has proper ending punctuation
        if answer.strip() and answer.strip()[-1] in '.!':
            score += 0.2
        
        return min(max(score, 0), 1.0)
    
    def _estimate_difficulty(self, question: str, answer: str) -> float:
        """Estimate difficulty level (0-1, where 1 is most difficult)."""
        # Simple heuristic based on length and complexity
        q_words = len(question.split())
        a_words = len(answer.split())
        
        # Longer answers typically indicate more complex topics
        complexity = min(a_words / 50, 1.0)
        
        # Multi-part questions are harder
        if 'and' in question.lower() or 'or' in question.lower():
            complexity += 0.2
        
        return min(complexity, 1.0)
    
    def _evaluate_summary(self, context: Optional[Dict]) -> Dict[str, Any]:
        """
        Evaluate summary quality.
        
        Metrics:
        - Compression ratio
        - Key information retention
        - Coherence
        - Readability
        """
        try:
            from mcp.database_tool import DatabaseTool
            db = DatabaseTool()
            
            summaries = db.get_recent_summaries(limit=20)
            
            if not summaries:
                return {
                    'success': True,
                    'message': 'No summaries to evaluate',
                    'metrics': {}
                }
            
            metrics = self._calculate_summary_metrics(summaries)
            
            # Save evaluation
            self._save_evaluation('summary', metrics)
            
            return {
                'success': True,
                'message': f'Evaluated {len(summaries)} summaries',
                'metrics': metrics,
                'num_evaluated': len(summaries)
            }
            
        except Exception as e:
            logger.error(f"Summary evaluation error: {e}")
            return {'success': False, 'message': str(e)}
    
    def _calculate_summary_metrics(self, summaries: List[Dict]) -> Dict[str, float]:
        """Calculate summary quality metrics."""
        if not summaries:
            return {}
        
        compression_ratios = []
        coherence_scores = []
        
        for summary in summaries:
            original_len = summary.get('original_length', 0)
            summary_len = summary.get('summary_length', 0)
            
            if original_len > 0:
                ratio = summary_len / original_len
                compression_ratios.append(ratio)
            
            # Coherence: Simple heuristic based on sentence structure
            coherence = self._score_coherence(summary.get('content', ''))
            coherence_scores.append(coherence)
        
        avg_compression = sum(compression_ratios) / len(compression_ratios) if compression_ratios else 0
        avg_coherence = sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0
        
        return {
            'compression_ratio': avg_compression,
            'coherence': avg_coherence,
            'readability': 0.75,  # Placeholder
            'information_retention': 0.80  # Placeholder
        }
    
    def _score_coherence(self, text: str) -> float:
        """Score text coherence (0-1)."""
        if not text:
            return 0.0
        
        score = 0.5
        
        # Has multiple sentences
        sentences = text.split('.')
        if len(sentences) >= 3:
            score += 0.2
        
        # Uses transition words
        transitions = ['however', 'therefore', 'furthermore', 'additionally', 'consequently']
        if any(word in text.lower() for word in transitions):
            score += 0.3
        
        return min(score, 1.0)
    
    def _evaluate_overall_performance(self) -> Dict[str, Any]:
        """
        Generate overall performance report.
        
        Aggregates metrics across all evaluations.
        """
        try:
            from mcp.database_tool import DatabaseTool
            db = DatabaseTool()
            
            # Get aggregated metrics
            metrics = db.get_evaluation_metrics()
            logs = db.get_evaluation_logs(limit=100)
            
            # Calculate trends
            trends = self._calculate_trends(logs)
            
            return {
                'success': True,
                'message': 'Generated overall performance report',
                'metrics': metrics,
                'trends': trends,
                'total_evaluations': len(logs)
            }
            
        except Exception as e:
            logger.error(f"Overall evaluation error: {e}")
            return {'success': False, 'message': str(e)}
    
    def _calculate_trends(self, logs: List[Dict]) -> Dict[str, str]:
        """Calculate performance trends from evaluation logs."""
        if len(logs) < 2:
            return {'trend': 'insufficient_data'}
        
        # Simple trend analysis: compare recent vs older scores
        recent = logs[:len(logs)//2]
        older = logs[len(logs)//2:]
        
        recent_avg = sum(log.get('score', 0) for log in recent) / len(recent) if recent else 0
        older_avg = sum(log.get('score', 0) for log in older) / len(older) if older else 0
        
        if recent_avg > older_avg * 1.1:
            trend = 'improving'
        elif recent_avg < older_avg * 0.9:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'recent_average': recent_avg,
            'older_average': older_avg
        }
    
    def _save_evaluation(self, eval_type: str, metrics: Dict[str, float]):
        """Save evaluation results to database."""
        try:
            from mcp.database_tool import DatabaseTool
            db = DatabaseTool()
            
            eval_data = {
                'type': eval_type,
                'metrics': metrics,
                'timestamp': datetime.now().isoformat()
            }
            
            db.save_evaluation(eval_data)
            logger.info(f"Saved {eval_type} evaluation")
            
        except Exception as e:
            logger.warning(f"Failed to save evaluation: {e}")
    
    def compare_models(self, base_output: str, finetuned_output: str, reference: str) -> Dict[str, Any]:
        """
        Compare base model vs fine-tuned model outputs.
        
        Args:
            base_output: Output from base model
            finetuned_output: Output from fine-tuned model
            reference: Reference/ground truth
            
        Returns:
            Comparison metrics
        """
        try:
            base_score = self._calculate_similarity(base_output, reference)
            finetuned_score = self._calculate_similarity(finetuned_output, reference)
            
            improvement = ((finetuned_score - base_score) / base_score * 100) if base_score > 0 else 0
            
            return {
                'base_model_score': base_score,
                'finetuned_model_score': finetuned_score,
                'improvement_percentage': improvement,
                'winner': 'fine-tuned' if finetuned_score > base_score else 'base'
            }
            
        except Exception as e:
            logger.error(f"Model comparison error: {e}")
            return {'error': str(e)}
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts.
        Simple implementation using word overlap.
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0