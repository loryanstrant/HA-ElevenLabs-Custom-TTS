"""Constants for the ElevenLabs Custom TTS integration."""

DOMAIN = "elevenlabs_custom_tts"

# Configuration constants
CONF_API_KEY = "api_key"

# Service names
SERVICE_GET_VOICES = "get_voices"
SERVICE_GENERATE_VOICE = "generate_voice"

# Service parameters
ATTR_TEXT = "text"
ATTR_MODEL_ID = "model_id"
ATTR_VOICE_ID = "voice_id"
ATTR_VOICE = "voice"
ATTR_PROFILE_NAME = "profile_name"
ATTR_STABILITY = "stability"
ATTR_USE_SPEAKER_BOOST = "use_speaker_boost"
ATTR_SIMILARITY_BOOST = "similarity_boost"
ATTR_STYLE = "style"
ATTR_SPEED = "speed"
ATTR_OUTPUT_PATH = "output_path"
ATTR_APPLY_TEXT_NORMALIZATION = "apply_text_normalization"

# Voice filtering parameters
ATTR_VOICE_TYPE = "voice_type"
ATTR_SEARCH_TEXT = "search_text"

# Media player parameters
ATTR_MEDIA_PLAYER_ENTITY = "media_player_entity"

# Defaults
DEFAULT_MODEL = "eleven_multilingual_v2"
DEFAULT_STABILITY = 0.5
DEFAULT_SIMILARITY_BOOST = 0.75
DEFAULT_STYLE = 0.0
DEFAULT_SPEED = 1.0
DEFAULT_USE_SPEAKER_BOOST = True
DEFAULT_APPLY_TEXT_NORMALIZATION = "auto"

# Fallback model list, used only when the ElevenLabs /v1/models endpoint
# can't be reached. The options flow also accepts any custom model ID typed in.
FALLBACK_MODELS = [
    "eleven_v3",
    "eleven_multilingual_v2",
    "eleven_flash_v2_5",
    "eleven_flash_v2",
]

# Models that reject the language_code parameter
MODELS_WITHOUT_LANGUAGE_CODE = {
    "eleven_multilingual_v2",
    "eleven_multilingual_v1",
    "eleven_monolingual_v1",
}

# Per-request timeout for audio generation (seconds)
TTS_TIMEOUT = 60
