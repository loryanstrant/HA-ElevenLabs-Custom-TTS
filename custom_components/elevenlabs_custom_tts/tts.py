"""ElevenLabs TTS platform."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import async_timeout
from elevenlabs import VoiceSettings
from elevenlabs.core import ApiError

from homeassistant.components.tts import TextToSpeechEntity, TtsAudioType
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from .const import (
    DOMAIN,
    DEFAULT_MODEL,
    DEFAULT_STABILITY,
    DEFAULT_SIMILARITY_BOOST,
    DEFAULT_STYLE,
    DEFAULT_SPEED,
    DEFAULT_USE_SPEAKER_BOOST,
)

_LOGGER = logging.getLogger(__name__)

SUPPORT_LANGUAGES = ["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh", "ja", "hu", "ko"]

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ElevenLabs TTS platform via config entry."""
    # Get the client from the integration data
    if DOMAIN not in hass.data or config_entry.entry_id not in hass.data[DOMAIN]:
        _LOGGER.error("ElevenLabs integration not loaded")
        return
        
    client = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([ElevenLabsTTSProvider(hass, client)])


class ElevenLabsTTSProvider(TextToSpeechEntity):
    """ElevenLabs TTS provider."""

    def __init__(self, hass: HomeAssistant, client) -> None:
        """Initialize ElevenLabs TTS provider."""
        self.hass = hass
        self._client = client
        self._name = "ElevenLabs"

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def default_language(self) -> str:
        """Return the default language."""
        return "en"

    @property
    def supported_languages(self) -> list[str]:
        """Return list of supported languages."""
        return SUPPORT_LANGUAGES

    @property
    def supported_options(self) -> list[str]:
        """Return list of supported options."""
        return [
            "voice",
            "model_id", 
            "stability",
            "similarity_boost",
            "style",
            "speed",
            "use_speaker_boost"
        ]

    @property
    def default_options(self) -> dict[str, Any]:
        """Return dict of default options."""
        return {
            "voice": "21m00Tcm4TlvDq8ikWAM",  # Default Rachel voice
            "model_id": DEFAULT_MODEL,
            "stability": DEFAULT_STABILITY,
            "similarity_boost": DEFAULT_SIMILARITY_BOOST,
            "style": DEFAULT_STYLE,
            "speed": DEFAULT_SPEED,
            "use_speaker_boost": DEFAULT_USE_SPEAKER_BOOST,
        }

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict[str, Any] | None = None
    ) -> TtsAudioType:
        """Load TTS audio file from ElevenLabs."""
        if options is None:
            options = {}
            
        # Merge provided options with defaults
        merged_options = {**self.default_options, **options}
        
        voice_id = merged_options["voice"]
        model_id = merged_options["model_id"]
        stability = merged_options["stability"]
        similarity_boost = merged_options["similarity_boost"]
        style = merged_options["style"]
        speed = merged_options["speed"]
        use_speaker_boost = merged_options["use_speaker_boost"]
        
        voice_settings = VoiceSettings(
            stability=stability,
            similarity_boost=similarity_boost,
            style=style,
            use_speaker_boost=use_speaker_boost,
            speed=speed,
        )
        
        def _generate_audio_sync():
            """Generate audio synchronously to avoid blocking the event loop."""
            # Prepare conversion parameters
            convert_params = {
                "text": message,
                "voice_id": voice_id,
                "model_id": model_id,
                "voice_settings": voice_settings,
            }
            
            # Generate audio with ElevenLabs
            audio_generator = self._client.text_to_speech.convert(**convert_params)
            
            # Collect all audio bytes
            return b"".join([chunk for chunk in audio_generator])
        
        try:
            with async_timeout.timeout(30):
                # Run the blocking operation in an executor thread
                audio_bytes = await self.hass.async_add_executor_job(_generate_audio_sync)
                
                if not audio_bytes:
                    _LOGGER.error("No audio data received from ElevenLabs")
                    return None
                    
                _LOGGER.info(
                    "Successfully generated %d bytes of audio for voice %s",
                    len(audio_bytes),
                    voice_id
                )
                
                return ("mp3", audio_bytes)
                
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout generating TTS audio")
            return None
        except ApiError as err:
            _LOGGER.error("ElevenLabs API error: %s", err)
            return None
        except Exception as err:
            _LOGGER.error("Error generating TTS audio: %s", err)
            return None