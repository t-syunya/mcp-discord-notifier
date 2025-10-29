"""pytest configuration and fixtures."""

import pytest


@pytest.fixture
def isolate_env(monkeypatch):
    """Isolate tests from .env file by clearing relevant environment variables.

    This fixture is NOT autouse - it must be explicitly requested by tests that need isolation.
    Unit tests should use this fixture, but integration tests should not.
    """
    # Clear environment variables that might be set by .env
    env_vars = [
        "DISCORD_TOKEN",
        "LOG_CHANNEL_ID",
        "LOG_THREAD_NAME",
        "VOICE_CHANNEL_ID",
        "VOICEVOX_URL",
    ]
    for var in env_vars:
        monkeypatch.delenv(var, raising=False)

    # Modify Settings model_config to disable .env file loading
    from src.settings import Settings
    from pydantic_settings import SettingsConfigDict

    # Create new config without env_file
    new_config = SettingsConfigDict(
        env_file=None,  # Disable .env file loading
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Replace model_config
    monkeypatch.setattr(Settings, "model_config", new_config)

    yield

    # Restore original config (monkeypatch will handle this automatically)
