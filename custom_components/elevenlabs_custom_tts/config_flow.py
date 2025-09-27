"""Config flow for ElevenLabs Custom TTS integration."""

from __future__ import annotations

import logging
from typing import Any

from elevenlabs import AsyncElevenLabs
from elevenlabs.core import ApiError
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.httpx_client import get_async_client

from .const import DOMAIN

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
                )
            else:
                errors["base"] = "invalid_api_key"
                
        return self.async_show_form(
            step_id="user",
            data_schema=USER_STEP_SCHEMA,
            errors=errors,
        )