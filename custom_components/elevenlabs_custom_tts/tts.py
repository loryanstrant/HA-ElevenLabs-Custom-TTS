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
    async_add_entities([ElevenLabsTTSProvider(hass, client, config_entry)])


class ElevenLabsTTSProvider(TextToSpeechEntity):
    """ElevenLabs TTS provider."""

    def __init__(self, hass: HomeAssistant, client, config_entry: ConfigEntry) -> None:
        """Initialize ElevenLabs TTS provider."""
        self.hass = hass
        self._client = client
        self._config_entry = config_entry
        self._name = "elevenlabs_custom_tts"  # This creates the entity ID: tts.elevenlabs_custom_tts
        self._attr_name = "ElevenLabs Custom TTS"  # This sets the display name
        self._attr_friendly_name = "ElevenLabs Custom TTS"  # Alternative display name attribute

    @property
    def name(self) -> str:
        """Return the name of the entity (used for entity ID)."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique ID for this TTS entity."""
        return f"{DOMAIN}_tts"

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
            "voice_profile",
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
            
        # Check if voice_profile is provided
        voice_profile_name = options.get("voice_profile")
        if voice_profile_name:
            # Get voice profiles from config entry
            voice_profiles = self._config_entry.options.get("voice_profiles", {})
            if voice_profile_name in voice_profiles:
                # Use voice profile settings as base, allow options to override
                profile_options = voice_profiles[voice_profile_name].copy()
                profile_options.update({k: v for k, v in options.items() if k != "voice_profile"})
                merged_options = {**self.default_options, **profile_options}
                _LOGGER.info("Using voice profile '%s' with settings: %s", voice_profile_name, profile_options)
            else:
                _LOGGER.warning("Voice profile '%s' not found, using default options", voice_profile_name)
                merged_options = {**self.default_options, **options}
        else:
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
        
        try:
            with async_timeout.timeout(30):
                # Prepare conversion parameters
                convert_params = {
                    "text": message,
                    "voice_id": voice_id,
                    "model_id": model_id,
                    "voice_settings": voice_settings,
                }
                
                # Generate audio with ElevenLabs (async generator)
                audio_generator = self._client.text_to_speech.convert(**convert_params)
                
                # Collect all audio bytes from async generator
                audio_bytes = b""
                async for chunk in audio_generator:
                    audio_bytes += chunk
                
                if not audio_bytes:
                    _LOGGER.error("No audio data received from ElevenLabs")
                    return None
                    
                _LOGGER.info(
                    "Successfully generated %d bytes of audio for voice %s%s",
                    len(audio_bytes),
                    voice_id,
                    f" using profile '{voice_profile_name}'" if voice_profile_name else ""
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