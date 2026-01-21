"""Discord Bot Daemon with HTTP API for MCP communication."""

import asyncio
import os
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from .discord_logger import DiscordLogger  # type: ignore
from .settings import get_settings  # type: ignore


# Request models for HTTP API
class LogRequest(BaseModel):
    """Request model for logging messages."""

    role: str
    message: str
    context: Optional[str] = None


class WaitReactionRequest(BaseModel):
    """Request model for waiting for reactions."""

    message: str
    options: List[str]
    timeout: int = 300
    context: Optional[str] = None


class NotifyVoiceRequest(BaseModel):
    """Request model for voice notifications."""

    message: str
    priority: str = "normal"
    speaker_id: int = 1


class BotDaemon:
    """Discord Bot Daemon with HTTP API."""

    def __init__(self):
        """Initialize the bot daemon."""
        self.settings = get_settings()
        self.discord_logger: Optional[DiscordLogger] = None
        self.app = FastAPI(title="MCP Discord Notifier Bot Daemon")
        self._setup_routes()

    def _setup_routes(self):
        """Setup HTTP API routes."""

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            if self.discord_logger and self.discord_logger._client:
                is_ready = self.discord_logger._client.is_ready()
                return {
                    "status": "healthy" if is_ready else "starting",
                    "discord_connected": is_ready,
                }
            return {"status": "starting", "discord_connected": False}

        @self.app.post("/log")
        async def log_message(request: LogRequest):
            """Log a message to Discord."""
            if not self.discord_logger:
                raise HTTPException(
                    status_code=503, detail="Discord logger not initialized"
                )

            try:
                await self.discord_logger.log(
                    request.role, request.message, request.context
                )
                return {"status": "success", "message": "Message logged successfully"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/wait_reaction")
        async def wait_for_reaction(request: WaitReactionRequest):
            """Wait for user reaction on Discord."""
            if not self.discord_logger:
                raise HTTPException(
                    status_code=503, detail="Discord logger not initialized"
                )

            try:
                result = await self.discord_logger.wait_for_reaction(
                    request.message, request.options, request.timeout, request.context
                )
                return {"status": "success", "result": result}
            except asyncio.TimeoutError:
                raise HTTPException(status_code=408, detail="Reaction timeout")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/notify_voice")
        async def notify_voice(request: NotifyVoiceRequest):
            """Send voice notification."""
            if not self.discord_logger:
                raise HTTPException(
                    status_code=503, detail="Discord logger not initialized"
                )

            # Use configured default voice channel; request payload no longer provides it.
            voice_channel_id = self.settings.voice_channel_id
            if voice_channel_id is None:
                raise HTTPException(
                    status_code=400,
                    detail="VOICE_CHANNEL_ID is not configured on the bot daemon",
                )

            try:
                result = await self.discord_logger.notify_voice(
                    message=request.message,
                    priority=request.priority,
                    speaker_id=request.speaker_id,
                    voice_channel_id=voice_channel_id,
                )
                return {"status": "success", "result": result}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    async def start_discord(self):
        """Start Discord client."""
        cwd = os.getcwd()
        thread_name_with_cwd = f"{self.settings.log_thread_name} [{cwd}]"

        self.discord_logger = DiscordLogger(
            token=self.settings.discord_token,
            log_channel_id=self.settings.log_channel_id,
            log_thread_name=thread_name_with_cwd,
            voicevox_url=self.settings.voicevox_url,
            voice_channel_id=self.settings.voice_channel_id,
        )

        await self.discord_logger.start()
        print(f"Discord client ready as {self.discord_logger._client.user}")

    async def run(self, host: str = "127.0.0.1", port: int = 8765):
        """Run the bot daemon."""
        # Start Discord client in background
        asyncio.create_task(self.start_discord())

        # Wait for Discord to be ready
        await asyncio.sleep(3)

        if not self.discord_logger or not self.discord_logger._client.is_ready():
            print("Warning: Discord client not ready yet, but starting HTTP server...")

        # Start HTTP server
        config = uvicorn.Config(
            self.app, host=host, port=port, log_level="info", loop="asyncio"
        )
        server = uvicorn.Server(config)

        print(f"HTTP API server starting on http://{host}:{port}")
        print(f"Health check: http://{host}:{port}/health")

        try:
            await server.serve()
        finally:
            # Cleanup Discord connection
            if self.discord_logger:
                await self.discord_logger.close()


async def main():
    """Main entry point for the daemon."""
    daemon = BotDaemon()
    await daemon.run()


def cli_entry():
    """CLI entry point."""
    import sys

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
