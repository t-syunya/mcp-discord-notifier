"""VoiceVox API client for text-to-speech conversion."""

import asyncio
import io
from typing import Optional

import httpx


class VoiceVoxClient:
    """Client for VoiceVox Engine API."""

    def __init__(self, base_url: str = "http://localhost:50021"):
        """Initialize VoiceVox client.

        Args:
            base_url: Base URL of VoiceVox Engine API (default: http://localhost:50021)
        """
        self.base_url = base_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    async def get_speakers(self) -> list[dict]:
        """Get list of available speakers.

        Returns:
            List of speaker information dictionaries
        """
        if not self._client:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.base_url}/speakers")
                response.raise_for_status()
                return response.json()
        else:
            response = await self._client.get(f"{self.base_url}/speakers")
            response.raise_for_status()
            return response.json()

    async def create_audio_query(self, text: str, speaker_id: int = 1) -> dict:
        """Create audio query for text.

        Args:
            text: Text to convert to speech
            speaker_id: Speaker ID (default: 1, which is typically "四国めたん (ノーマル)")

        Returns:
            Audio query dictionary
        """
        if not self._client:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/audio_query",
                    params={"text": text, "speaker": speaker_id},
                )
                response.raise_for_status()
                return response.json()
        else:
            response = await self._client.post(
                f"{self.base_url}/audio_query",
                params={"text": text, "speaker": speaker_id},
            )
            response.raise_for_status()
            return response.json()

    async def synthesize(
        self, audio_query: dict, speaker_id: int = 1
    ) -> bytes:
        """Synthesize speech from audio query.

        Args:
            audio_query: Audio query dictionary from create_audio_query
            speaker_id: Speaker ID (default: 1)

        Returns:
            WAV audio data as bytes
        """
        if not self._client:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/synthesis",
                    params={"speaker": speaker_id},
                    json=audio_query,
                )
                response.raise_for_status()
                return response.content
        else:
            response = await self._client.post(
                f"{self.base_url}/synthesis",
                params={"speaker": speaker_id},
                json=audio_query,
            )
            response.raise_for_status()
            return response.content

    async def text_to_speech(
        self, text: str, speaker_id: int = 1
    ) -> bytes:
        """Convert text to speech in one call.

        Args:
            text: Text to convert to speech
            speaker_id: Speaker ID (default: 1)

        Returns:
            WAV audio data as bytes
        """
        audio_query = await self.create_audio_query(text, speaker_id)
        return await self.synthesize(audio_query, speaker_id)

    async def is_available(self) -> bool:
        """Check if VoiceVox Engine is available.

        Returns:
            True if VoiceVox is available, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/version")
                return response.status_code == 200
        except Exception:
            return False
