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
ATTR_STABILITY = "stability"
ATTR_USE_SPEAKER_BOOST = "use_speaker_boost"
ATTR_SIMILARITY_BOOST = "similarity_boost"
ATTR_STYLE = "style"
ATTR_SPEED = "speed"
ATTR_OUTPUT_PATH = "output_path"

# Defaults
DEFAULT_MODEL = "eleven_multilingual_v2"
DEFAULT_STABILITY = 0.5
DEFAULT_SIMILARITY_BOOST = 0.75
DEFAULT_STYLE = 0.0
DEFAULT_SPEED = 1.0
DEFAULT_USE_SPEAKER_BOOST = True