"""Main entry point for the Discord Conversation Logger MCP server."""

import asyncio
import sys

from .mcp_server import ConversationLoggerServer  # type: ignore


async def main() -> None:
    """Main entry point for MCP server (HTTP client mode)."""
    # Initialize and run MCP server that connects to bot daemon via HTTP
    mcp_server = ConversationLoggerServer()
    await mcp_server.run()


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
