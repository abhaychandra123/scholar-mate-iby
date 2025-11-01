"""
Fine-tune model using LoRA for lecture summarization and flashcard generation.
"""

import json
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model
import torch

def find_target_modules(model):
    """
    Automatically find the correct target modules for LoRA based on model architecture.
    Returns a list of module names that PEFT can use for pattern matching.
    """
    model_type = model.config.model_type if hasattr(model.config, 'model_type') else None
    
    # Phi-3 specific: uses qkv_proj (combined) and o_proj for attention
    if model_type == "phi3":
        target_modules = []
        for name, module in model.named_modules():
            # Get the base module name (last part after the dot)
            module_name = name.split('.')[-1]
            # Phi-3 uses: qkv_proj, o_proj, gate_proj, up_proj, down_proj
            if module_name in ["qkv_proj", "q_proj", "k_proj", "v_proj", "o_proj", 
                              "gate_proj", "up_proj", "down_proj"]:
                if module_name not in target_modules:
                    target_modules.append(module_name)
        
        if target_modules:
            return target_modules
    
    # Mistral/Llama style
    if model_type in ["mistral", "llama"]:
        return ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
    
    # Generic: scan model for common attention/MLP projection patterns
    target_modules = []
    seen_modules = set()
    
    for name, module in model.named_modules():
        module_name = name.split('.')[-1]
        # Common patterns for attention and MLP layers
        if module_name in ["qkv_proj", "q_proj", "k_proj", "v_proj", "o_proj",
                          "gate_proj", "up_proj", "down_proj", "gate_up_proj"]:
            if module_name not in seen_modules:
                target_modules.append(module_name)
                seen_modules.add(module_name)
    
    # If we found modules, return them
    if target_modules:
        return target_modules
    
    # Last resort: find all Linear layers except lm_head and embeddings
    target_modules = []
    for name, module in model.named_modules():
        if "Linear" in str(type(module)):
            if "lm_head" not in name and "embed" not in name.lower():
                module_name = name.split('.')[-1]
                if module_name not in seen_modules:
                    target_modules.append(module_name)
                    seen_modules.add(module_name)
    
    return target_modules

def load_dataset(file_path):
    """Load and format training data."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    formatted_data = []
    for item in data:
        # Format as instruction-following task
        input_text = item['input']
        output = item['output']
        
        # Create prompt
        prompt = f"""Summarize the following lecture and generate flashcards.

Lecture: {input_text}

Response:"""
        
        # Create completion
        completion = f"""Summary: {output['summary']}

Flashcards:
{json.dumps(output['flashcards'], indent=2)}"""
        
        formatted_data.append({
            'text': prompt + completion
        })
    
    return Dataset.from_list(formatted_data)

def tokenize_function(examples, tokenizer):
    """Tokenize dataset and create labels for causal LM training."""
    tokenized = tokenizer(
        examples['text'],
        truncation=True,
        max_length=512,
        padding='max_length'
    )
    # For causal LM, labels are the same as input_ids (they'll be shifted internally)
    tokenized['labels'] = tokenized['input_ids'].copy()
    return tokenized

def main():
    print("Loading base model...")
    
    # Choose base model
    model_name = "microsoft/phi-3-mini-4k-instruct"
    # Alternative: "mistralai/Mistral-7B-v0.1"
    
    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    
    # Load model with cache disabled for training compatibility
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        dtype=torch.float16,  # Changed from torch_dtype (deprecated)
        device_map="auto",
        trust_remote_code=True,
        attn_implementation="eager",  # Avoid flash attention issues
    )
    
    # Disable cache during training to avoid DynamicCache compatibility issues
    if hasattr(model.config, 'use_cache'):
        model.config.use_cache = False
    
    # Auto-detect target modules for LoRA
    target_modules = find_target_modules(model)
    print(f"Detected target modules for LoRA: {target_modules}")
    
    if not target_modules:
        raise ValueError("Could not detect target modules for LoRA. Please specify manually.")
    
    # LoRA configuration
    lora_config = LoraConfig(
        r=16,  # LoRA rank
        lora_alpha=32,
        target_modules=target_modules,  # Auto-detected based on model architecture
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    # Apply LoRA
    model = get_peft_model(model, lora_config)
    
    # Ensure cache is disabled on the PEFT model as well
    if hasattr(model.config, 'use_cache'):
        model.config.use_cache = False
    if hasattr(model.base_model.config, 'use_cache'):
        model.base_model.config.use_cache = False
    
    model.print_trainable_parameters()
    
    print("Loading dataset...")
    dataset = load_dataset('data/fine_tuning_dataset.json')
    
    # Tokenize
    tokenized_dataset = dataset.map(
        lambda x: tokenize_function(x, tokenizer),
        batched=True,
        remove_columns=['text']
    )
    
    # Split dataset
    split = tokenized_dataset.train_test_split(test_size=0.1)
    train_dataset = split['train']
    eval_dataset = split['test']
    
    print("Starting training...")
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir="models/lora_model",
        num_train_epochs=3,
        per_device_train_batch_size=2,
        per_device_eval_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        fp16=True,
        save_steps=100,
        logging_steps=10,
        eval_steps=50,
        eval_strategy="steps",  # Changed from evaluation_strategy (newer transformers version)
        save_total_limit=2,
        load_best_model_at_end=True,
    )
    
    # Data collator for language modeling
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,  # We're doing causal LM, not masked LM
    )
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
    )
    
    # Train
    trainer.train()
    
    # Save
    print("Saving model...")
    model.save_pretrained("models/lora_model")
    tokenizer.save_pretrained("models/lora_model")
    
    print("Training complete!")

if __name__ == "__main__":
    main()