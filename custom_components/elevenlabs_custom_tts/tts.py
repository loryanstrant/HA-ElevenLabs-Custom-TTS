"""ElevenLabs TTS platform."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from elevenlabs import VoiceSettings
from elevenlabs.core import ApiError

from homeassistant.components.tts import TextToSpeechEntity, TtsAudioType, Voice
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
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
    DEFAULT_APPLY_TEXT_NORMALIZATION,
    MODELS_WITHOUT_LANGUAGE_CODE,
    TTS_TIMEOUT,
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


def _merge_options(
    defaults: dict[str, Any],
    profile: dict[str, Any] | None,
    call_options: dict[str, Any],
) -> dict[str, Any]:
    """Decide the final TTS settings from defaults, a voice profile, and per-call options.

    defaults:     integration-wide defaults (always contains every key)
    profile:      the selected voice profile's settings, or None if no profile was used
    call_options: options passed in the tts.speak call, e.g. {"speed": 1.2}
                  (when a profile is used, voice/voice_profile are already stripped)
    """
    # Preserves the original behaviour: a profile wins outright and per-call
    # options are ignored when a profile is selected.
    if profile is not None:
        return {**defaults, **profile}
    return {**defaults, **call_options}


class ElevenLabsTTSProvider(TextToSpeechEntity):
    """ElevenLabs TTS provider."""

    def __init__(self, hass: HomeAssistant, client, config_entry: ConfigEntry) -> None:
        """Initialize ElevenLabs TTS provider."""
        self.hass = hass
        self._client = client
        self._config_entry = config_entry
        # Shown in the UI; also slugifies to the tts.elevenlabs_custom_tts entity_id
        self._attr_name = "ElevenLabs Custom TTS"

    @property
    def unique_id(self) -> str:
        """Return a unique ID for this TTS entity."""
        # One entity per config entry; a fixed ID collides with multiple API keys
        return f"{DOMAIN}_{self._config_entry.entry_id}"

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
            "use_speaker_boost",
            "apply_text_normalization"
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
            "apply_text_normalization": DEFAULT_APPLY_TEXT_NORMALIZATION,
        }

    @callback
    def async_get_supported_voices(self, language: str) -> list[Voice]:
        """Return list of supported voices for Assist pipeline."""
        voices = []
        
        # Get voice profiles from config entry
        voice_profiles = self._config_entry.options.get("voice_profiles", {})
        
        _LOGGER.debug("Getting supported voices for language %s, found %d voice profiles", 
                     language, len(voice_profiles))
        
        # Add each configured voice profile as a selectable voice
        for profile_name, profile_data in voice_profiles.items():
            voice_id = profile_data.get("voice", "")
            
            # Create a Voice object for this profile
            # The voice_id in Voice() becomes the identifier used in the Assist pipeline
            # When selected, it will be passed as the "voice" option to async_get_tts_audio
            voices.append(
                Voice(
                    voice_id=profile_name,  # Use profile name as the voice identifier
                    name=profile_name,  # Display name in UI
                )
            )
            _LOGGER.debug("Added voice profile '%s' (ElevenLabs voice: %s) to supported voices", 
                         profile_name, voice_id)
        
        # If no profiles configured, return empty list to use default
        if not voices:
            _LOGGER.debug("No voice profiles configured, Assist will use default voice")
        
        return voices

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict[str, Any] | None = None
    ) -> TtsAudioType:
        """Load TTS audio file from ElevenLabs."""
        _LOGGER.debug("TTS request received for message length: %d", len(message))
        _LOGGER.debug("Language: %s", language) 
        _LOGGER.debug("Options: %s", options)
        
        if options is None:
            options = {}
        
        # Get voice profiles from config entry
        voice_profiles = self._config_entry.options.get("voice_profiles", {})
        
        # Check if voice_profile is explicitly provided
        voice_profile_name = options.get("voice_profile")
        
        # If no explicit voice_profile but "voice" is provided, check if it matches a profile name
        # This handles when Assist pipeline passes the selected voice
        if not voice_profile_name and "voice" in options:
            potential_profile = options["voice"]
            if potential_profile in voice_profiles:
                voice_profile_name = potential_profile
                _LOGGER.debug("Voice '%s' matches a voice profile, using profile settings", potential_profile)
        
        _LOGGER.debug("Voice profile requested: %s", voice_profile_name)
        
        profile = voice_profiles.get(voice_profile_name) if voice_profile_name else None
        if voice_profile_name and profile is None:
            _LOGGER.warning("Voice profile '%s' not found in profiles %s, using default options",
                          voice_profile_name, list(voice_profiles.keys()))
        
        call_options = dict(options)
        if profile is not None:
            # "voice" held the profile name, not an ElevenLabs voice ID
            call_options.pop("voice", None)
            call_options.pop("voice_profile", None)
        merged_options = _merge_options(self.default_options, profile, call_options)
        
        voice_id = merged_options["voice"]
        model_id = merged_options["model_id"]
        stability = merged_options["stability"]
        similarity_boost = merged_options["similarity_boost"]
        style = merged_options["style"]
        speed = merged_options["speed"]
        use_speaker_boost = merged_options["use_speaker_boost"]
        apply_text_normalization = merged_options["apply_text_normalization"]
        
        voice_settings = VoiceSettings(
            stability=stability,
            similarity_boost=similarity_boost,
            style=style,
            use_speaker_boost=use_speaker_boost,
            speed=speed,
        )
        
        convert_params = {
            "text": message,
            "voice_id": voice_id,
            "model_id": model_id,
            "voice_settings": voice_settings,
            "apply_text_normalization": apply_text_normalization,
        }
        if model_id not in MODELS_WITHOUT_LANGUAGE_CODE:
            convert_params["language_code"] = language
        
        try:
            async with asyncio.timeout(TTS_TIMEOUT):
                # Collect all audio bytes from the async generator
                chunks = [
                    chunk async for chunk in self._client.text_to_speech.convert(**convert_params)
                ]
        except TimeoutError as err:
            raise HomeAssistantError("Timed out generating ElevenLabs TTS audio") from err
        except ApiError as err:
            # err.body carries ElevenLabs' explanation (e.g. unsupported setting for a model)
            raise HomeAssistantError(
                f"ElevenLabs API error {err.status_code}: {err.body}"
            ) from err
        
        audio_bytes = b"".join(chunks)
        if not audio_bytes:
            raise HomeAssistantError("No audio data received from ElevenLabs")
        
        _LOGGER.debug(
            "Generated %d bytes of audio for voice %s with model %s%s",
            len(audio_bytes),
            voice_id,
            model_id,
            f" using profile '{voice_profile_name}'" if voice_profile_name else "",
        )
        return ("mp3", audio_bytes)
