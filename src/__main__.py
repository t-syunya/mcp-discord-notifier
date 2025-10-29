"""Main entry point for the Discord Conversation Logger MCP server."""

import asyncio
import os
import sys

from .discord_logger import DiscordLogger
from .mcp_server import ConversationLoggerServer
from .settings import get_settings


async def main() -> None:
    """Main entry point."""
    # Load settings from .env file
    settings = get_settings()

    # Get current working directory
    cwd = os.getcwd()

    # Include working directory in thread name
    thread_name_with_cwd = f"{settings.log_thread_name} [{cwd}]"

    # Initialize Discord logger
    discord_logger = DiscordLogger(
        token=settings.discord_token,
        log_channel_id=settings.log_channel_id,
        log_thread_name=thread_name_with_cwd,
        voicevox_url=settings.voicevox_url,
        voice_channel_id=settings.voice_channel_id,
    )

    # Start Discord client
    await discord_logger.start()

    # Initialize and run MCP server
    mcp_server = ConversationLoggerServer(discord_logger)

    try:
        await mcp_server.run()
    finally:
        # Clean up Discord connection
        await discord_logger.close()


def cli_entry() -> None:
    """CLI entry point for console script."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down...", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    cli_entry()
