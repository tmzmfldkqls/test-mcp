"""Application configuration"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Application configuration from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    AGENT_NAME: str = "test-agent"

    # OpenAI settings
    OPENAI_API_KEY: str = "AIzaSyBgqJeWCI8NG7gQ_8jwGFmmQEvPOZUFpeU"
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TEMPERATURE: float = 0.7

    # Logging
    LOG_LEVEL: str = "INFO"


# Global config instance
config = AppConfig()


def get_config() -> AppConfig:
    """Get application configuration"""
    return config
