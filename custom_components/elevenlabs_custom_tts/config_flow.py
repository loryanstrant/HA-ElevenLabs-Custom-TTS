"""Config flow for ElevenLabs Custom TTS integration."""

from __future__ import annotations

import logging
from typing import Any

from elevenlabs import AsyncElevenLabs
from elevenlabs.core import ApiError
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.httpx_client import get_async_client

from .const import (
    DOMAIN,
    DEFAULT_MODEL,
    DEFAULT_STABILITY,
    DEFAULT_SIMILARITY_BOOST,
    DEFAULT_STYLE,
    DEFAULT_SPEED,
    DEFAULT_USE_SPEAKER_BOOST,
)

USER_STEP_SCHEMA = vol.Schema({vol.Required(CONF_API_KEY): str})

_LOGGER = logging.getLogger(__name__)


async def validate_api_key(hass: HomeAssistant, api_key: str) -> bool:
    """Validate the API key by testing it with ElevenLabs API."""
    httpx_client = get_async_client(hass)
    client = AsyncElevenLabs(api_key=api_key, httpx_client=httpx_client)
    
    def _test_api_key():
        """Test API key synchronously to avoid blocking import_module calls."""
        import asyncio
        try:
            # Create a new event loop for this executor thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(client.voices.get_all())
            finally:
                loop.close()
        except ApiError:
            return None
    
    try:
        result = await hass.async_add_executor_job(_test_api_key)
        return result is not None
    except Exception:
        return False


class ElevenLabsCustomTTSConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ElevenLabs Custom TTS."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get options flow."""
        return ElevenLabsOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            api_key = user_input[CONF_API_KEY]
            
            # Check if API key is already configured
            await self.async_set_unique_id(api_key)
            self._abort_if_unique_id_configured()
            
            # Validate API key
            if await validate_api_key(self.hass, api_key):
                return self.async_create_entry(
                    title="ElevenLabs Custom TTS",
                    data=user_input,
                    options={"voice_profiles": {}},  # Initialize empty voice profiles
                )
            else:
                errors["base"] = "invalid_api_key"
                
        return self.async_show_form(
            step_id="user",
            data_schema=USER_STEP_SCHEMA,
            errors=errors,
        )


class ElevenLabsOptionsFlow(OptionsFlow):
    """Handle options flow for ElevenLabs Custom TTS."""

    def __init__(self, config_entry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage voice profiles."""
        if user_input is not None:
            if user_input.get("action") == "add_profile":
                return await self.async_step_add_profile()
            elif user_input.get("action") == "delete_profile":
                return await self.async_step_delete_profile()
            elif user_input.get("action") == "done":
                return self.async_create_entry(title="", data=self.config_entry.options)
        
        # Get current voice profiles
        current_profiles = self.config_entry.options.get("voice_profiles", {})
        profile_list = list(current_profiles.keys()) if current_profiles else ["No profiles configured"]
        
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional("action"): vol.In([
                    "add_profile",
                    "delete_profile", 
                    "done"
                ])
            }),
            description_placeholders={
                "current_profiles": "\n".join(f"• {profile}" for profile in profile_list)
            }
        )

    async def async_step_add_profile(self, user_input: dict[str, Any] | None = None):
        """Add a new voice profile."""
        errors = {}
        
        if user_input is not None:
            profile_name = user_input["profile_name"]
            
            # Check if profile already exists
            current_profiles = self.config_entry.options.get("voice_profiles", {})
            if profile_name in current_profiles:
                errors["profile_name"] = "profile_exists"
            else:
                # Create new profile
                new_profile = {
                    "voice": user_input["voice"],
                    "model_id": user_input.get("model_id", DEFAULT_MODEL),
                    "stability": user_input.get("stability", DEFAULT_STABILITY),
                    "similarity_boost": user_input.get("similarity_boost", DEFAULT_SIMILARITY_BOOST),
                    "style": user_input.get("style", DEFAULT_STYLE),
                    "speed": user_input.get("speed", DEFAULT_SPEED),
                    "use_speaker_boost": user_input.get("use_speaker_boost", DEFAULT_USE_SPEAKER_BOOST),
                }
                
                # Update options
                updated_profiles = current_profiles.copy()
                updated_profiles[profile_name] = new_profile
                
                new_options = self.config_entry.options.copy()
                new_options["voice_profiles"] = updated_profiles
                
                return self.async_create_entry(title="", data=new_options)
        
        return self.async_show_form(
            step_id="add_profile",
            data_schema=vol.Schema({
                vol.Required("profile_name"): str,
                vol.Required("voice"): str,
                vol.Optional("model_id", default=DEFAULT_MODEL): str,
                vol.Optional("stability", default=DEFAULT_STABILITY): vol.All(
                    vol.Coerce(float), vol.Range(min=0, max=1)
                ),
                vol.Optional("similarity_boost", default=DEFAULT_SIMILARITY_BOOST): vol.All(
                    vol.Coerce(float), vol.Range(min=0, max=1)
                ),
                vol.Optional("style", default=DEFAULT_STYLE): vol.All(
                    vol.Coerce(float), vol.Range(min=0, max=1)
                ),
                vol.Optional("speed", default=DEFAULT_SPEED): vol.All(
                    vol.Coerce(float), vol.Range(min=0.25, max=4.0)
                ),
                vol.Optional("use_speaker_boost", default=DEFAULT_USE_SPEAKER_BOOST): bool,
            }),
            errors=errors,
        )

    async def async_step_delete_profile(self, user_input: dict[str, Any] | None = None):
        """Delete a voice profile."""
        current_profiles = self.config_entry.options.get("voice_profiles", {})
        
        if not current_profiles:
            # No profiles to delete, go back to main menu
            return await self.async_step_init()
        
        if user_input is not None:
            profile_to_delete = user_input["profile_name"]
            
            # Remove profile
            updated_profiles = current_profiles.copy()
            if profile_to_delete in updated_profiles:
                del updated_profiles[profile_to_delete]
            
            new_options = self.config_entry.options.copy()
            new_options["voice_profiles"] = updated_profiles
            
            return self.async_create_entry(title="", data=new_options)
        
        return self.async_show_form(
            step_id="delete_profile",
            data_schema=vol.Schema({
                vol.Required("profile_name"): vol.In(list(current_profiles.keys()))
            })
        )