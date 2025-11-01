
"""
Evaluation Utilities - Metrics calculation for content quality assessment.
Implements ROUGE, BLEU, and custom educational metrics.
"""

import logging
from typing import Dict, List, Tuple
import re

logger = logging.getLogger(__name__)


class EvaluationMetrics:
    """
    Calculate various quality metrics for generated content.
    """
    
    @staticmethod
    def calculate_rouge(generated: str, reference: str) -> Dict[str, float]:
        """
        Calculate ROUGE scores (simple implementation).
        
        Args:
            generated: Generated text
            reference: Reference text
            
        Returns:
            Dictionary with ROUGE-1, ROUGE-2, ROUGE-L scores
        """
        try:
            # Tokenize
            gen_tokens = generated.lower().split()
            ref_tokens = reference.lower().split()
            
            # ROUGE-1 (unigram overlap)
            rouge_1 = EvaluationMetrics._calculate_rouge_n(gen_tokens, ref_tokens, 1)
            
            # ROUGE-2 (bigram overlap)
            rouge_2 = EvaluationMetrics._calculate_rouge_n(gen_tokens, ref_tokens, 2)
            
            # ROUGE-L (longest common subsequence)
            rouge_l = EvaluationMetrics._calculate_rouge_l(gen_tokens, ref_tokens)
            
            return {
                'rouge-1': rouge_1,
                'rouge-2': rouge_2,
                'rouge-l': rouge_l
            }
            
        except Exception as e:
            logger.error(f"Error calculating ROUGE: {e}")
            return {'rouge-1': 0.0, 'rouge-2': 0.0, 'rouge-l': 0.0}
    
    @staticmethod
    def _calculate_rouge_n(generated_tokens: List[str], reference_tokens: List[str], n: int) -> float:
        """Calculate ROUGE-N score."""
        if len(generated_tokens) < n or len(reference_tokens) < n:
            return 0.0
        
        # Generate n-grams
        gen_ngrams = EvaluationMetrics._get_ngrams(generated_tokens, n)
        ref_ngrams = EvaluationMetrics._get_ngrams(reference_tokens, n)
        
        if not ref_ngrams:
            return 0.0
        
        # Calculate overlap
        overlap = len(gen_ngrams.intersection(ref_ngrams))
        
        # Recall-based ROUGE
        return overlap / len(ref_ngrams)
    
    @staticmethod
    def _get_ngrams(tokens: List[str], n: int) -> set:
        """Generate n-grams from token list."""
        ngrams = set()
        for i in range(len(tokens) - n + 1):
            ngram = tuple(tokens[i:i+n])
            ngrams.add(ngram)
        return ngrams
    
    @staticmethod
    def _calculate_rouge_l(generated_tokens: List[str], reference_tokens: List[str]) -> float:
        """Calculate ROUGE-L score using longest common subsequence."""
        lcs_length = EvaluationMetrics._lcs_
        return lcs_length / max(len(generated_tokens), len(reference_tokens))
    
    @staticmethod
    def _calculate_rouge_l(generated_tokens: List[str], reference_tokens: List[str]) -> float:
        """Calculate ROUGE-L score using longest common subsequence."""
        lcs_length = EvaluationMetrics._lcs_length(generated_tokens, reference_tokens)
        
        if not reference_tokens:
            return 0.0
        
        # F-measure based on LCS
        recall = lcs_length / len(reference_tokens) if reference_tokens else 0
        precision = lcs_length / len(generated_tokens) if generated_tokens else 0
        
        if precision + recall == 0:
            return 0.0
        
        f_score = (2 * precision * recall) / (precision + recall)
        return f_score
    
    @staticmethod
    def _lcs_length(seq1: List[str], seq2: List[str]) -> int:
        """Calculate longest common subsequence length."""
        m, n = len(seq1), len(seq2)
        
        # Create DP table
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # Fill table
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        return dp[m][n]
    
    @staticmethod
    def calculate_bleu(generated: str, reference: str) -> float:
        """
        Calculate BLEU score (simplified implementation).
        
        Args:
            generated: Generated text
            reference: Reference text
            
        Returns:
            BLEU score (0-1)
        """
        try:
            gen_tokens = generated.lower().split()
            ref_tokens = reference.lower().split()
            
            if not gen_tokens or not ref_tokens:
                return 0.0
            
            # Calculate precision for n-grams (1-4)
            precisions = []
            for n in range(1, 5):
                if len(gen_tokens) < n:
                    break
                
                gen_ngrams = EvaluationMetrics._get_ngrams(gen_tokens, n)
                ref_ngrams = EvaluationMetrics._get_ngrams(ref_tokens, n)
                
                if not gen_ngrams:
                    continue
                
                overlap = len(gen_ngrams.intersection(ref_ngrams))
                precision = overlap / len(gen_ngrams)
                precisions.append(precision)
            
            if not precisions:
                return 0.0
            
            # Geometric mean of precisions
            import math
            bleu = math.exp(sum(math.log(p + 1e-10) for p in precisions) / len(precisions))
            
            # Brevity penalty
            bp = 1.0
            if len(gen_tokens) < len(ref_tokens):
                bp = math.exp(1 - len(ref_tokens) / len(gen_tokens))
            
            return bleu * bp
            
        except Exception as e:
            logger.error(f"Error calculating BLEU: {e}")
            return 0.0
    
    @staticmethod
    def calculate_educational_quality(flashcards: List[Dict]) -> Dict[str, float]:
        """
        Calculate educational quality metrics for flashcards.
        
        Args:
            flashcards: List of flashcard dictionaries
            
        Returns:
            Dictionary with quality metrics
        """
        if not flashcards:
            return {
                'clarity': 0.0,
                'completeness': 0.0,
                'diversity': 0.0,
                'difficulty_balance': 0.0
            }
        
        clarity_scores = []
        completeness_scores = []
        question_types = set()
        difficulty_scores = []
        
        for card in flashcards:
            question = card.get('question', '')
            answer = card.get('answer', '')
            
            # Clarity: Question is clear and well-formed
            clarity = EvaluationMetrics._score_clarity(question)
            clarity_scores.append(clarity)
            
            # Completeness: Answer is complete
            completeness = EvaluationMetrics._score_completeness(answer)
            completeness_scores.append(completeness)
            
            # Track question types for diversity
            q_type = EvaluationMetrics._classify_question(question)
            question_types.add(q_type)
            
            # Difficulty estimation
            difficulty = EvaluationMetrics._estimate_difficulty(question, answer)
            difficulty_scores.append(difficulty)
        
        # Calculate diversity (more question types = more diverse)
        diversity = len(question_types) / 5.0  # Normalized by max expected types
        
        # Difficulty balance (standard deviation - lower is more balanced)
        import statistics
        difficulty_balance = 1.0 - min(statistics.stdev(difficulty_scores) if len(difficulty_scores) > 1 else 0, 1.0)
        
        return {
            'clarity': sum(clarity_scores) / len(clarity_scores),
            'completeness': sum(completeness_scores) / len(completeness_scores),
            'diversity': min(diversity, 1.0),
            'difficulty_balance': difficulty_balance
        }
    
    @staticmethod
    def _score_clarity(question: str) -> float:
        """Score question clarity (0-1)."""
        score = 0.5
        
        # Has interrogative word at start
        interrogatives = ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'explain', 'describe']
        if any(question.lower().startswith(word) for word in interrogatives):
            score += 0.2
        
        # Ends with question mark
        if question.strip().endswith('?'):
            score += 0.15
        
        # Appropriate length
        word_count = len(question.split())
        if 5 <= word_count <= 20:
            score += 0.15
        
        return min(score, 1.0)
    
    @staticmethod
    def _score_completeness(answer: str) -> float:
        """Score answer completeness (0-1)."""
        score = 0.5
        
        word_count = len(answer.split())
        
        # Appropriate length
        if 5 <= word_count <= 50:
            score += 0.3
        elif word_count > 50:
            score += 0.2
        
        # Has proper punctuation
        if answer.strip() and answer.strip()[-1] in '.!':
            score += 0.2
        
        return min(score, 1.0)
    
    @staticmethod
    def _classify_question(question: str) -> str:
        """Classify question type."""
        q_lower = question.lower()
        
        if q_lower.startswith('what is') or q_lower.startswith('define'):
            return 'definition'
        elif q_lower.startswith('how'):
            return 'process'
        elif q_lower.startswith('why'):
            return 'explanation'
        elif q_lower.startswith('compare') or 'difference' in q_lower:
            return 'comparison'
        else:
            return 'general'
    
    @staticmethod
    def _estimate_difficulty(question: str, answer: str) -> float:
        """Estimate question difficulty (0-1)."""
        # Heuristic based on complexity
        q_words = len(question.split())
        a_words = len(answer.split())
        
        # Longer answers suggest more complex topics
        complexity = min(a_words / 50, 1.0)
        
        # Multi-part questions are harder
        if 'and' in question.lower() or ',' in question:
            complexity += 0.2
        
        return min(complexity, 1.0)
    
    @staticmethod
    def compare_outputs(output1: str, output2: str, reference: str) -> Dict[str, Any]:
        """
        Compare two outputs against a reference.
        
        Args:
            output1: First output (e.g., base model)
            output2: Second output (e.g., fine-tuned model)
            reference: Ground truth reference
            
        Returns:
            Comparison metrics
        """
        # Calculate ROUGE for both
        rouge1 = EvaluationMetrics.calculate_rouge(output1, reference)
        rouge2 = EvaluationMetrics.calculate_rouge(output2, reference)
        
        # Calculate BLEU for both
        bleu1 = EvaluationMetrics.calculate_bleu(output1, reference)
        bleu2 = EvaluationMetrics.calculate_bleu(output2, reference)
        
        # Determine winner
        avg_score1 = (rouge1['rouge-1'] + rouge1['rouge-2'] + bleu1) / 3
        avg_score2 = (rouge2['rouge-1'] + rouge2['rouge-2'] + bleu2) / 3
        
        improvement = ((avg_score2 - avg_score1) / avg_score1 * 100) if avg_score1 > 0 else 0
        
        return {
            'output1_scores': {
                'rouge': rouge1,
                'bleu': bleu1,
                'average': avg_score1
            },
            'output2_scores': {
                'rouge': rouge2,
                'bleu': bleu2,
                'average': avg_score2
            },
            'improvement_percentage': improvement,
            'winner': 'output2' if avg_score2 > avg_score1 else 'output1'
        }