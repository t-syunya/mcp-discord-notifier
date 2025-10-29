#!/usr/bin/env python3
"""Test script for persistent voice connection workflow."""

import asyncio
import sys
import pytest
from src.discord_logger import DiscordLogger
from src.settings import get_settings


@pytest.mark.manual
async def test_persistent_voice():
    """Test persistent voice connection workflow."""
    # Load settings
    settings = get_settings()

    print("="*50)
    print("Testing Persistent Voice Connection")
    print("="*50)
    print()
    print("Instructions:")
    print("1. Start the MCP server with: ./scripts/start.sh")
    print("2. In Discord, go to your log channel and type:")
    print("   !join 1356518373097214022")
    print("3. The bot will connect to the voice channel")
    print("4. This script will send a voice notification")
    print("5. The bot will play audio WITHOUT disconnecting")
    print("6. Use !leave in Discord to disconnect when done")
    print()
    print("="*50)
    print()

    logger = DiscordLogger(
        token=settings.discord_token,
        log_channel_id=settings.log_channel_id,
        log_thread_name="Voice Test (Persistent)",
        voicevox_url=settings.voicevox_url,
    )

    print("Starting Discord client...")
    await logger.start()

    # Wait for Discord to be ready
    await asyncio.sleep(3)

    try:
        print("\nTest 1: Sending voice notification WITHOUT pre-connection")
        print("Expected: Text notification only, warning about !join command")
        result1 = await logger.notify_voice(
            voice_channel_id=1356518373097214022,
            message="これは接続前のテストです",
            priority="normal",
            speaker_id=1,
        )
        print(f"Result: {result1}")
        print()

        print("Now please connect the bot using !join command in Discord...")
        print("Waiting 30 seconds for you to type: !join 1356518373097214022")
        await asyncio.sleep(30)

        print("\nTest 2: Sending voice notification WITH persistent connection")
        print("Expected: Audio plays in connected voice channel, bot stays connected")
        result2 = await logger.notify_voice(
            voice_channel_id=1356518373097214022,
            message="接続されました。音声テスト成功です",
            priority="normal",
            speaker_id=1,
        )
        print(f"Result: {result2}")
        print()

        print("Test 3: Sending another notification (bot should still be connected)")
        await asyncio.sleep(2)
        result3 = await logger.notify_voice(
            voice_channel_id=1356518373097214022,
            message="２回目のテストです",
            priority="high",
            speaker_id=3,  # Different speaker
        )
        print(f"Result: {result3}")
        print()

        print("✅ All tests completed!")
        print("The bot should still be connected to the voice channel.")
        print("Use !leave in Discord to disconnect.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("\nKeeping connection alive for 60 seconds...")
        print("You can test more notifications or use !leave to disconnect")
        await asyncio.sleep(60)

        print("\nClosing Discord connection...")
        await logger.close()
        print("Done!")


if __name__ == "__main__":
    try:
        asyncio.run(test_persistent_voice())
    except KeyboardInterrupt:
        print("\nTest cancelled by user")
        sys.exit(0)
