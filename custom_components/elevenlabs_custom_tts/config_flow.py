"""Config flow for ElevenLabs Custom TTS integration."""

from __future__ import annotations

import logging
from typing import Any

from elevenlabs import AsyncElevenLabs
from elevenlabs.core import ApiError
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
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
    DEFAULT_APPLY_TEXT_NORMALIZATION,
)

# Schema field mappings for user-friendly labels
PROFILE_NAME_KEY = "Profile Name"
VOICE_ID_KEY = "Voice ID" 
MODEL_KEY = "Model"
STABILITY_KEY = "Voice Stability (0.0-1.0)"
SIMILARITY_KEY = "Similarity Boost (0.0-1.0)"
STYLE_KEY = "Style Exaggeration (0.0-1.0)"
SPEED_KEY = "Speech Speed (0.25-4.0)"
SPEAKER_BOOST_KEY = "Enable Speaker Boost"
APPLY_TEXT_NORMALIZATION_KEY = "Apply Text Normalization"

def _map_form_data_to_profile(user_input: dict[str, Any]) -> dict[str, Any]:
    """Map form data with friendly keys back to profile data with standard keys."""
    return {
        "voice": user_input.get(VOICE_ID_KEY, ""),
        "model_id": user_input.get(MODEL_KEY, DEFAULT_MODEL),
        "stability": user_input.get(STABILITY_KEY, DEFAULT_STABILITY),
        "similarity_boost": user_input.get(SIMILARITY_KEY, DEFAULT_SIMILARITY_BOOST),
        "style": user_input.get(STYLE_KEY, DEFAULT_STYLE),
        "speed": user_input.get(SPEED_KEY, DEFAULT_SPEED),
        "use_speaker_boost": user_input.get(SPEAKER_BOOST_KEY, DEFAULT_USE_SPEAKER_BOOST),
        "apply_text_normalization": user_input.get(APPLY_TEXT_NORMALIZATION_KEY, DEFAULT_APPLY_TEXT_NORMALIZATION ),
    }

