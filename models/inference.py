"""
Model Inference - Handles fine-tuned model inference.
Supports LoRA-tuned models for summarization and flashcard generation.
"""

import logging
from typing import Dict, List, Optional, Any
import json

logger = logging.getLogger(__name__)


class ModelInference:
    """
    Inference engine for fine-tuned models.
    Handles both summarization and flashcard generation.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize model inference.
        
        Args:
            model_path: Path to fine-tuned model (optional)
        """
        self.model = None
        self.tokenizer = None
        self.model_loaded = False
        self.model_path = model_path or "models/lora_model"
        
        # Try to load model
        try:
            self._load_model()
        except Exception as e:
            logger.warning(f"Model not available, using fallback: {e}")
    
    def _load_model(self):
        """Load fine-tuned model and tokenizer."""
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
            from peft import PeftModel
            
            # Check if model exists
            import os
            if not os.path.exists(self.model_path):
                logger.warning(f"Model path not found: {self.model_path}")
                return
            
            # Load base model and LoRA adapter
            base_model_name = "microsoft/phi-3-mini-4k-instruct"  # or mistralai/Mistral-7B-v0.1
            
            logger.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)
            
            logger.info("Loading base model...")
            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True
            )
            
            logger.info("Loading LoRA adapter...")
            self.model = PeftModel.from_pretrained(base_model, self.model_path)
            self.model.eval()
            
            self.model_loaded = True
            logger.info("Model loaded successfully")
            
        except ImportError as e:
            logger.warning(f"Required libraries not installed: {e}")
            logger.info("Install with: pip install torch transformers peft")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
    
    def generate_summary(self, prompt: str, max_length: int = 512) -> str:
        """
        Generate summary from lecture content.
        
        Args:
            prompt: Formatted prompt with lecture content
            max_length: Maximum length of generated summary
            
        Returns:
            Generated summary text
        """
        if not self.model_loaded:
            return self._fallback_summary(prompt)
        
        try:
            import torch
            
            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048
            ).to(self.model.device)
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_length,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode output
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract summary (remove prompt)
            summary = generated_text[len(prompt):].strip()
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return self._fallback_summary(prompt)
    
    def generate_flashcards(self, prompt: str, num_cards: int = 5) -> List[Dict[str, str]]:
        """
        Generate flashcards from lecture content.
        
        Args:
            prompt: Formatted prompt with lecture content
            num_cards: Number of flashcards to generate
            
        Returns:
            List of flashcard dictionaries with question/answer pairs
        """
        if not self.model_loaded:
            return self._fallback_flashcards(prompt, num_cards)
        
        try:
            import torch
            
            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048
            ).to(self.model.device)
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=1024,
                    temperature=0.8,
                    top_p=0.95,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode output
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Parse flashcards from generated text
            flashcards = self._parse_flashcards(generated_text)
            
            return flashcards[:num_cards]
            
        except Exception as e:
            logger.error(f"Error generating flashcards: {e}")
            return self._fallback_flashcards(prompt, num_cards)
    
    def _parse_flashcards(self, text: str) -> List[Dict[str, str]]:
        """Parse flashcards from generated text."""
        import re
        
        flashcards = []
        
        # Try to parse JSON format first
        try:
            # Look for JSON array
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                cards_data = json.loads(json_match.group(0))
                for card in cards_data:
                    if isinstance(card, dict) and 'question' in card and 'answer' in card:
                        flashcards.append(card)
        except:
            pass
        
        # Fallback: Parse Q&A format
        if not flashcards:
            # Pattern: Q: ... A: ...
            qa_pattern = r'Q\d*[:\.]?\s*([^\n]+)\s*A\d*[:\.]?\s*([^\n]+)'
            matches = re.finditer(qa_pattern, text, re.IGNORECASE)
            
            for match in matches:
                flashcards.append({
                    'question': match.group(1).strip(),
                    'answer': match.group(2).strip(),
                    'category': 'generated'
                })
        
        return flashcards
    
    def _fallback_summary(self, prompt: str) -> str:
        """Fallback summary generation without model."""
        # Extract content from prompt
        content = prompt.replace("Summarize the following lecture:", "").strip()
        
        # Simple extraction of first few sentences
        sentences = content.split('.')[:5]
        return '. '.join(s.strip() for s in sentences if s.strip()) + '.'
    
    def _fallback_flashcards(self, prompt: str, num_cards: int) -> List[Dict[str, str]]:
        """Fallback flashcard generation without model."""
        content = prompt.replace("Generate flashcards from:", "").strip()
        
        # Generate simple flashcards
        flashcards = [
            {
                'question': 'What is the main topic discussed?',
                'answer': content[:100] + '...',
                'category': 'fallback'
            }
        ]
        
        return flashcards[:num_cards]