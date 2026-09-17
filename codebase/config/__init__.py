"""Configuration package"""
from .system_prompt import SYSTEM_PROMPT, PROMPT_VARIANTS
from .env import get_api_key, PROVIDER_CONFIG

__all__ = ["SYSTEM_PROMPT", "PROMPT_VARIANTS", "get_api_key", "PROVIDER_CONFIG"]