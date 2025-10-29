"""Tests for VoiceVox client."""

import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from src.voicevox_client import VoiceVoxClient


@pytest.mark.usefixtures("isolate_env")
class TestVoiceVoxClient:
    """Test suite for VoiceVoxClient class."""

    @pytest.fixture
    def client(self):
        """Create a VoiceVoxClient instance."""
        return VoiceVoxClient(base_url="http://localhost:50021")

    @pytest.mark.asyncio
    async def test_is_available_success(self, client):
        """Test is_available returns True when server is reachable."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await client.is_available()

            assert result is True

    @pytest.mark.asyncio
    async def test_is_available_failure(self, client):
        """Test is_available returns False when server is unreachable."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.ConnectError("Connection failed")
            )

            result = await client.is_available()

            assert result is False

    @pytest.mark.asyncio
    async def test_is_available_timeout(self, client):
        """Test is_available returns False on timeout."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.TimeoutException("Timeout")
            )

            result = await client.is_available()

            assert result is False

    @pytest.mark.asyncio
    async def test_create_audio_query_success(self, client):
        """Test create_audio_query returns audio query data."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {"query": "data"}
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await client.create_audio_query("こんにちは", speaker_id=1)

            assert result == {"query": "data"}

    @pytest.mark.asyncio
    async def test_synthesize_success(self, client):
        """Test synthesize returns audio data."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.content = b"audio-data"
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            audio_query = {"query": "data"}
            result = await client.synthesize(audio_query, speaker_id=1)

            assert result == b"audio-data"

    @pytest.mark.asyncio
    async def test_text_to_speech_success(self, client):
        """Test text_to_speech complete pipeline."""
        with patch.object(client, "create_audio_query", new_callable=AsyncMock) as mock_query, \
             patch.object(client, "synthesize", new_callable=AsyncMock) as mock_synth:

            mock_query.return_value = {"query": "data"}
            mock_synth.return_value = b"audio-data"

            result = await client.text_to_speech("こんにちは", speaker_id=1)

            assert result == b"audio-data"
            mock_query.assert_awaited_once_with("こんにちは", 1)
            mock_synth.assert_awaited_once_with({"query": "data"}, 1)

    @pytest.mark.asyncio
    async def test_text_to_speech_different_speaker(self, client):
        """Test text_to_speech with different speaker ID."""
        with patch.object(client, "create_audio_query", new_callable=AsyncMock) as mock_query, \
             patch.object(client, "synthesize", new_callable=AsyncMock) as mock_synth:

            mock_query.return_value = {"query": "data"}
            mock_synth.return_value = b"audio-data"

            result = await client.text_to_speech("テストです", speaker_id=3)

            assert result == b"audio-data"
            mock_query.assert_awaited_once_with("テストです", 3)
            mock_synth.assert_awaited_once_with({"query": "data"}, 3)

    def test_client_initialization(self):
        """Test VoiceVoxClient initialization with custom URL."""
        client = VoiceVoxClient(base_url="http://custom:8080")
        assert client.base_url == "http://custom:8080"

    def test_client_default_url(self):
        """Test VoiceVoxClient initialization with default URL."""
        client = VoiceVoxClient()
        assert client.base_url == "http://localhost:50021"
