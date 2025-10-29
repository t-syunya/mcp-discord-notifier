"""Discord logger implementation using discord.py."""

import asyncio
import os
import tempfile
from datetime import datetime
from typing import Optional, List, Dict, Any

import discord
from discord import Intents, Thread, Message, VoiceClient, FFmpegPCMAudio

from .voicevox_client import VoiceVoxClient


class DiscordLogger:
    """Logger that sends messages to a Discord thread."""

    def __init__(
        self,
        token: str,
        log_channel_id: int,
        log_thread_name: str,
        voicevox_url: str = "http://localhost:50021",
        voice_channel_id: Optional[int] = None,
    ):
        """Initialize the Discord logger.

        Args:
            token: Discord bot token
            log_channel_id: Channel ID where the log thread will be created
            log_thread_name: Name for the log thread
            voicevox_url: VoiceVox Engine API URL (default: http://localhost:50021)
            voice_channel_id: Default voice channel ID (optional, can be set via !join command)
        """
        self.token = token
        self.log_channel_id = log_channel_id
        self.log_thread_name = log_thread_name
        self.voicevox_url = voicevox_url
        self.voice_channel_id = voice_channel_id
        self._client: Optional[discord.Client] = None
        self._log_thread: Optional[Thread] = None
        self._ready_event = asyncio.Event()
        self._voicevox: Optional[VoiceVoxClient] = None
        self._voice_client: Optional[VoiceClient] = None  # Persistent voice connection

    async def start(self) -> None:
        """Start the Discord client."""
        intents = Intents.default()
        intents.message_content = True

        self._client = discord.Client(intents=intents)

        @self._client.event
        async def on_ready():
            """Called when the Discord client is ready."""
            print(f"Discord client logged in as {self._client.user}")
            self._ready_event.set()

        @self._client.event
        async def on_message(message: Message):
            """Handle incoming Discord messages for voice commands."""
            # Ignore messages from the bot itself
            if message.author == self._client.user:
                return

            # Only process messages in the log channel
            if message.channel.id != self.log_channel_id:
                return

            # Process voice commands
            if message.content.startswith("!join"):
                await self._handle_join_command(message)
            elif message.content.startswith("!leave"):
                await self._handle_leave_command(message)

        # Initialize VoiceVox client
        self._voicevox = VoiceVoxClient(self.voicevox_url)

        # Check if VoiceVox is available
        voicevox_available = await self._voicevox.is_available()
        if voicevox_available:
            print(f"VoiceVox Engine is available at {self.voicevox_url}")
        else:
            print(f"Warning: VoiceVox Engine is not available at {self.voicevox_url}")
            print("Voice notifications will be logged to text channel only")

        # Start the client in the background
        asyncio.create_task(self._client.start(self.token))

        # Wait for the client to be ready
        await self._ready_event.wait()

        # Auto-connect to voice channel if configured
        if self.voice_channel_id:
            await self._auto_connect_voice()

    async def _ensure_thread(self) -> Thread:
        """Ensure the log thread exists, creating it if necessary.

        Returns:
            The Discord thread object

        Raises:
            RuntimeError: If the Discord client is not ready
        """
        if self._log_thread is not None:
            return self._log_thread

        if self._client is None:
            raise RuntimeError("Discord client is not initialized")

        channel = self._client.get_channel(self.log_channel_id)
        if channel is None:
            raise RuntimeError(f"Channel {self.log_channel_id} not found")

        # Create a new thread in the channel
        self._log_thread = await channel.create_thread(
            name=self.log_thread_name,
            auto_archive_duration=10080,  # 1 week in minutes
            type=discord.ChannelType.public_thread,
        )

        return self._log_thread

    async def log(
        self, role: str, message: str, context: Optional[str] = None
    ) -> None:
        """Log a message to Discord.

        Args:
            role: The role of the message sender ('human', 'assistant', or 'system')
            message: The message content to log
            context: Optional context or metadata about the message

        Raises:
            RuntimeError: If the Discord client is not ready
        """
        if self._client is None or not self._client.is_ready():
            raise RuntimeError("The connection with Discord is not ready")

        thread = await self._ensure_thread()

        # Determine embed color based on role
        color_map = {
            "human": 0x3498DB,  # Blue
            "assistant": 0x2ECC71,  # Green
            "system": 0x95A5A6,  # Gray
        }
        color = color_map.get(role, 0x7F8C8D)  # Default gray

        # Create embed
        embed = discord.Embed(
            title=f"💬 {role.upper()}",
            description=message,
            color=color,
            timestamp=datetime.utcnow(),
        )

        if context:
            embed.set_footer(text=context)

        await thread.send(embed=embed)

    async def wait_for_reaction(
        self,
        message: str,
        options: List[str],
        timeout: int = 300,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send a message and wait for user reaction.

        Args:
            message: The message content to display
            options: List of reaction options (e.g., ["✅ Approve", "❌ Reject"])
            timeout: Timeout in seconds (default: 300)
            context: Optional context or metadata

        Returns:
            Dictionary with selected option and emoji

        Raises:
            RuntimeError: If the Discord client is not ready
            asyncio.TimeoutError: If no reaction is received within timeout
        """
        if self._client is None or not self._client.is_ready():
            raise RuntimeError("The connection with Discord is not ready")

        thread = await self._ensure_thread()

        # Create embed for the reaction prompt
        embed = discord.Embed(
            title="🤔 WAITING FOR INPUT",
            description=message,
            color=0xF39C12,  # Orange
            timestamp=datetime.utcnow(),
        )

        # Add options to embed
        option_text = "\n".join(options)
        embed.add_field(name="Options", value=option_text, inline=False)

        if context:
            embed.set_footer(text=context)

        # Send message
        sent_message = await thread.send(embed=embed)

        # Extract emojis from options (first emoji in each option string)
        emojis = []
        for option in options:
            # Find first emoji-like character
            for char in option:
                if char in ["✅", "❌", "⏸️", "▶️", "⏭️", "🔄", "⏹️", "👍", "👎", "ℹ️"]:
                    emojis.append(char)
                    break

        # Add reactions to the message
        for emoji in emojis:
            await sent_message.add_reaction(emoji)

        # Wait for reaction
        def check(reaction, user):
            return (
                user != self._client.user
                and reaction.message.id == sent_message.id
                and str(reaction.emoji) in emojis
            )

        try:
            reaction, user = await self._client.wait_for(
                "reaction_add", timeout=timeout, check=check
            )

            # Find matching option
            selected_emoji = str(reaction.emoji)
            selected_option = None
            for option in options:
                if selected_emoji in option:
                    selected_option = option
                    break

            return {
                "emoji": selected_emoji,
                "option": selected_option,
                "user": str(user),
                "message_id": sent_message.id,
            }

        except asyncio.TimeoutError:
            # Update embed to show timeout
            timeout_embed = discord.Embed(
                title="⏱️ TIMEOUT",
                description=f"No response received within {timeout} seconds",
                color=0x95A5A6,  # Gray
                timestamp=datetime.utcnow(),
            )
            await sent_message.edit(embed=timeout_embed)
            raise

    async def notify_voice(
        self,
        voice_channel_id: int,
        message: str,
        priority: str = "normal",
        speaker_id: int = 1,
    ) -> Dict[str, Any]:
        """Send a voice notification using VoiceVox TTS.

        Note: This method requires a persistent voice connection established via !join command.
        If not connected, the notification will only be logged to the text channel.

        Args:
            voice_channel_id: ID of the voice channel (for reference only, not used if already connected)
            message: Message to announce via text-to-speech
            priority: Priority level ("normal" or "high")
            speaker_id: VoiceVox speaker ID (default: 1 = 四国めたん ノーマル)

        Returns:
            Dictionary with notification status

        Raises:
            RuntimeError: If the Discord client is not ready
        """
        if self._client is None or not self._client.is_ready():
            raise RuntimeError("The connection with Discord is not ready")

        # Log to text channel
        thread = await self._ensure_thread()

        embed = discord.Embed(
            title="🔊 VOICE NOTIFICATION",
            description=message,
            color=0xE74C3C if priority == "high" else 0x3498DB,
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="Priority", value=priority.upper(), inline=True)

        # Check if connected to voice channel
        if not self._voice_client or not self._voice_client.is_connected():
            embed.add_field(
                name="Status",
                value="⚠️ Not connected to voice channel",
                inline=False
            )
            embed.set_footer(text="Use !join <voice_channel_id> to connect")
            await thread.send(embed=embed)
            return {
                "status": "not_connected",
                "message": message,
                "priority": priority,
                "note": "Not connected to voice channel - message logged to text only. Use !join command to connect.",
            }

        voice_channel_name = self._voice_client.channel.name
        embed.add_field(name="Voice Channel", value=voice_channel_name, inline=True)

        # Check if VoiceVox is available
        if self._voicevox is None or not await self._voicevox.is_available():
            embed.add_field(
                name="Status",
                value="⚠️ VoiceVox not available",
                inline=False
            )
            embed.set_footer(text="VoiceVox Engine is not running")
            await thread.send(embed=embed)
            return {
                "status": "voicevox_unavailable",
                "voice_channel": voice_channel_name,
                "message": message,
                "priority": priority,
                "note": "VoiceVox not available - message logged to text channel only",
            }

        audio_file_path: Optional[str] = None

        try:
            # Generate TTS audio using VoiceVox
            embed.add_field(
                name="Status", value="🎵 Generating audio...", inline=False
            )
            status_msg = await thread.send(embed=embed)

            audio_data = await self._voicevox.text_to_speech(message, speaker_id)

            # Save to temporary file
            with tempfile.NamedTemporaryFile(
                suffix=".wav", delete=False
            ) as temp_file:
                temp_file.write(audio_data)
                audio_file_path = temp_file.name

            # Play audio (already connected)
            embed.set_field_at(
                2, name="Status", value="▶️ Playing audio...", inline=False
            )
            await status_msg.edit(embed=embed)

            # Wait for any currently playing audio to finish
            while self._voice_client.is_playing():
                await asyncio.sleep(0.1)

            self._voice_client.play(FFmpegPCMAudio(audio_file_path))

            # Wait for playback to finish
            while self._voice_client.is_playing():
                await asyncio.sleep(0.1)

            # Update status
            embed.set_field_at(
                2, name="Status", value="✅ Completed", inline=False
            )
            embed.set_footer(text=f"Speaker ID: {speaker_id}")
            await status_msg.edit(embed=embed)

            return {
                "status": "played",
                "voice_channel": voice_channel_name,
                "message": message,
                "priority": priority,
                "speaker_id": speaker_id,
            }

        except Exception as e:
            # Handle errors
            error_embed = discord.Embed(
                title="❌ VOICE NOTIFICATION FAILED",
                description=f"Error: {str(e)}",
                color=0xE74C3C,
                timestamp=datetime.utcnow(),
            )
            error_embed.add_field(
                name="Voice Channel", value=voice_channel_name, inline=True
            )
            error_embed.add_field(name="Message", value=message, inline=False)
            await thread.send(embed=error_embed)

            raise RuntimeError(f"Failed to send voice notification: {e}") from e

        finally:
            # Cleanup temporary file only (keep voice connection)
            if audio_file_path and os.path.exists(audio_file_path):
                try:
                    os.unlink(audio_file_path)
                except Exception:
                    pass  # Ignore cleanup errors

    async def _auto_connect_voice(self) -> None:
        """Automatically connect to voice channel if configured."""
        if not self.voice_channel_id:
            return

        try:
            voice_channel = self._client.get_channel(self.voice_channel_id)
            if voice_channel is None:
                print(f"Warning: Voice channel {self.voice_channel_id} not found. Skipping auto-connect.")
                return

            if not isinstance(voice_channel, discord.VoiceChannel):
                print(f"Warning: Channel {self.voice_channel_id} is not a voice channel. Skipping auto-connect.")
                return

            self._voice_client = await voice_channel.connect()
            print(f"Auto-connected to voice channel: {voice_channel.name} (ID: {self.voice_channel_id})")

        except Exception as e:
            print(f"Warning: Failed to auto-connect to voice channel: {e}")

    async def _handle_join_command(self, message: Message) -> None:
        """Handle !join command to connect to a voice channel.

        Args:
            message: Discord message containing the command
        """
        parts = message.content.split()

        # Determine voice channel ID
        if len(parts) < 2:
            # No ID provided - use default if configured
            if self.voice_channel_id:
                voice_channel_id = self.voice_channel_id
            else:
                await message.reply(
                    "❌ Usage: `!join <voice_channel_id>`\n"
                    "Right-click on a voice channel and select 'Copy ID' to get the channel ID.\n"
                    "Or set VOICE_CHANNEL_ID in .env file for auto-connect."
                )
                return
        else:
            # ID provided in command
            try:
                voice_channel_id = int(parts[1])
            except ValueError:
                await message.reply("❌ Invalid voice channel ID. Please provide a numeric ID.")
                return

        # Check if already connected
        if self._voice_client and self._voice_client.is_connected():
            current_channel = self._voice_client.channel
            await message.reply(
                f"⚠️ Already connected to voice channel: **{current_channel.name}**\n"
                f"Use `!leave` first to disconnect."
            )
            return

        # Get voice channel
        voice_channel = self._client.get_channel(voice_channel_id)
        if voice_channel is None:
            await message.reply(f"❌ Voice channel with ID `{voice_channel_id}` not found.")
            return

        if not isinstance(voice_channel, discord.VoiceChannel):
            await message.reply(f"❌ Channel `{voice_channel.name}` is not a voice channel.")
            return

        # Connect to voice channel
        try:
            self._voice_client = await voice_channel.connect()
            await message.reply(
                f"✅ Connected to voice channel: **{voice_channel.name}**\n"
                f"Voice notifications will now be played in this channel.\n"
                f"Use `!leave` to disconnect."
            )
            print(f"Connected to voice channel: {voice_channel.name} (ID: {voice_channel_id})")

        except Exception as e:
            await message.reply(f"❌ Failed to connect to voice channel: {str(e)}")
            print(f"Error connecting to voice channel: {e}")

    async def _handle_leave_command(self, message: Message) -> None:
        """Handle !leave command to disconnect from voice channel.

        Args:
            message: Discord message containing the command
        """
        if not self._voice_client or not self._voice_client.is_connected():
            await message.reply("⚠️ Not connected to any voice channel.")
            return

        channel_name = self._voice_client.channel.name

        try:
            await self._voice_client.disconnect()
            self._voice_client = None
            await message.reply(f"✅ Disconnected from voice channel: **{channel_name}**")
            print(f"Disconnected from voice channel: {channel_name}")

        except Exception as e:
            await message.reply(f"❌ Failed to disconnect: {str(e)}")
            print(f"Error disconnecting from voice channel: {e}")

    async def close(self) -> None:
        """Close the Discord client."""
        # Disconnect from voice if connected
        if self._voice_client and self._voice_client.is_connected():
            await self._voice_client.disconnect()
            self._voice_client = None

        if self._client is not None:
            await self._client.close()
