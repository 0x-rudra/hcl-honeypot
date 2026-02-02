"""Configuration module for Honeypot API."""

import os


class Config:
    """Application configuration."""

    API_KEY: str = os.getenv("HONEYPOT_API_KEY", "your-secret-key-here")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = "gemini-2.0-flash"

    AGENT_TEMPERATURE: float = 0.7
    AGENT_TOP_P: float = 0.95
    AGENT_TOP_K: int = 40
    AGENT_MAX_OUTPUT_TOKENS: int = 2048
    SCAM_CONFIDENCE_THRESHOLD: float = 0.5

    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    HOST: str = "0.0.0.0"
    PORT: int = int(os.getenv("PORT", 8000))

    @classmethod
    def validate(cls, raise_error: bool = True) -> bool:
        """Validate required configuration."""
        if not cls.GEMINI_API_KEY:
            if raise_error:
                raise ValueError("GEMINI_API_KEY environment variable not set")
            return False
        return True
