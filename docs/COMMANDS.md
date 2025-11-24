# Discord Bot Commands

This document provides detailed information about all available Discord bot commands.

## Command Structure

All commands start with the `!` prefix and are case-insensitive. Commands can be used in the designated log channel.

```
!command [required_argument] <optional_argument>
```

## Information Commands

### !help

Display a list of all available commands or get detailed help for a specific command.

**Aliases**: `!h`, `!?`

**Usage**:
```
!help              # Show all commands grouped by category
!help <command>    # Show detailed help for a specific command
```

**Examples**:
```
!help              # Shows all commands
!help ping         # Shows help for the ping command
!h join            # Using alias to get help for join command
```

---

### !ping

Check the bot's latency (response time) to Discord servers.

**Usage**:
```
!ping
```

**Response**: Displays latency in milliseconds.

---

### !status

Display comprehensive status information about the bot, including:
- Bot user information
- Current latency
- Active log thread
- Voice channel connection status
- VoiceVox Engine availability

**Aliases**: `!info`

**Usage**:
```
!status
!info
```

---

## Management Commands

### !thread

Create a new log thread or rename the current thread. This is useful when starting work on a new feature or project phase.

**Usage**:
```
!thread                    # Create new thread with default name
!thread <custom name>      # Create new thread with custom name
```

**Examples**:
```
!thread                           # Uses default thread name
!thread Feature Implementation    # Creates "Feature Implementation" thread
!thread Bug Fix #123             # Creates "Bug Fix #123" thread
```

**Notes**:
- Creates a new thread in the log channel
- Automatically archives old threads
- Thread names can include spaces and special characters

---

## Voice Commands

### !join

Connect the bot to a voice channel for voice notifications.

**Usage**:
```
!join                        # Connect to default voice channel (if configured)
!join <voice_channel_id>     # Connect to specific voice channel
```

**How to get Voice Channel ID**:
1. Enable Developer Mode in Discord Settings → Advanced → Developer Mode
2. Right-click on the voice channel
3. Click "Copy ID"

**Examples**:
```
!join                        # Uses VOICE_CHANNEL_ID from .env
!join 123456789012345678     # Connects to specific channel
```

**Notes**:
- Bot must have permission to connect to the voice channel
- Only one voice channel connection at a time
- Use `!leave` to disconnect before joining another channel

---

### !leave

Disconnect the bot from the current voice channel.

**Aliases**: `!disconnect`

**Usage**:
```
!leave
!disconnect
```

**Notes**:
- Automatically disconnects if bot is shut down
- Can reconnect using `!join`

---

### !say

Speak a message in the connected voice channel using text-to-speech.

**Aliases**: `!speak`, `!tts`

**Requirements**:
- Bot must be connected to a voice channel (`!join`)
- VoiceVox Engine must be running (default: http://localhost:50021)

**Usage**:
```
!say <message>
!speak <message>
!tts <message>
```

**Examples**:
```
!say Hello world
!say テストが完了しました
!speak The build has completed successfully
!tts 重要な通知があります
```

**Notes**:
- Uses default VoiceVox speaker (ID: 1 - 四国めたん)
- Japanese text is recommended for best quality
- VoiceVoxが起動していない場合はコマンドが失敗します（音声再生とテキスト通知は常にセットで行います）

---

### !speakers

List all available VoiceVox speakers and their IDs.

**Requirements**:
- VoiceVox Engine must be running

**Usage**:
```
!speakers
```

**Response**: Displays a list of available speakers with:
- Speaker name
- Available styles (e.g., Normal, Happy, Angry)
- Speaker ID for each style

**Notes**:
- Shows first 15 speakers to avoid message length limits
- Use speaker IDs with the `notify_voice` MCP tool

---

## Adding Custom Commands

You can add custom commands programmatically:

### Python Example

```python
from mcp_discord_notifier.discord_logger import DiscordLogger

# Initialize logger
logger = DiscordLogger(
    token="YOUR_BOT_TOKEN",
    log_channel_id=123456789,
    log_thread_name="Conversation Log"
)

await logger.start()

# Define custom command handler
async def uptime_command(message, args):
    """Show bot uptime."""
    import time
    uptime = time.time() - start_time
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    await message.reply(f"Uptime: {hours}h {minutes}m")

# Register the command
logger.register_command(
    name="uptime",
    handler=uptime_command,
    description="Show bot uptime",
    usage="!uptime",
    category="Information",
    aliases=["up"]
)
```

### Command Handler Signature

All command handlers must follow this signature:

```python
async def command_handler(message: discord.Message, args: list[str]) -> None:
    """
    Args:
        message: The Discord message that triggered the command
        args: List of arguments (words after the command name)
    """
    # Your command logic here
    await message.reply("Response")
```

### Registration Parameters

- **name** (required): Command name without the `!` prefix
- **handler** (required): Async function to handle the command
- **description** (required): Short description shown in help
- **usage** (required): Usage example (e.g., `!mycommand <arg>`)
- **category** (optional): Command category (default: "Custom")
- **aliases** (optional): List of alternative command names

---

## Command Categories

Commands are organized into the following categories:

- **Information**: Commands for getting information about the bot
- **Management**: Commands for managing threads and settings
- **Voice**: Commands for voice channel integration
- **Custom**: User-defined commands

---

## Error Handling

If a command fails, the bot will respond with an error message:

```
❌ Error executing command: <error details>
```

Common errors:
- **Not connected to voice channel**: Use `!join` first
- **VoiceVox unavailable**: Start VoiceVox Engine
- **Invalid arguments**: Check command usage with `!help <command>`
- **Permission denied**: Check bot permissions in Discord

---

## Tips

1. **Use tab completion**: Many Discord clients support command completion
2. **Check status regularly**: Use `!status` to verify connections
3. **Test voice before notifications**: Use `!say test` to verify VoiceVox
4. **Create project-specific threads**: Use `!thread` when starting new work
5. **Explore commands**: Use `!help` to discover all available commands

---

## Future Commands

Planned commands for future releases:

- `!volume <0-100>`: Adjust voice playback volume
- `!speaker <id>`: Change default VoiceVox speaker
- `!speed <0.5-2.0>`: Adjust speech speed
- `!logs [count]`: Show recent log messages
- `!clear`: Clear current thread messages
- `!archive`: Manually archive current thread

---

For more information, see the main [CLAUDE.md](../CLAUDE.md) documentation.
