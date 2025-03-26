"""Model configuration and prompt templates for the LLM service."""
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class ModelConfig:
    """Configuration for LLM models."""
    name: str
    max_tokens: int
    temperature: float
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    thinking: Optional[Dict[str, str]] = None
class PromptTemplates:
    """Collection of prompt templates for different use cases."""
    
    @staticmethod
    def generate_task_prompt(task: str, variables: Optional[list] = None, thinking_mode: bool = False) -> str:
        """Generate a prompt template for task description."""
        prompt = f"Task: {task}\n"
        if variables:
            prompt += f"Variables: {', '.join(variables)}\n"
        if thinking_mode:
            prompt += "Please think step by step and explain your reasoning.\n"
        return prompt

# Available models configuration
ANTROPIC_MODELS = {
    "claude-3-7-sonnet": ModelConfig(
        name="claude-3-7-sonnet-20250219",
        max_tokens=15000,
        temperature=0.7
    ),
    "claude-3-7-sonnet-thinking": ModelConfig(
        name="claude-3-7-sonnet-20250219",
        max_tokens=25000,
        temperature=0.7,
        thinking={
            "type": "enabled",
            "budget_tokens": 16000
        }
    )
}

# Default model configuration
DEFAULT_MODEL = "claude-3-7-sonnet"

def get_model_config(model_name: Optional[str] = None) -> ModelConfig:
    """Get model configuration by name."""
    if model_name is None:
        model_name = DEFAULT_MODEL
    
    if model_name not in ANTROPIC_MODELS:
        raise ValueError(f"Model {model_name} not found. Available models: {list(ANTROPIC_MODELS.keys())}")
    
    return ANTROPIC_MODELS[model_name]

def update_model_config(model_name: str, **kwargs) -> None:
    """Update model configuration parameters."""
    if model_name not in ANTROPIC_MODELS:
        raise ValueError(f"Model {model_name} not found. Available models: {list(ANTROPIC_MODELS.keys())}")
    
    model_config = ANTROPIC_MODELS[model_name]
    for key, value in kwargs.items():
        if hasattr(model_config, key):
            setattr(model_config, key, value)
        else:
            raise ValueError(f"Invalid configuration parameter: {key}")
