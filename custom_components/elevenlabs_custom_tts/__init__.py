"""The ElevenLabs Custom TTS integration."""

from __future__ import annotations

import logging
import os
from typing import Any

from elevenlabs import AsyncElevenLabs, VoiceSettings
from elevenlabs.core import ApiError
from httpx import ConnectError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers.httpx_client import get_async_client

from .const import (
    DOMAIN,
    SERVICE_GET_VOICES,
    SERVICE_GENERATE_VOICE,
    ATTR_TEXT,
    ATTR_MODEL_ID,
    ATTR_VOICE_ID,
    ATTR_STABILITY,
    ATTR_USE_SPEAKER_BOOST,
    ATTR_SIMILARITY_BOOST,
    ATTR_STYLE,
    ATTR_SPEED,
    ATTR_OUTPUT_PATH,
    DEFAULT_MODEL,
    DEFAULT_STABILITY,
    DEFAULT_SIMILARITY_BOOST,
    DEFAULT_STYLE,
    DEFAULT_SPEED,
    DEFAULT_USE_SPEAKER_BOOST,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ElevenLabs Custom TTS from a config entry."""
    
    # Store the client in hass.data
    httpx_client = get_async_client(hass)
    client = AsyncElevenLabs(
        api_key=entry.data[CONF_API_KEY], 
        httpx_client=httpx_client
    )
    
    # Test the connection
    try:
        await client.voices.get_all()
    except ConnectError as err:
        raise ConfigEntryNotReady("Failed to connect to ElevenLabs") from err
    except ApiError as err:
        raise ConfigEntryNotReady("Authentication failed") from err
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = client
    
    # Register services
    await _async_register_services(hass, client)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id, None)
    
    # Unregister services if this is the last entry
    if not hass.data[DOMAIN]:
        hass.services.async_remove(DOMAIN, SERVICE_GET_VOICES)
        hass.services.async_remove(DOMAIN, SERVICE_GENERATE_VOICE)
    
    return True


async def _async_register_services(hass: HomeAssistant, client: AsyncElevenLabs) -> None:
    """Register the services."""
    
    async def get_voices_service(call: ServiceCall) -> ServiceResponse:
        """Service to get all available voices."""
        try:
            voices_response = await client.voices.get_all()
            voices_list = []
            
            for voice in voices_response.voices:
                voice_data = {
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "category": voice.category,
                }
                if hasattr(voice, 'description') and voice.description:
                    voice_data["description"] = voice.description
                if hasattr(voice, 'labels') and voice.labels:
                    voice_data["labels"] = voice.labels
                    
                voices_list.append(voice_data)
                
            return {"voices": voices_list}
            
        except ApiError as exc:
            _LOGGER.error("Error fetching voices: %s", exc)
            raise HomeAssistantError(f"Failed to fetch voices: {exc}") from exc
    
    async def generate_voice_service(call: ServiceCall) -> ServiceResponse:
        """Service to generate voice with custom options."""
        text = call.data[ATTR_TEXT]
        model_id = call.data.get(ATTR_MODEL_ID, DEFAULT_MODEL)
        voice_id = call.data[ATTR_VOICE_ID]
        stability = call.data.get(ATTR_STABILITY, DEFAULT_STABILITY)
        similarity_boost = call.data.get(ATTR_SIMILARITY_BOOST, DEFAULT_SIMILARITY_BOOST)
        style = call.data.get(ATTR_STYLE, DEFAULT_STYLE)
        speed = call.data.get(ATTR_SPEED, DEFAULT_SPEED)
        use_speaker_boost = call.data.get(ATTR_USE_SPEAKER_BOOST, DEFAULT_USE_SPEAKER_BOOST)
        output_path = call.data.get(ATTR_OUTPUT_PATH)
        
        voice_settings = VoiceSettings(
            stability=stability,
            similarity_boost=similarity_boost,
            style=style,
            use_speaker_boost=use_speaker_boost,
        )
        
        try:
            # Note: ElevenLabs Python SDK doesn't support speed parameter in the current version
            # We'll generate without speed for now and log a warning if speed != 1.0
            if speed != 1.0:
                _LOGGER.warning(
                    "Speed parameter (%s) is not supported in current ElevenLabs SDK version. "
                    "Using default speed.", speed
                )
            
            audio_generator = client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id=model_id,
                voice_settings=voice_settings,
            )
            
            # Collect all audio bytes
            audio_bytes = b"".join([chunk async for chunk in audio_generator])
            
            response_data = {
                "success": True,
                "audio_size": len(audio_bytes),
                "parameters": {
                    "text": text,
                    "model_id": model_id,
                    "voice_id": voice_id,
                    "stability": stability,
                    "similarity_boost": similarity_boost,
                    "style": style,
                    "speed": speed,
                    "use_speaker_boost": use_speaker_boost,
                },
            }
            
            # Save to file if output_path is provided
            if output_path:
                try:
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    with open(output_path, "wb") as f:
                        f.write(audio_bytes)
                    
                    response_data["output_path"] = output_path
                    _LOGGER.info("Audio saved to %s", output_path)
                    
                except OSError as exc:
                    _LOGGER.error("Failed to save audio to %s: %s", output_path, exc)
                    response_data["error"] = f"Failed to save file: {exc}"
            else:
                # Return audio data as base64 if no output path
                import base64
                response_data["audio_data"] = base64.b64encode(audio_bytes).decode()
                
            return response_data
            
        except ApiError as exc:
            _LOGGER.error("Error generating voice: %s", exc)
            raise HomeAssistantError(f"Failed to generate voice: {exc}") from exc
    
    # Register the services
    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_VOICES,
        get_voices_service,
        supports_response=SupportsResponse.ONLY,
    )
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_GENERATE_VOICE,
        generate_voice_service,
        supports_response=SupportsResponse.ONLY,
    )