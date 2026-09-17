"""Configuration loader - loads from .env file"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from root directory
ROOT_DIR = Path(__file__).parent.parent.parent
ENV_PATH = ROOT_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
elif Path.cwd() != ROOT_DIR:
    # Try loading from current directory
    load_dotenv()

# API Keys
def get_api_key(provider: str = "openai") -> str:
    """Get API key for specified provider"""
    key_map = {
        "openai": "OPENAI_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
    }
    env_var = key_map.get(provider.lower(), f"{provider.upper()}_API_KEY")
    return os.getenv(env_var, "")

# Provider configuration
PROVIDER_CONFIG = {
    "default": os.getenv("DEFAULT_PROVIDER", "openai"),
    "default_model": os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo"),
    "fallback": os.getenv("FALLBACK_PROVIDER", "openrouter"),
}

__all__ = ["get_api_key", "PROVIDER_CONFIG", "load_dotenv"]