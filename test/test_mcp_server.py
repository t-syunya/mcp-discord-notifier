"""Tests for MCP server."""

import pytest
from src.mcp_server import (
    LogConversationRequest,
    WaitForReactionRequest,
    NotifyVoiceRequest,
)


@pytest.mark.usefixtures("isolate_env")
class TestMCPServerModels:
    """Test suite for MCP server Pydantic models."""

    def test_log_conversation_request_valid(self):
        """Test LogConversationRequest with valid data."""
        request = LogConversationRequest(
            role="human", message="Test message", context="test-context"
        )

        assert request.role == "human"
        assert request.message == "Test message"
        assert request.context == "test-context"

    def test_log_conversation_request_without_context(self):
        """Test LogConversationRequest without optional context."""
        request = LogConversationRequest(role="assistant", message="Test response")

        assert request.role == "assistant"
        assert request.message == "Test response"
        assert request.context is None

    def test_wait_for_reaction_request_valid(self):
        """Test WaitForReactionRequest with valid data."""
        request = WaitForReactionRequest(
            message="Confirm?", options=["✅ Yes", "❌ No"], timeout=300
        )

        assert request.message == "Confirm?"
        assert request.options == ["✅ Yes", "❌ No"]
        assert request.timeout == 300

    def test_wait_for_reaction_request_default_timeout(self):
        """Test WaitForReactionRequest uses default timeout."""
        request = WaitForReactionRequest(message="Confirm?", options=["✅ Yes"])

        assert request.timeout == 300  # Default value

    def test_notify_voice_request_valid(self):
        """Test NotifyVoiceRequest with valid data."""
        request = NotifyVoiceRequest(
            voice_channel_id=123456789,
            message="Test notification",
            priority="high",
            speaker_id=3,
        )

        assert request.voice_channel_id == 123456789
        assert request.message == "Test notification"
        assert request.priority == "high"
        assert request.speaker_id == 3

    def test_notify_voice_request_defaults(self):
        """Test NotifyVoiceRequest uses default values."""
        request = NotifyVoiceRequest(voice_channel_id=123456789, message="Test")

        assert request.priority == "normal"  # Default
        assert request.speaker_id == 1  # Default
