"""Command handler for Discord bot commands."""

from typing import Callable, Dict, Optional, Any
from dataclasses import dataclass
import discord
from discord import Message


@dataclass
class Command:
    """Represents a bot command."""

    name: str
    description: str
    usage: str
    handler: Callable
    category: str = "General"
    aliases: list[str] | None = None


class CommandRegistry:
    """Registry for bot commands."""

    def __init__(self):
        """Initialize the command registry."""
        self._commands: Dict[str, Command] = {}

    def register(
        self,
        name: str,
        description: str,
        usage: str,
        category: str = "General",
        aliases: list[str] | None = None,
    ) -> Callable:
        """Decorator to register a command.

        Args:
            name: Command name (without !)
            description: Command description
            usage: Usage example
            category: Command category
            aliases: Alternative names for the command

        Returns:
            Decorator function
        """

        def decorator(func: Callable) -> Callable:
            command = Command(
                name=name,
                description=description,
                usage=usage,
                handler=func,
                category=category,
                aliases=aliases or [],
            )
            self._commands[name] = command

            # Register aliases
            for alias in aliases or []:
                self._commands[alias] = command

            return func

        return decorator

    def get(self, name: str) -> Optional[Command]:
        """Get a command by name.

        Args:
            name: Command name (without !)

        Returns:
            Command object or None if not found
        """
        return self._commands.get(name)

    def get_all(self) -> Dict[str, Command]:
        """Get all registered commands.

        Returns:
            Dictionary of command name to Command object
        """
        # Return only primary commands (not aliases)
        return {name: cmd for name, cmd in self._commands.items() if cmd.name == name}

    def get_by_category(self) -> Dict[str, list[Command]]:
        """Get commands grouped by category.

        Returns:
            Dictionary of category to list of commands
        """
        categories: Dict[str, list[Command]] = {}
        for cmd in self.get_all().values():
            if cmd.category not in categories:
                categories[cmd.category] = []
            categories[cmd.category].append(cmd)
        return categories


