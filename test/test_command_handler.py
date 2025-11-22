"""Tests for command handler."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.command_handler import CommandRegistry, CommandHandler
import discord


class TestCommandRegistry:
    """Test command registry."""

    def test_register_command(self):
        """Test registering a command."""
        registry = CommandRegistry()

        @registry.register(
            name="test",
            description="Test command",
            usage="!test",
            category="Test",
        )
        async def test_command(message, args):
            pass

        cmd = registry.get("test")
        assert cmd is not None
        assert cmd.name == "test"
        assert cmd.description == "Test command"
        assert cmd.usage == "!test"
        assert cmd.category == "Test"

    def test_register_command_with_aliases(self):
        """Test registering a command with aliases."""
        registry = CommandRegistry()

        @registry.register(
            name="test",
            description="Test command",
            usage="!test",
            aliases=["t", "tst"],
        )
        async def test_command(message, args):
            pass

        # Should be accessible by name and aliases
        assert registry.get("test") is not None
        assert registry.get("t") is not None
        assert registry.get("tst") is not None

        # All should point to the same command
        assert registry.get("test").name == "test"
        assert registry.get("t").name == "test"
        assert registry.get("tst").name == "test"

    def test_get_all_excludes_aliases(self):
        """Test that get_all returns only primary commands."""
        registry = CommandRegistry()

        @registry.register(
            name="test1",
            description="Test 1",
            usage="!test1",
            aliases=["t1"],
        )
        async def test1_command(message, args):
            pass

        @registry.register(
            name="test2",
            description="Test 2",
            usage="!test2",
        )
        async def test2_command(message, args):
            pass

        all_commands = registry.get_all()
        assert len(all_commands) == 2
        assert "test1" in all_commands
        assert "test2" in all_commands
        assert "t1" not in all_commands

    def test_get_by_category(self):
        """Test grouping commands by category."""
        registry = CommandRegistry()

        @registry.register(
            name="cmd1",
            description="Command 1",
            usage="!cmd1",
            category="CategoryA",
        )
        async def cmd1(message, args):
            pass

        @registry.register(
            name="cmd2",
            description="Command 2",
            usage="!cmd2",
            category="CategoryA",
        )
        async def cmd2(message, args):
            pass

        @registry.register(
            name="cmd3",
            description="Command 3",
            usage="!cmd3",
            category="CategoryB",
        )
        async def cmd3(message, args):
            pass

        categories = registry.get_by_category()
        assert len(categories) == 2
        assert len(categories["CategoryA"]) == 2
        assert len(categories["CategoryB"]) == 1


class TestCommandHandler:
    """Test command handler."""

    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger."""
        logger = MagicMock()
        logger._client = MagicMock()
        logger._client.user = MagicMock()
        logger._client.latency = 0.05
        logger._log_thread = None
        logger._voice_client = None
        logger._voicevox = None
        logger.voicevox_url = "http://localhost:50021"
        return logger

    @pytest.fixture
    def handler(self, mock_logger):
        """Create a command handler."""
        return CommandHandler(mock_logger)

    @pytest.mark.asyncio
    async def test_help_command(self, handler, mock_logger):
        """Test help command."""
        message = AsyncMock()
        message.author = MagicMock()
        message.content = "!help"
        message.reply = AsyncMock()

        await handler.handle_message(message)

        # Should reply with help embed
        message.reply.assert_called_once()
        embed_arg = message.reply.call_args[1]["embed"]
        assert isinstance(embed_arg, discord.Embed)
        assert "Available Commands" in embed_arg.title

    @pytest.mark.asyncio
    async def test_help_command_specific(self, handler, mock_logger):
        """Test help command for specific command."""
        message = AsyncMock()
        message.author = MagicMock()
        message.content = "!help ping"
        message.reply = AsyncMock()

        await handler.handle_message(message)

        # Should reply with specific command help
        message.reply.assert_called_once()
        embed_arg = message.reply.call_args[1]["embed"]
        assert isinstance(embed_arg, discord.Embed)
        assert "ping" in embed_arg.title.lower()

    @pytest.mark.asyncio
    async def test_ping_command(self, handler, mock_logger):
        """Test ping command."""
        message = AsyncMock()
        message.author = MagicMock()
        message.content = "!ping"
        message.reply = AsyncMock()

        await handler.handle_message(message)

        # Should reply with latency
        message.reply.assert_called_once()
        embed_arg = message.reply.call_args[1]["embed"]
        assert isinstance(embed_arg, discord.Embed)
        assert "Pong" in embed_arg.title

    @pytest.mark.asyncio
    async def test_status_command(self, handler, mock_logger):
        """Test status command."""
        mock_logger._client.user = MagicMock()
        mock_logger._client.user.mention = "@Bot"
        mock_logger._client.user.name = "TestBot"
        mock_logger._client.user.discriminator = "1234"

        message = AsyncMock()
        message.author = MagicMock()
        message.content = "!status"
        message.guild = MagicMock()
        message.guild.id = 123456789
        message.reply = AsyncMock()

        await handler.handle_message(message)

        # Should reply with status
        message.reply.assert_called_once()
        embed_arg = message.reply.call_args[1]["embed"]
        assert isinstance(embed_arg, discord.Embed)
        assert "Bot Status" in embed_arg.title

    @pytest.mark.asyncio
    async def test_unknown_command(self, handler, mock_logger):
        """Test unknown command."""
        message = AsyncMock()
        message.author = MagicMock()
        message.content = "!unknowncommand"

        result = await handler.handle_message(message)

        # Should return False for unknown command
        assert result is False

    @pytest.mark.asyncio
    async def test_non_command_message(self, handler, mock_logger):
        """Test non-command message."""
        message = AsyncMock()
        message.author = MagicMock()
        message.content = "This is not a command"

        result = await handler.handle_message(message)

        # Should return False for non-command
        assert result is False

    @pytest.mark.asyncio
    async def test_command_with_args(self, handler, mock_logger):
        """Test command with arguments."""
        message = AsyncMock()
        message.author = MagicMock()
        message.content = "!help ping"
        message.reply = AsyncMock()

        await handler.handle_message(message)

        # Should handle args correctly
        message.reply.assert_called_once()

    @pytest.mark.asyncio
    async def test_command_aliases(self, handler, mock_logger):
        """Test command aliases."""
        message = AsyncMock()
        message.author = MagicMock()
        message.content = "!h"  # Alias for help
        message.reply = AsyncMock()

        await handler.handle_message(message)

        # Should work with alias
        message.reply.assert_called_once()

    @pytest.mark.asyncio
    async def test_ignore_bot_messages(self, handler, mock_logger):
        """Test that bot messages are ignored."""
        message = AsyncMock()
        message.author = mock_logger._client.user
        message.content = "!help"

        result = await handler.handle_message(message)

        # Should return False and not process
        assert result is False

    @pytest.mark.asyncio
    async def test_custom_command_registration(self, handler, mock_logger):
        """Test registering a custom command."""
        executed = []

        @handler.registry.register(
            name="custom",
            description="Custom command",
            usage="!custom",
            category="Test",
        )
        async def custom_command(message, args):
            executed.append(True)

        message = AsyncMock()
        message.author = MagicMock()
        message.content = "!custom"

        await handler.handle_message(message)

        # Should execute custom command
        assert len(executed) == 1

    @pytest.mark.asyncio
    async def test_command_error_handling(self, handler, mock_logger):
        """Test error handling in commands."""

        @handler.registry.register(
            name="error",
            description="Error command",
            usage="!error",
        )
        async def error_command(message, args):
            raise ValueError("Test error")

        message = AsyncMock()
        message.author = MagicMock()
        message.content = "!error"
        message.reply = AsyncMock()

        await handler.handle_message(message)

        # Should handle error and reply with error message
        message.reply.assert_called_once()
        call_args = message.reply.call_args[0][0]
        assert "Error" in call_args
