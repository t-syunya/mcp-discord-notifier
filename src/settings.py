"""Configuration settings using pydantic-settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Discord Configuration
    discord_token: str = Field(
        ...,
        description="Discord bot token",
    )
    log_channel_id: int = Field(
        ...,
        description="Discord channel ID for logging",
    )
    log_thread_name: str = Field(
        default="Conversation Log",
        description="Name of the thread to create for logs",
    )
    voice_channel_id: int | None = Field(
        default=None,
        description="Default voice channel ID for voice notifications (optional)",
    )

    # VoiceVox Configuration
    voicevox_url: str = Field(
        default="http://localhost:50021",
        description="VoiceVox Engine API URL",
    )


def get_settings() -> Settings:
    """Get application settings.

    Returns:
        Settings: Application settings instance
    """
    return Settings()
