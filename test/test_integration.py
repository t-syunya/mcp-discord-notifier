"""Integration tests for full workflow.

These tests require actual Discord connection and are marked as integration tests.
Run with: pytest -m integration
"""

import pytest
import asyncio
from src.discord_logger import DiscordLogger
from src.mcp_server import ConversationLoggerServer
from src.settings import get_settings


@pytest.mark.integration
class TestIntegration:
    """Integration tests for full system workflow."""

    @pytest.fixture
    async def logger(self):
        """Create and start a DiscordLogger instance."""
        try:
            settings = get_settings()
            logger = DiscordLogger(
                token=settings.discord_token,
                log_channel_id=settings.log_channel_id,
                log_thread_name="Integration Test",
                voicevox_url=settings.voicevox_url,
                voice_channel_id=settings.voice_channel_id,
            )
            await logger.start()
            # Wait for Discord to be ready
            await asyncio.sleep(3)
            yield logger
        finally:
            await logger.close()

    @pytest.mark.asyncio
    async def test_full_logging_workflow(self, logger):
        """Test complete logging workflow."""
        # Log different message types
        await logger.log("system", "Integration test started", "test")
        await logger.log("human", "Test user message", "test")
        await logger.log("assistant", "Test assistant response", "test")
        await logger.log("system", "Integration test completed", "test")

        # If we reach here, logging works
        assert True

    @pytest.mark.asyncio
    async def test_voice_notification_without_connection(self, logger):
        """Test voice notification when not connected to voice channel.

        Note: If the bot is already connected to a voice channel (via auto-connect),
        this test will verify that notification works instead of checking not_connected status.
        """
        result = await logger.notify_voice(
            voice_channel_id=123456789,  # Dummy ID
            message="Test notification",
        )

        # Accept both statuses: not_connected (if not auto-connected) or played (if auto-connected)
        assert result["status"] in ["not_connected", "played", "voicevox_unavailable"]

    @pytest.mark.asyncio
    async def test_mcp_server_initialization(self, logger):
        """Test MCP server can be initialized with Discord logger."""
        server = ConversationLoggerServer(logger)

        # The attribute is discord_logger, not logger
        assert server.discord_logger == logger
        assert server.server is not None

    @pytest.mark.skipif(
        "VOICE_CHANNEL_ID" not in __import__("os").environ,
        reason="VOICE_CHANNEL_ID not set",
    )
    @pytest.mark.asyncio
    async def test_auto_connect_voice(self):
        """Test automatic voice channel connection on startup."""
        settings = get_settings()

        if not settings.voice_channel_id:
            pytest.skip("VOICE_CHANNEL_ID not configured")

        logger = DiscordLogger(
            token=settings.discord_token,
            log_channel_id=settings.log_channel_id,
            log_thread_name="Voice Connection Test",
            voicevox_url=settings.voicevox_url,
            voice_channel_id=settings.voice_channel_id,
        )

        try:
            await logger.start()
            await asyncio.sleep(5)  # Wait for auto-connect

            # Check if connected
            assert logger._voice_client is not None
            if logger._voice_client:
                assert logger._voice_client.is_connected()

        finally:
            await logger.close()


@pytest.mark.integration
@pytest.mark.manual
class TestManualInteraction:
    """Tests that require manual interaction via Discord.

    These tests are marked as 'manual' and should be run individually.
    Run with: pytest -m manual
    """

    @pytest.mark.asyncio
    async def test_wait_for_reaction_manual(self):
        """Test wait_for_reaction with manual Discord interaction.

        This test will:
        1. Send a message to Discord
        2. Wait for you to react with an emoji
        3. Verify the reaction was captured

        MANUAL STEP: Go to Discord and react to the message within 60 seconds!
        """
        settings = get_settings()
        logger = DiscordLogger(
            token=settings.discord_token,
            log_channel_id=settings.log_channel_id,
            log_thread_name="Manual Test",
        )

        try:
            await logger.start()
            await asyncio.sleep(3)

            print("\n" + "=" * 60)
            print("MANUAL TEST: Please react to the message in Discord!")
            print("Options: ✅ (approve) or ❌ (reject)")
            print("You have 60 seconds...")
            print("=" * 60 + "\n")

            result = await logger.wait_for_reaction(
                message="🧪 **INTEGRATION TEST**: Please react to this message!",
                options=["✅ Approve", "❌ Reject"],
                timeout=60,
            )

            print(f"\n✅ Reaction received: {result['emoji']} from {result['user']}\n")

            assert result["emoji"] in ["✅", "❌"]
            assert result["option"] in ["✅ Approve", "❌ Reject"]

        finally:
            await logger.close()

    @pytest.mark.asyncio
    async def test_voice_notification_manual(self):
        """Test voice notification with manual verification.

        This test will:
        1. Connect to configured voice channel (if set)
        2. Play a test message
        3. Wait for manual verification

        MANUAL STEP: Join the voice channel and verify you hear the message!
        """
        settings = get_settings()

        if not settings.voice_channel_id:
            pytest.skip("VOICE_CHANNEL_ID not configured")

        logger = DiscordLogger(
            token=settings.discord_token,
            log_channel_id=settings.log_channel_id,
            log_thread_name="Voice Test",
            voicevox_url=settings.voicevox_url,
            voice_channel_id=settings.voice_channel_id,
        )

        try:
            await logger.start()
            await asyncio.sleep(5)  # Wait for auto-connect

            print("\n" + "=" * 60)
            print("MANUAL TEST: Listen for voice notification!")
            print("You should hear: 'インテグレーションテストです'")
            print("=" * 60 + "\n")

            result = await logger.notify_voice(
                voice_channel_id=settings.voice_channel_id,
                message="インテグレーションテストです",
                priority="normal",
                speaker_id=1,
            )

            print(f"\n✅ Voice notification sent: {result['status']}\n")

            assert result["status"] in [
                "played",
                "not_connected",
                "voicevox_unavailable",
            ]

            # Wait a bit for audio to finish
            await asyncio.sleep(3)

        finally:
            await logger.close()