def _map_profile_to_form_data(profile_name: str, profile_data: dict[str, Any]) -> dict[str, Any]:
    """Map profile data with standard keys to form data with friendly keys."""
    return {
        PROFILE_NAME_KEY: profile_name,
        VOICE_ID_KEY: profile_data.get("voice", ""),
        MODEL_KEY: profile_data.get("model_id", DEFAULT_MODEL),
        STABILITY_KEY: profile_data.get("stability", DEFAULT_STABILITY),
        SIMILARITY_KEY: profile_data.get("similarity_boost", DEFAULT_SIMILARITY_BOOST),
        STYLE_KEY: profile_data.get("style", DEFAULT_STYLE),
        SPEED_KEY: profile_data.get("speed", DEFAULT_SPEED),
        SPEAKER_BOOST_KEY: profile_data.get("use_speaker_boost", DEFAULT_USE_SPEAKER_BOOST),
        APPLY_TEXT_NORMALIZATION_KEY: profile_data.get("apply_text_normalization", DEFAULT_APPLY_TEXT_NORMALIZATION ),
    }

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

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the options flow."""
        super().__init__()
        self._config_entry = config_entry

    @property
    def config_entry(self) -> ConfigEntry:
        """Return the config entry."""
        return self._config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage voice profiles."""
        if user_input is not None:
            if user_input.get("action") == "add_profile":
                return await self.async_step_add_profile()
            elif user_input.get("action") == "modify_profile":
                return await self.async_step_modify_profile()
            elif user_input.get("action") == "delete_profile":
                return await self.async_step_delete_profile()
            elif user_input.get("action") == "done":
                return self.async_create_entry(title="", data=self._config_entry.options)
        
        # Get current voice profiles
        current_profiles = self._config_entry.options.get("voice_profiles", {})
        profile_list = list(current_profiles.keys()) if current_profiles else ["No profiles configured"]
        
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional("action"): vol.In({
                    "add_profile": "Add New Voice Profile",
                    "modify_profile": "Modify Existing Profile", 
                    "delete_profile": "Delete Voice Profile",
                    "done": "Finish Configuration"
                })
            }),
            description_placeholders={
                "current_profiles": "\n".join(f"• {profile}" for profile in profile_list)
            }
        )

    async def async_step_add_profile(self, user_input: dict[str, Any] | None = None):
        """Add a new voice profile."""
        errors = {}
        
        if user_input is not None:
            profile_name = user_input[PROFILE_NAME_KEY]
            
            # Check if profile already exists
            current_profiles = self._config_entry.options.get("voice_profiles", {})
            if profile_name in current_profiles:
                errors["profile_name"] = "profile_exists"
            else:
                # Create new profile from form data
                new_profile = _map_form_data_to_profile(user_input)
                
                # Update options
                updated_profiles = current_profiles.copy()
                updated_profiles[profile_name] = new_profile
                
                new_options = self._config_entry.options.copy()
                new_options["voice_profiles"] = updated_profiles
                
                return self.async_create_entry(title="", data=new_options)
        
        return self.async_show_form(
            step_id="add_profile",
            data_schema=vol.Schema({
                vol.Required(PROFILE_NAME_KEY): str,
                vol.Required(VOICE_ID_KEY): str,
                vol.Optional(MODEL_KEY, default=DEFAULT_MODEL): vol.In([
                    "eleven_turbo_v2_5",
                    "eleven_multilingual_v2", 
                    "eleven_monolingual_v1",
                    "eleven_turbo_v2"
                ]),
                vol.Optional(STABILITY_KEY, default=DEFAULT_STABILITY): vol.All(
                    vol.Coerce(float), vol.Range(min=0, max=1)
                ),
                vol.Optional(SIMILARITY_KEY, default=DEFAULT_SIMILARITY_BOOST): vol.All(
                    vol.Coerce(float), vol.Range(min=0, max=1)
                ),
                vol.Optional(STYLE_KEY, default=DEFAULT_STYLE): vol.All(
                    vol.Coerce(float), vol.Range(min=0, max=1)
                ),
                vol.Optional(SPEED_KEY, default=DEFAULT_SPEED): vol.All(
                    vol.Coerce(float), vol.Range(min=0.25, max=4.0)
                ),
                vol.Optional(SPEAKER_BOOST_KEY, default=DEFAULT_USE_SPEAKER_BOOST): bool,
                vol.Optional(APPLY_TEXT_NORMALIZATION_KEY, default=DEFAULT_APPLY_TEXT_NORMALIZATION) : vol.In([
                    "on",
                    "off",
                    "auto"
                ]),
            }),
            errors=errors,
        )

    async def async_step_modify_profile(self, user_input: dict[str, Any] | None = None):
        """Modify an existing voice profile."""
        current_profiles = self._config_entry.options.get("voice_profiles", {})
        
        if not current_profiles:
            # No profiles to modify, go back to main menu
            return await self.async_step_init()
        
        if user_input is not None:
            if "selected_profile" in user_input:
                # Profile selected, now show editing form
                profile_name = user_input["selected_profile"]
                profile_data = current_profiles[profile_name]
                form_data = _map_profile_to_form_data(profile_name, profile_data)
                
                return self.async_show_form(
                    step_id="edit_profile",
                    data_schema=vol.Schema({
                        vol.Required(PROFILE_NAME_KEY, default=form_data[PROFILE_NAME_KEY]): str,
                        vol.Required(VOICE_ID_KEY, default=form_data[VOICE_ID_KEY]): str,
                        vol.Optional(MODEL_KEY, default=form_data[MODEL_KEY]): vol.In([
                            "eleven_turbo_v2_5",
                            "eleven_multilingual_v2", 
                            "eleven_monolingual_v1",
                            "eleven_turbo_v2"
                        ]),
                        vol.Optional(STABILITY_KEY, default=form_data[STABILITY_KEY]): vol.All(
                            vol.Coerce(float), vol.Range(min=0, max=1)
                        ),
                        vol.Optional(SIMILARITY_KEY, default=form_data[SIMILARITY_KEY]): vol.All(
                            vol.Coerce(float), vol.Range(min=0, max=1)
                        ),
                        vol.Optional(STYLE_KEY, default=form_data[STYLE_KEY]): vol.All(
                            vol.Coerce(float), vol.Range(min=0, max=1)
                        ),
                        vol.Optional(SPEED_KEY, default=form_data[SPEED_KEY]): vol.All(
                            vol.Coerce(float), vol.Range(min=0.25, max=4.0)
                        ),
                        vol.Optional(SPEAKER_BOOST_KEY, default=form_data[SPEAKER_BOOST_KEY]): bool,
                        vol.Optional(APPLY_TEXT_NORMALIZATION_KEY, default=form_data[APPLY_TEXT_NORMALIZATION_KEY]) : vol.In([
                            "on",
                            "off",
                            "auto"
                        ]),
                    })
                )
        
        return self.async_show_form(
            step_id="modify_profile",
            data_schema=vol.Schema({
                vol.Required("selected_profile"): vol.In(list(current_profiles.keys()))
            })
        )

    async def async_step_edit_profile(self, user_input: dict[str, Any] | None = None):
        """Edit the selected profile."""
        errors = {}
        
        if user_input is not None:
            old_profile_name = None
            current_profiles = self._config_entry.options.get("voice_profiles", {})
            
            # Find the original profile name by matching voice ID
            new_voice_id = user_input[VOICE_ID_KEY]
            for name, data in current_profiles.items():
                if data.get("voice") == new_voice_id:
                    old_profile_name = name
                    break
            
            new_profile_name = user_input[PROFILE_NAME_KEY]
            
            # Check if renaming and new name already exists
            if old_profile_name != new_profile_name and new_profile_name in current_profiles:
                errors["profile_name"] = "profile_exists"
            else:
                # Create updated profile from form data
                updated_profile = _map_form_data_to_profile(user_input)
                
                # Update options
                updated_profiles = current_profiles.copy()
                
                # Remove old profile if name changed
                if old_profile_name and old_profile_name != new_profile_name:
                    del updated_profiles[old_profile_name]
                    
                # Add/update profile with new name
                updated_profiles[new_profile_name] = updated_profile
                
                new_options = self._config_entry.options.copy()
                new_options["voice_profiles"] = updated_profiles
                
                return self.async_create_entry(title="", data=new_options)
        
        # If we get here, there were errors, show form again
        # We need to reconstruct the form with current values
        return await self.async_step_modify_profile()

    async def async_step_delete_profile(self, user_input: dict[str, Any] | None = None):
        """Delete a voice profile."""
        current_profiles = self._config_entry.options.get("voice_profiles", {})
        
        if not current_profiles:
            # No profiles to delete, go back to main menu
            return await self.async_step_init()
        
        if user_input is not None:
            profile_to_delete = user_input["profile_name"]
            
            # Remove profile
            updated_profiles = current_profiles.copy()
            if profile_to_delete in updated_profiles:
                del updated_profiles[profile_to_delete]
            
            new_options = self._config_entry.options.copy()
            new_options["voice_profiles"] = updated_profiles
            
            return self.async_create_entry(title="", data=new_options)
        
        return self.async_show_form(
            step_id="delete_profile",
            data_schema=vol.Schema({
                vol.Required("profile_name"): vol.In(list(current_profiles.keys()))
            })
        )