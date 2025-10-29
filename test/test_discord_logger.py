"""Tests for Discord logger."""

import asyncio
import pytest
import discord
from unittest.mock import AsyncMock, MagicMock, patch
from src.discord_logger import DiscordLogger


@pytest.mark.usefixtures("isolate_env")
class TestDiscordLogger:
    """Test suite for DiscordLogger class."""

    @pytest.fixture
    def logger(self):
        """Create a DiscordLogger instance."""
        return DiscordLogger(
            token="test-token",
            log_channel_id=123456789,
            log_thread_name="Test Thread",
            voicevox_url="http://localhost:50021",
            voice_channel_id=987654321,
        )

    def test_initialization(self, logger):
        """Test DiscordLogger initialization."""
        assert logger.token == "test-token"
        assert logger.log_channel_id == 123456789
        assert logger.log_thread_name == "Test Thread"
        assert logger.voicevox_url == "http://localhost:50021"
        assert logger.voice_channel_id == 987654321

    def test_initialization_without_voice_channel(self):
        """Test DiscordLogger initialization without voice channel."""
        logger = DiscordLogger(
            token="test-token",
            log_channel_id=123456789,
            log_thread_name="Test Thread",
        )
        assert logger.voice_channel_id is None

    @pytest.mark.asyncio
    async def test_log_human_role(self, logger):
        """Test logging a human message."""
        # Mock Discord client and thread
        logger._client = MagicMock()
        logger._client.is_ready.return_value = True

        mock_thread = MagicMock()
        mock_thread.send = AsyncMock()
        logger._log_thread = mock_thread

        # Patch _ensure_thread to return the mock thread
        with patch.object(logger, "_ensure_thread", new_callable=AsyncMock, return_value=mock_thread):
            await logger.log("human", "Test message", "test-context")

            # Verify send was called
            mock_thread.send.assert_awaited_once()
            call_args = mock_thread.send.call_args
            embed = call_args.kwargs.get("embed") or call_args.args[0]

            # Verify embed properties
            assert isinstance(embed, discord.Embed)
            assert "Test message" in embed.description
            assert embed.color.value == 0x3498DB  # Blue for human

    @pytest.mark.asyncio
    async def test_log_assistant_role(self, logger):
        """Test logging an assistant message."""
        logger._client = MagicMock()
        logger._client.is_ready.return_value = True

        mock_thread = MagicMock()
        mock_thread.send = AsyncMock()

        with patch.object(logger, "_ensure_thread", new_callable=AsyncMock, return_value=mock_thread):
            await logger.log("assistant", "Test response", None)

            mock_thread.send.assert_awaited_once()
            call_args = mock_thread.send.call_args
            embed = call_args.kwargs.get("embed") or call_args.args[0]

            assert embed.color.value == 0x2ECC71  # Green for assistant

    @pytest.mark.asyncio
    async def test_log_system_role(self, logger):
        """Test logging a system message."""
        logger._client = MagicMock()
        logger._client.is_ready.return_value = True

        mock_thread = MagicMock()
        mock_thread.send = AsyncMock()

        with patch.object(logger, "_ensure_thread", new_callable=AsyncMock, return_value=mock_thread):
            await logger.log("system", "System message", None)

            mock_thread.send.assert_awaited_once()
            call_args = mock_thread.send.call_args
            embed = call_args.kwargs.get("embed") or call_args.args[0]

            assert embed.color.value == 0x95A5A6  # Gray for system

    @pytest.mark.asyncio
    async def test_log_client_not_ready(self, logger):
        """Test that logging fails when client is not ready."""
        logger._client = None

        with pytest.raises(RuntimeError, match="The connection with Discord is not ready"):
            await logger.log("human", "Test", None)

    @pytest.mark.asyncio
    async def test_wait_for_reaction_timeout(self, logger):
        """Test wait_for_reaction with timeout."""
        logger._client = MagicMock()
        logger._client.is_ready.return_value = True
        logger._client.user = MagicMock()

        mock_thread = MagicMock()
        mock_message = MagicMock()
        mock_message.id = 123
        mock_message.add_reaction = AsyncMock()
        mock_message.edit = AsyncMock()
        mock_thread.send = AsyncMock(return_value=mock_message)

        # Simulate timeout
        async def wait_for_side_effect(*args, **kwargs):
            import asyncio
            raise asyncio.TimeoutError()

        logger._client.wait_for = AsyncMock(side_effect=wait_for_side_effect)

        with patch.object(logger, "_ensure_thread", new_callable=AsyncMock, return_value=mock_thread):
            with pytest.raises(asyncio.TimeoutError):
                await logger.wait_for_reaction(
                    message="Test?",
                    options=["✅ Yes", "❌ No"],
                    timeout=1
                )

    @pytest.mark.asyncio
    async def test_notify_voice_not_connected(self, logger):
        """Test notify_voice when not connected to voice channel."""
        logger._client = MagicMock()
        logger._client.is_ready.return_value = True
        logger._voice_client = None  # Not connected

        mock_thread = MagicMock()
        mock_thread.send = AsyncMock()

        with patch.object(logger, "_ensure_thread", new_callable=AsyncMock, return_value=mock_thread):
            result = await logger.notify_voice(
                voice_channel_id=123,
                message="Test",
            )

            assert result["status"] == "not_connected"
            mock_thread.send.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_auto_connect_voice_success(self, logger):
        """Test automatic voice channel connection."""
        logger._client = MagicMock()

        mock_voice_channel = MagicMock(spec=discord.VoiceChannel)
        mock_voice_channel.name = "Test Voice"
        mock_voice_client = MagicMock()
        mock_voice_channel.connect = AsyncMock(return_value=mock_voice_client)

        logger._client.get_channel = MagicMock(return_value=mock_voice_channel)

        await logger._auto_connect_voice()

        assert logger._voice_client is not None
        assert logger._voice_client == mock_voice_client
        mock_voice_channel.connect.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_auto_connect_voice_channel_not_found(self, logger):
        """Test auto-connect when channel not found."""
        logger._client = MagicMock()
        logger._client.get_channel = MagicMock(return_value=None)

        # Should not raise, just log warning
        await logger._auto_connect_voice()

        assert logger._voice_client is None

    @pytest.mark.asyncio
    async def test_close_disconnects_voice(self, logger):
        """Test that close() disconnects voice client."""
        logger._client = MagicMock()
        logger._client.close = AsyncMock()

        mock_voice_client = MagicMock()
        mock_voice_client.is_connected.return_value = True
        mock_voice_client.disconnect = AsyncMock()
        logger._voice_client = mock_voice_client

        await logger.close()

        mock_voice_client.disconnect.assert_awaited_once()
        logger._client.close.assert_awaited_once()
