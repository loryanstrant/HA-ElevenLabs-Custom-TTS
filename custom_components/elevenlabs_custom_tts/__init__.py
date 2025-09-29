"""The ElevenLabs Custom TTS integration."""

from __future__ import annotations

import logging

from elevenlabs import AsyncElevenLabs
from elevenlabs.core import ApiError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.httpx_client import get_async_client

from .const import (
    DOMAIN,
    SERVICE_GET_VOICES,
    SERVICE_SAVE_VOICE_PROFILE,
    ATTR_VOICE_TYPE,
    ATTR_SEARCH_TEXT,
    ATTR_PROFILE_NAME,
    ATTR_VOICE,
    ATTR_MODEL_ID,
    ATTR_STABILITY,
    ATTR_SIMILARITY_BOOST,
    ATTR_STYLE,
    ATTR_SPEED,
    ATTR_USE_SPEAKER_BOOST,
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
    
    # Set up TTS platform
    await hass.config_entries.async_forward_entry_setups(entry, ["tts"])
    
    # Register services
    await _async_register_services(hass, client)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload TTS platform
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["tts"])
    
    hass.data[DOMAIN].pop(entry.entry_id, None)
    
    # Unregister services if this is the last entry
    if not hass.data[DOMAIN]:
        hass.services.async_remove(DOMAIN, SERVICE_GET_VOICES)
        hass.services.async_remove(DOMAIN, SERVICE_SAVE_VOICE_PROFILE)
    
    return unload_ok


async def _async_register_services(hass: HomeAssistant, client: AsyncElevenLabs) -> None:
    """Register the services."""
    
    async def get_voices_service(call: ServiceCall) -> ServiceResponse:
        """Service to get all available voices with optional filtering."""
        voice_type = call.data.get(ATTR_VOICE_TYPE)
        search_text = call.data.get(ATTR_SEARCH_TEXT, "").lower().strip()
        
        # Get the first available client from hass.data
        entry_clients = list(hass.data[DOMAIN].values())
        if not entry_clients:
            raise HomeAssistantError("No ElevenLabs client available")
        client = entry_clients[0]
        
        try:
            # Use the async client directly but handle the blocking import properly
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

    async def save_voice_profile_service(call: ServiceCall) -> None:
        """Service to save a voice profile with settings."""
        profile_name = call.data.get(ATTR_PROFILE_NAME)
        voice = call.data.get(ATTR_VOICE)
        
        if not profile_name or not voice:
            raise HomeAssistantError("Profile name and voice are required")
        
        # Build profile data
        profile_data = {
            "voice": voice,
            "model_id": call.data.get(ATTR_MODEL_ID, DEFAULT_MODEL),
            "stability": call.data.get(ATTR_STABILITY, DEFAULT_STABILITY),
            "similarity_boost": call.data.get(ATTR_SIMILARITY_BOOST, DEFAULT_SIMILARITY_BOOST),
            "style": call.data.get(ATTR_STYLE, DEFAULT_STYLE),
            "speed": call.data.get(ATTR_SPEED, DEFAULT_SPEED),
            "use_speaker_boost": call.data.get(ATTR_USE_SPEAKER_BOOST, DEFAULT_USE_SPEAKER_BOOST),
        }
        
        # Find the first config entry to save the profile to
        config_entries = hass.config_entries.async_entries(DOMAIN)
        if not config_entries:
            raise HomeAssistantError("No ElevenLabs integration configured")
        
        config_entry = config_entries[0]
        
        # Update options with the new profile
        options = config_entry.options.copy()
        voice_profiles = options.get("voice_profiles", {})
        voice_profiles[profile_name] = profile_data
        options["voice_profiles"] = voice_profiles
        
        # Update the config entry
        hass.config_entries.async_update_entry(config_entry, options=options)
        
        _LOGGER.info("Saved voice profile '%s' with voice '%s'", profile_name, voice)
    
    # Register the services
    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_VOICES,
        get_voices_service,
        supports_response=SupportsResponse.ONLY,
    )
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_SAVE_VOICE_PROFILE,
        save_voice_profile_service,
    )