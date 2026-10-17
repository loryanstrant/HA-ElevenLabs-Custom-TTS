"""Tests for config flow, migration and TTS generation."""

from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.elevenlabs_custom_tts import api_key_unique_id
from custom_components.elevenlabs_custom_tts.config_flow import MODEL_KEY
from custom_components.elevenlabs_custom_tts.const import DOMAIN

PROFILE = {
    "voice": "voice123",
    "model_id": "eleven_multilingual_v2",
    "stability": 0.3,
    "similarity_boost": 0.75,
    "style": 0.0,
    "speed": 1.1,
    "use_speaker_boost": True,
    "apply_text_normalization": "auto",
}


async def test_user_flow_hashes_unique_id(hass: HomeAssistant, mock_client) -> None:
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"api_key": "sk_secret"}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    assert entry.unique_id == api_key_unique_id("sk_secret")
    assert "sk_secret" not in entry.unique_id


async def test_migration_keeps_entity_id(hass: HomeAssistant, mock_client) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN, version=1, unique_id="sk_secret",
        data={"api_key": "sk_secret"}, options={"voice_profiles": {}},
    )
    entry.add_to_hass(hass)
    registry = er.async_get(hass)
    old = registry.async_get_or_create(
        "tts", DOMAIN, f"{DOMAIN}_tts", config_entry=entry, suggested_object_id="elevenlabs_custom_tts"
    )
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.version == 2
    assert entry.unique_id == api_key_unique_id("sk_secret")
    migrated = registry.async_get(old.entity_id)
    assert migrated.unique_id == f"{DOMAIN}_{entry.entry_id}"
    assert len(er.async_entries_for_config_entry(registry, entry.entry_id)) == 1


async def test_entity_friendly_name(hass: HomeAssistant, mock_client) -> None:
    await _setup(hass)
    state = hass.states.get("tts.elevenlabs_custom_tts")
    assert state is not None
    assert state.attributes["friendly_name"] == "ElevenLabs Custom TTS"


async def _setup(hass, profiles=None):
    entry = MockConfigEntry(
        domain=DOMAIN, version=2, unique_id="x",
        data={"api_key": "k"}, options={"voice_profiles": profiles or {}},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_tts_profile_omits_language_code_for_multilingual(hass, mock_client) -> None:
    await _setup(hass, {"Narrator": PROFILE})
    entity = hass.data["tts"].get_entity("tts.elevenlabs_custom_tts")
    audio = await entity.async_get_tts_audio("hello", "en", {"voice": "Narrator"})
    assert audio == ("mp3", b"abcdef")
    kwargs = mock_client.last_convert_kwargs
    assert kwargs["voice_id"] == "voice123"
    assert "language_code" not in kwargs


async def test_tts_sends_language_code_for_v3(hass, mock_client) -> None:
    await _setup(hass)
    entity = hass.data["tts"].get_entity("tts.elevenlabs_custom_tts")
    await entity.async_get_tts_audio("hello", "en", {"model_id": "eleven_v3"})
    assert mock_client.last_convert_kwargs["language_code"] == "en"


async def test_options_model_dropdown_and_rename(hass, mock_client) -> None:
    entry = await _setup(hass, {"Narrator": PROFILE, "Other": {**PROFILE, "voice": "voice123"}})

    # Model selector is populated from the API (TTS-capable only) plus the stored model
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"action": "modify_profile"})
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"selected_profile": "Narrator"})
    assert result["step_id"] == "edit_profile"
    selector = next(v for k, v in result["data_schema"].schema.items() if k == MODEL_KEY)
    options = selector.config["options"]
    assert "eleven_v3" in options and "eleven_english_sts_v2" not in options
    assert "eleven_multilingual_v2" in options

    # Rename + change voice ID; old code matched by voice ID and corrupted "Other"
    form = {k.schema: (k.default() if callable(k.default) else None) for k in result["data_schema"].schema}
    form.update({"Profile Name": "Storyteller", "Voice ID": "newvoice", MODEL_KEY: "eleven_v3"})
    result = await hass.config_entries.options.async_configure(result["flow_id"], form)
    assert result["type"] is FlowResultType.CREATE_ENTRY
    profiles = entry.options["voice_profiles"]
    assert set(profiles) == {"Storyteller", "Other"}
    assert profiles["Storyteller"]["voice"] == "newvoice"
    assert profiles["Storyteller"]["model_id"] == "eleven_v3"
