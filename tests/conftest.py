"""Fixtures for ElevenLabs Custom TTS tests."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading custom_components in every test."""
    yield


@pytest.fixture
def mock_client():
    """Patch AsyncElevenLabs everywhere it is constructed."""
    client = MagicMock()
    tts_model = MagicMock(model_id="eleven_v3", can_do_text_to_speech=True)
    sts_model = MagicMock(model_id="eleven_english_sts_v2", can_do_text_to_speech=False)
    client.models.list = AsyncMock(return_value=[tts_model, sts_model])

    async def _convert(**kwargs):
        client.last_convert_kwargs = kwargs
        yield b"abc"
        yield b"def"

    client.text_to_speech.convert = MagicMock(side_effect=_convert)
    with (
        patch("custom_components.elevenlabs_custom_tts.AsyncElevenLabs", return_value=client),
        patch("custom_components.elevenlabs_custom_tts.config_flow.AsyncElevenLabs", return_value=client),
    ):
        yield client