class CommandHandler:
    """Handles Discord bot commands."""

    def __init__(self, logger: Any, prefix: str = "!"):
        """Initialize the command handler.

        Args:
            logger: DiscordLogger instance
            prefix: Command prefix (default: !)
        """
        self.logger = logger
        self.prefix = prefix
        self.registry = CommandRegistry()

        # Register built-in commands
        self._register_builtin_commands()

    def _register_builtin_commands(self):
        """Register built-in commands."""

        @self.registry.register(
            name="help",
            description="Show available commands",
            usage="!help [command]",
            category="Information",
            aliases=["h", "?"],
        )
        async def help_command(message: Message, args: list[str]):
            """Show help for all commands or a specific command."""
            if args:
                # Show help for specific command
                cmd = self.registry.get(args[0])
                if cmd is None:
                    await message.reply(f"❌ Unknown command: `{args[0]}`")
                    return

                embed = discord.Embed(
                    title=f"📖 Help: !{cmd.name}",
                    description=cmd.description,
                    color=0x3498DB,
                )
                embed.add_field(name="Usage", value=f"`{cmd.usage}`", inline=False)
                if cmd.aliases:
                    aliases = ", ".join([f"`!{alias}`" for alias in cmd.aliases])
                    embed.add_field(name="Aliases", value=aliases, inline=False)
                embed.add_field(name="Category", value=cmd.category, inline=True)

                await message.reply(embed=embed)
            else:
                # Show all commands grouped by category
                categories = self.registry.get_by_category()

                embed = discord.Embed(
                    title="📚 Available Commands",
                    description=f"Use `{self.prefix}help <command>` for detailed help",
                    color=0x3498DB,
                )

                for category, commands in sorted(categories.items()):
                    cmd_list = "\n".join(
                        [
                            f"`{self.prefix}{cmd.name}` - {cmd.description}"
                            for cmd in commands
                        ]
                    )
                    embed.add_field(name=category, value=cmd_list, inline=False)

                embed.set_footer(text=f"Command prefix: {self.prefix}")
                await message.reply(embed=embed)

        @self.registry.register(
            name="ping",
            description="Check bot latency",
            usage="!ping",
            category="Information",
        )
        async def ping_command(message: Message, args: list[str]):
            """Check bot latency."""
            latency = self.logger._client.latency * 1000  # Convert to ms
            embed = discord.Embed(
                title="🏓 Pong!",
                description=f"Latency: `{latency:.2f}ms`",
                color=0x2ECC71,
            )
            await message.reply(embed=embed)

        @self.registry.register(
            name="status",
            description="Show bot status and connection info",
            usage="!status",
            category="Information",
            aliases=["info"],
        )
        async def status_command(message: Message, args: list[str]):
            """Show bot status."""
            embed = discord.Embed(
                title="📊 Bot Status",
                color=0x3498DB,
            )

            # Bot info
            bot_user = self.logger._client.user
            embed.add_field(
                name="Bot",
                value=f"{bot_user.mention}\n`{bot_user.name}#{bot_user.discriminator}`",
                inline=True,
            )

            # Latency
            latency = self.logger._client.latency * 1000
            embed.add_field(name="Latency", value=f"`{latency:.2f}ms`", inline=True)

            # Thread info
            if self.logger._log_thread:
                thread_name = self.logger._log_thread.name
                thread_id = self.logger._log_thread.id
                embed.add_field(
                    name="Log Thread",
                    value=f"[{thread_name}](https://discord.com/channels/{message.guild.id}/{thread_id})",
                    inline=False,
                )

            # Voice connection
            if self.logger._voice_client and self.logger._voice_client.is_connected():
                voice_channel = self.logger._voice_client.channel
                embed.add_field(
                    name="Voice Channel",
                    value=f"🔊 Connected to **{voice_channel.name}**",
                    inline=False,
                )
            else:
                embed.add_field(
                    name="Voice Channel",
                    value="❌ Not connected",
                    inline=False,
                )

            # VoiceVox status
            if self.logger._voicevox:
                voicevox_available = await self.logger._voicevox.is_available()
                voicevox_status = (
                    "✅ Available" if voicevox_available else "❌ Unavailable"
                )
                embed.add_field(
                    name="VoiceVox Engine",
                    value=f"{voicevox_status}\n`{self.logger.voicevox_url}`",
                    inline=False,
                )

            await message.reply(embed=embed)

        @self.registry.register(
            name="thread",
            description="Create a new log thread",
            usage="!thread [name]",
            category="Management",
        )
        async def thread_command(message: Message, args: list[str]):
            """Create a new log thread."""
            # Close current thread by setting it to None
            self.logger._log_thread = None

            # Update thread name if provided
            if args:
                new_name = " ".join(args)
                self.logger.log_thread_name = new_name

            # Create new thread
            thread = await self.logger._ensure_thread()

            await message.reply(
                f"✅ Created new thread: **{thread.name}**\n"
                f"Future logs will be sent to this thread."
            )

        @self.registry.register(
            name="say",
            description="Speak a message in voice channel (requires VoiceVox)",
            usage="!say <message>",
            category="Voice",
            aliases=["speak", "tts"],
        )
        async def say_command(message: Message, args: list[str]):
            """Speak a message in voice channel."""
            if not args:
                await message.reply("❌ Usage: `!say <message>`")
                return

            text = " ".join(args)

            # Check voice connection
            if (
                not self.logger._voice_client
                or not self.logger._voice_client.is_connected()
            ):
                await message.reply(
                    "❌ Not connected to voice channel.\n"
                    "Use `!join <voice_channel_id>` first."
                )
                return

            # Use notify_voice to speak
            try:
                result = await self.logger.notify_voice(
                    message=text,
                    priority="normal",
                    speaker_id=1,  # Default speaker
                    voice_channel_id=self.logger._voice_client.channel.id,
                )

                if result["status"] == "played":
                    await message.add_reaction("✅")
                else:
                    await message.reply(f"⚠️ {result.get('note', 'Unknown error')}")

            except Exception as e:
                await message.reply(f"❌ Error: {str(e)}")

        @self.registry.register(
            name="speakers",
            description="List available VoiceVox speakers",
            usage="!speakers",
            category="Voice",
        )
        async def speakers_command(message: Message, args: list[str]):
            """List available VoiceVox speakers."""
            if not self.logger._voicevox:
                await message.reply("❌ VoiceVox client not initialized")
                return

            if not await self.logger._voicevox.is_available():
                await message.reply(
                    f"❌ VoiceVox Engine is not available at `{self.logger.voicevox_url}`"
                )
                return

            try:
                speakers = await self.logger._voicevox.get_speakers()

                embed = discord.Embed(
                    title="🎤 Available VoiceVox Speakers",
                    description=f"Total: {len(speakers)} speakers",
                    color=0x9B59B6,
                )

                # Group by speaker (each speaker may have multiple styles)
                speaker_lines = []
                for speaker in speakers[:15]:  # Show first 15 to avoid message too long
                    styles = ", ".join([style["name"] for style in speaker["styles"]])
                    speaker_lines.append(
                        f"**{speaker['name']}** - {styles}\n"
                        f"ID: `{speaker['styles'][0]['id']}`"
                    )

                embed.description = "\n\n".join(speaker_lines)

                if len(speakers) > 15:
                    embed.set_footer(
                        text=f"Showing 15 of {len(speakers)} speakers. Visit VoiceVox Engine for full list."
                    )

                await message.reply(embed=embed)

            except Exception as e:
                await message.reply(f"❌ Error fetching speakers: {str(e)}")

        @self.registry.register(
            name="join",
            description="Connect to a voice channel",
            usage="!join [voice_channel_id]",
            category="Voice",
        )
        async def join_command(message: Message, args: list[str]):
            """Connect to a voice channel."""
            await self.logger._handle_join_command(message)

        @self.registry.register(
            name="leave",
            description="Disconnect from voice channel",
            usage="!leave",
            category="Voice",
            aliases=["disconnect"],
        )
        async def leave_command(message: Message, args: list[str]):
            """Disconnect from voice channel."""
            await self.logger._handle_leave_command(message)

    async def handle_message(self, message: Message) -> bool:
        """Handle a Discord message as a potential command.

        Args:
            message: Discord message to handle

        Returns:
            True if message was a command and was handled, False otherwise
        """
        # Ignore messages from the bot itself
        if message.author == self.logger._client.user:
            return False

        # Check if message starts with prefix
        if not message.content.startswith(self.prefix):
            return False

        # Parse command and arguments
        parts = message.content[len(self.prefix) :].split()
        if not parts:
            return False

        command_name = parts[0].lower()
        args = parts[1:]

        # Get command from registry
        command = self.registry.get(command_name)
        if command is None:
            return False

        # Execute command
        try:
            await command.handler(message, args)
            return True
        except Exception as e:
            await message.reply(f"❌ Error executing command: {str(e)}")
            print(f"Error executing command {command_name}: {e}")
            return True
