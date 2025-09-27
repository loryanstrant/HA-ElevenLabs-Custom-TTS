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
from homeassistant.components.media_player import DOMAIN as MEDIA_PLAYER_DOMAIN

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
    ATTR_VOICE_TYPE,
    ATTR_SEARCH_TEXT,
    ATTR_MEDIA_PLAYER_ENTITY,
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
    
    # Skip connection test during setup since it's already validated in config flow
    # The blocking import_module warning was occurring here due to pydantic imports
    # during the voices.get_all() call in the async event loop
    
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
        """Service to get all available voices with optional filtering."""
        voice_type = call.data.get(ATTR_VOICE_TYPE)
        search_text = call.data.get(ATTR_SEARCH_TEXT, "").lower().strip()
        
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
                
                # Apply voice type filter
                if voice_type and voice.category != voice_type:
                    continue
                
                # Apply search text filter
                if search_text:
                    searchable_text = f"{voice.name.lower()} {voice.category.lower()}"
                    if hasattr(voice, 'description') and voice.description:
                        searchable_text += f" {voice.description.lower()}"
                    if hasattr(voice, 'labels') and voice.labels:
                        searchable_text += f" {' '.join(voice.labels).lower()}"
                    
                    if search_text not in searchable_text:
                        continue
                
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
        media_player_entity = call.data.get(ATTR_MEDIA_PLAYER_ENTITY)
        
        voice_settings = VoiceSettings(
            stability=stability,
            similarity_boost=similarity_boost,
            style=style,
            use_speaker_boost=use_speaker_boost,
            speed=speed,
        )
        
        try:
            # Prepare conversion parameters
            convert_params = {
                "text": text,
                "voice_id": voice_id,
                "model_id": model_id,
                "voice_settings": voice_settings,
            }
            
            # Generate audio with speed parameter now properly included in voice_settings
            audio_generator = client.text_to_speech.convert(**convert_params)
            
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
            
            # Handle different output options
            if media_player_entity:
                # Send audio to media player entity
                try:
                    # Create a temporary file for the media player
                    import tempfile
                    import os
                    
                    # Create temporary file with .mp3 extension
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                        temp_file.write(audio_bytes)
                        temp_path = temp_file.name
                    
                    # Use Home Assistant's media player service to play the audio
                    await hass.services.async_call(
                        MEDIA_PLAYER_DOMAIN,
                        "play_media",
                        {
                            "entity_id": media_player_entity,
                            "media_content_id": f"file://{temp_path}",
                            "media_content_type": "music",
                        },
                        blocking=False,
                    )
                    
                    response_data["media_player_entity"] = media_player_entity
                    response_data["temp_file"] = temp_path
                    _LOGGER.info("Audio sent to media player %s", media_player_entity)
                    
                    # Clean up temporary file after a delay (optional)
                    # Note: We keep the file for now as the media player may need time to read it
                    
                except Exception as exc:
                    _LOGGER.error("Failed to send audio to media player %s: %s", media_player_entity, exc)
                    response_data["error"] = f"Failed to send to media player: {exc}"
            
            elif output_path:
                # Save to file if output_path is provided
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
                # Return audio data as base64 if no output path or media player
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