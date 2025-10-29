#!/usr/bin/env python3
"""Simple script to test voice notification functionality."""

import asyncio
import sys
import pytest
from src.discord_logger import DiscordLogger
from src.settings import get_settings


@pytest.mark.integration
async def test_voice_notification():
    """Test voice notification."""
    # Load settings
    settings = get_settings()

    # Voice channel ID to test
    VOICE_CHANNEL_ID = 1356518373097214022

    print("Initializing Discord logger...")
    logger = DiscordLogger(
        token=settings.discord_token,
        log_channel_id=settings.log_channel_id,
        log_thread_name="Voice Test",
        voicevox_url=settings.voicevox_url,
    )

    print("Starting Discord client...")
    await logger.start()

    # Wait a bit for Discord to be ready
    await asyncio.sleep(3)

    try:
        print(f"\nSending voice notification to channel {VOICE_CHANNEL_ID}...")
        result = await logger.notify_voice(
            voice_channel_id=VOICE_CHANNEL_ID,
            message="こんにちは、音声テストです",
            priority="normal",
            speaker_id=1,
        )

        print("\n✅ Success!")
        print(f"Result: {result}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        print("\nClosing Discord connection...")
        await logger.close()
        print("Done!")


if __name__ == "__main__":
    try:
        asyncio.run(test_voice_notification())
    except KeyboardInterrupt:
        print("\nTest cancelled by user")
        sys.exit(0)
