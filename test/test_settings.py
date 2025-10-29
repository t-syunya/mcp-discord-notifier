"""Tests for settings module."""

import pytest
from pydantic import ValidationError
from src.settings import Settings


@pytest.mark.usefixtures("isolate_env")
class TestSettings:
    """Test suite for Settings class."""

    def test_settings_from_env(self, monkeypatch):
        """Test loading settings from environment variables."""
        monkeypatch.setenv("DISCORD_TOKEN", "test-token-123")
        monkeypatch.setenv("LOG_CHANNEL_ID", "123456789012345678")
        monkeypatch.setenv("LOG_THREAD_NAME", "Test Thread")
        monkeypatch.setenv("VOICE_CHANNEL_ID", "987654321098765432")
        monkeypatch.setenv("VOICEVOX_URL", "http://test:8080")

        settings = Settings()

        assert settings.discord_token == "test-token-123"
        assert settings.log_channel_id == 123456789012345678
        assert settings.log_thread_name == "Test Thread"
        assert settings.voice_channel_id == 987654321098765432
        assert settings.voicevox_url == "http://test:8080"

    def test_settings_with_defaults(self, monkeypatch):
        """Test settings with default values."""
        monkeypatch.setenv("DISCORD_TOKEN", "test-token")
        monkeypatch.setenv("LOG_CHANNEL_ID", "123456789012345678")

        settings = Settings()

        assert settings.discord_token == "test-token"
        assert settings.log_channel_id == 123456789012345678
        assert settings.log_thread_name == "Conversation Log"  # Default
        assert settings.voice_channel_id is None  # Default
        assert settings.voicevox_url == "http://localhost:50021"  # Default

    def test_settings_missing_required(self, monkeypatch):
        """Test that missing required fields raise ValidationError."""
        # Clear all relevant env vars
        monkeypatch.delenv("DISCORD_TOKEN", raising=False)
        monkeypatch.delenv("LOG_CHANNEL_ID", raising=False)

        with pytest.raises(ValidationError):
            Settings()

    def test_settings_invalid_channel_id(self, monkeypatch):
        """Test that invalid channel ID type raises ValidationError."""
        monkeypatch.setenv("DISCORD_TOKEN", "test-token")
        monkeypatch.setenv("LOG_CHANNEL_ID", "not-a-number")

        with pytest.raises(ValidationError):
            Settings()

    def test_settings_case_insensitive(self, monkeypatch):
        """Test that environment variable names are case-insensitive."""
        monkeypatch.setenv("discord_token", "test-token-lowercase")
        monkeypatch.setenv("log_channel_id", "123456789012345678")

        settings = Settings()

        assert settings.discord_token == "test-token-lowercase"

    def test_settings_voice_channel_optional(self, monkeypatch):
        """Test that voice_channel_id is optional."""
        monkeypatch.setenv("DISCORD_TOKEN", "test-token")
        monkeypatch.setenv("LOG_CHANNEL_ID", "123456789012345678")
        # Don't set VOICE_CHANNEL_ID

        settings = Settings()

        assert settings.voice_channel_id is None
