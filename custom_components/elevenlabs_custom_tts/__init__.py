"""The ElevenLabs Custom TTS integration."""

from __future__ import annotations

import hashlib
import logging

from elevenlabs import AsyncElevenLabs
from elevenlabs.core import ApiError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant, callback, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.httpx_client import get_async_client

from .const import (
    DOMAIN,
    SERVICE_GET_VOICES,
    ATTR_VOICE_TYPE,
    ATTR_SEARCH_TEXT,
)

_LOGGER = logging.getLogger(__name__)


def api_key_unique_id(api_key: str) -> str:
    """Derive a stable unique ID from the API key without storing the key itself."""
    return hashlib.sha256(api_key.encode()).hexdigest()


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old config entries."""
    if entry.version == 1:
        # v1 used the raw API key as the unique ID, which leaks it into
        # registries, diagnostics and logs. Replace it with a hash.
        # The TTS entity's unique ID also becomes per-entry; migrate it in place
        # so the existing entity_id (and any automations using it) is kept.
        @callback
        def _migrate_entity(entity_entry: er.RegistryEntry) -> dict | None:
            if entity_entry.unique_id == f"{DOMAIN}_tts":
                return {"new_unique_id": f"{DOMAIN}_{entry.entry_id}"}
            return None

        await er.async_migrate_entries(hass, entry.entry_id, _migrate_entity)
        hass.config_entries.async_update_entry(
            entry,
            unique_id=api_key_unique_id(entry.data[CONF_API_KEY]),
            version=2,
        )
        _LOGGER.info("Migrated ElevenLabs Custom TTS entry to version 2")
    return True


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
                    searchable_text = f"{(voice.name or '').lower()} {(voice.category or '').lower()}"
                    if hasattr(voice, 'description') and voice.description:
                        searchable_text += f" {voice.description.lower()}"
                    if hasattr(voice, 'labels') and voice.labels:
                        # labels is a dict (e.g. {"accent": "british"}); search keys and values
                        label_terms = [f"{k} {v}" for k, v in voice.labels.items()]
                        searchable_text += f" {' '.join(label_terms).lower()}"
                    
                    if search_text not in searchable_text:
                        continue
                
                voices_list.append(voice_data)
                
            return {"voices": voices_list}
            
        except ApiError as exc:
            # str(ApiError) dumps every response header; status and body say the same thing
            _LOGGER.error(
                "Error fetching voices: API error %s: %s", exc.status_code, exc.body
            )
            raise HomeAssistantError(
                f"Failed to fetch voices: ElevenLabs API error {exc.status_code}: {exc.body}"
            ) from exc

    # Register the services
    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_VOICES,
        get_voices_service,
        supports_response=SupportsResponse.ONLY,
    )