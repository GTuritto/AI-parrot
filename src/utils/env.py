"""Environment variable utilities for Mujica."""
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


# Load environment variables from .env file
def load_env_vars(env_file: Optional[str] = None) -> bool:
    """Load environment variables from .env file.
    
    Args:
        env_file: Path to .env file. If None, will look for .env in project root.
        
    Returns:
        bool: True if .env file was found and loaded, False otherwise
    """
    if env_file is None:
        # Look for .env in the current working directory
        project_root = Path.cwd()
        env_file = project_root / ".env"
    else:
        env_file = Path(env_file)
    
    if not env_file.exists():
        print(f"Warning: .env file not found at {env_file}")
        return False
        
    load_dotenv(env_file, override=True)
    return True


class APIKeys:
    """Class to access API keys from environment variables."""
    
    @property
    def openai(self) -> str:
        """Get OpenAI API key."""
        return os.getenv("OPENAI_API_KEY", "")
    
    @property
    def anthropic(self) -> str:
        """Get Anthropic API key."""
        return os.getenv("ANTHROPIC_API_KEY", "")
    
    @property
    def google(self) -> str:
        """Get Google API key."""
        return os.getenv("GOOGLE_API_KEY", "")
        
    @property
    def elevenlabs(self) -> str:
        """Get ElevenLabs API key."""
        return os.getenv("ELEVENLABS_API_KEY", "")
    
    @property
    def mistral(self) -> str:
        """Get Mistral API key."""
        return os.getenv("MISTRAL_API_KEY", "")
    
    @property
    def openrouter(self) -> str:
        """Get OpenRouter API key."""
        return os.getenv("OPENROUTER_API_KEY", "")
    
    @property
    def elevenlabs(self) -> str:
        """Get ElevenLabs API key."""
        return os.getenv("ELEVENLABS_API_KEY", "")
    
    @property
    def tavily(self) -> str:
        """Get Tavily API key."""
        return os.getenv("TAVILY_API_KEY", "")
    
    @property
    def news_api(self) -> str:
        """Get News API key."""
        return os.getenv("NEWS_API_KEY", "")


def validate_api_keys() -> dict:
    """Validate that required API keys are set.
    
    Returns:
        Dictionary with API key name as key and boolean indicating if it's set as value.
    """
    api_keys = APIKeys()
    return {
        "openai": bool(api_keys.openai),
        "anthropic": bool(api_keys.anthropic),
        "google": bool(api_keys.google),
        "mistral": bool(api_keys.mistral),
        "openrouter": bool(api_keys.openrouter),
        "elevenlabs": bool(api_keys.elevenlabs),
        "tavily": bool(api_keys.tavily),
        "news_api": bool(api_keys.news_api),
    }


# Load environment variables when this module is imported
load_env_vars()
