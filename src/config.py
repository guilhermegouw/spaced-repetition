"""
Configuration management for the spaced repetition app.
"""
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load .env file from project root
_project_root = Path(__file__).parent.parent
_env_file = _project_root / ".env"
load_dotenv(_env_file)


class APIConfig(BaseModel):
    """Configuration for Z.AI API."""

    api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("ZAI_API_KEY")
    )
    base_url: str = Field(default="default")  # "default" or "coding"
    model: str = Field(default="glm-4.7")
    timeout: float = Field(default=60.0)
    enabled: bool = Field(default=True)

    @property
    def is_configured(self) -> bool:
        """Check if API is properly configured."""
        return bool(self.api_key) and self.enabled


class AppConfig(BaseModel):
    """Main application configuration."""

    api: APIConfig = Field(default_factory=APIConfig)
    use_clipboard_fallback: bool = Field(default=True)


def get_config() -> AppConfig:
    """Get application configuration from environment."""
    return AppConfig(
        api=APIConfig(
            api_key=os.getenv("ZAI_API_KEY"),
            base_url=os.getenv("ZAI_BASE_URL", "default"),
            enabled=os.getenv("ZAI_ENABLED", "true").lower() == "true",
        ),
        use_clipboard_fallback=os.getenv(
            "USE_CLIPBOARD_FALLBACK", "true"
        ).lower()
        == "true",
    )
