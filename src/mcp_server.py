"""MCP server implementation for conversation logging."""

from typing import Optional, List
import httpx

from mcp.server import Server
from mcp.types import Tool, TextContent
from pydantic import BaseModel, Field


class LogConversationRequest(BaseModel):
    """Request model for log_conversation tool."""

    role: str = Field(
        description="The role of the message sender: 'human', 'assistant', or 'system'"
    )
    message: str = Field(description="The message content to log")
    context: Optional[str] = Field(
        default=None, description="Optional context or metadata about the message"
    )


class WaitForReactionRequest(BaseModel):
    """Request model for wait_for_reaction tool."""

    message: str = Field(
        description="The message to display while waiting for user reaction"
    )
    options: List[str] = Field(
        description="List of reaction options (e.g., ['✅ Approve', '❌ Reject'])"
    )
    timeout: int = Field(default=300, description="Timeout in seconds (default: 300)")
    context: Optional[str] = Field(
        default=None, description="Optional context or metadata"
    )


class NotifyVoiceRequest(BaseModel):
    """Request model for notify_voice tool."""

    voice_channel_id: int = Field(
        description="ID of the voice channel to send notification to"
    )
    message: str = Field(description="Message to announce in the voice channel")
    priority: str = Field(
        default="normal",
        description="Priority level: 'normal' or 'high' (default: 'normal')",
    )
    speaker_id: int = Field(
        default=1, description="VoiceVox speaker ID (default: 1 = 四国めたん ノーマル)"
    )


class ConversationLoggerServer:
    """MCP server for logging conversations to Discord via HTTP."""

    def __init__(self, bot_daemon_url: str = "http://127.0.0.1:8765"):
        """Initialize the MCP server.

        Args:
            bot_daemon_url: URL of the Discord Bot Daemon HTTP API
        """
        self.bot_daemon_url = bot_daemon_url
        self.server = Server("mcp-discord-notifier")
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up MCP server handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="log_conversation",
                    description=(
                        "Log conversation messages to Discord for review and history tracking. "
                        "Use this to record important interactions, decisions, or context that "
                        "should be preserved"
                    ),
                    inputSchema=LogConversationRequest.model_json_schema(),
                ),
                Tool(
                    name="wait_for_reaction",
                    description=(
                        "Send a message to Discord and wait for user reaction/feedback. "
                        "Use this when you need user approval, decision, or input to proceed. "
                        "The tool will block until user reacts or timeout occurs."
                    ),
                    inputSchema=WaitForReactionRequest.model_json_schema(),
                ),
                Tool(
                    name="notify_voice",
                    description=(
                        "Send a voice notification to a Discord voice channel. "
                        "Use this to notify users who are in voice channels. "
                        "Note: Full TTS is not yet implemented - currently logs to text channel."
                    ),
                    inputSchema=NotifyVoiceRequest.model_json_schema(),
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Handle tool calls."""
            async with httpx.AsyncClient(timeout=30.0) as client:
                if name == "log_conversation":
                    # Parse and validate arguments
                    request = LogConversationRequest(**arguments)

                    # Send HTTP request to bot daemon
                    try:
                        response = await client.post(
                            f"{self.bot_daemon_url}/log",
                            json={
                                "role": request.role,
                                "message": request.message,
                                "context": request.context,
                            },
                        )
                        response.raise_for_status()
                        return [
                            TextContent(
                                type="text",
                                text="Message logged successfully",
                            )
                        ]
                    except httpx.HTTPError as e:
                        raise RuntimeError(f"Failed to log message: {e}") from e

                elif name == "wait_for_reaction":
                    # Parse and validate arguments
                    request = WaitForReactionRequest(**arguments)

                    # Send HTTP request to bot daemon
                    try:
                        response = await client.post(
                            f"{self.bot_daemon_url}/wait_reaction",
                            json={
                                "message": request.message,
                                "options": request.options,
                                "timeout": request.timeout,
                                "context": request.context,
                            },
                            timeout=request.timeout + 5.0,
                        )
                        response.raise_for_status()
                        result = response.json()["result"]
                        return [
                            TextContent(
                                type="text",
                                text=f"User selected: {result['option']} (by {result['user']})",
                            )
                        ]
                    except httpx.HTTPError as e:
                        raise RuntimeError(f"Failed to wait for reaction: {e}") from e

                elif name == "notify_voice":
                    # Parse and validate arguments
                    request = NotifyVoiceRequest(**arguments)

                    # Send HTTP request to bot daemon
                    try:
                        response = await client.post(
                            f"{self.bot_daemon_url}/notify_voice",
                            json={
                                "voice_channel_id": request.voice_channel_id,
                                "message": request.message,
                                "priority": request.priority,
                                "speaker_id": request.speaker_id,
                            },
                        )
                        response.raise_for_status()
                        result = response.json()["result"]

                        # Build response message
                        if result["status"] == "played":
                            response_text = f"Voice notification played in {result['voice_channel']} (Speaker: {result['speaker_id']})"
                        else:
                            response_text = f"Voice notification sent to {result['voice_channel']} ({result['status']})"
                            if "note" in result:
                                response_text += f". {result['note']}"

                        return [
                            TextContent(
                                type="text",
                                text=response_text,
                            )
                        ]
                    except httpx.HTTPError as e:
                        raise RuntimeError(f"Failed to send voice notification: {e}") from e

                else:
                    raise ValueError(f"Unknown tool: {name}")

    async def run(self) -> None:
        """Run the MCP server."""
        from mcp.server.stdio import stdio_server

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )
