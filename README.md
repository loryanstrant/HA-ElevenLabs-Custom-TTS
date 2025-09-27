# HA-ElevenLabs-custom-TTS

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/loryanstrant/HA-ElevenLabs-Custom-TTS.svg)](https://github.com/loryanstrant/HA-ElevenLabs-Custom-TTS/releases/)

An ElevenLabs TTS integration for Home Assistant that allows for custom options to be passed in actions, not just the integration settings.

This custom component provides two main services:
1. **Get Voices** - Retrieve all available voices from ElevenLabs API
2. **Generate Voice** - Generate speech with full control over parameters

## ✨ New Features

### Enhanced Voice Discovery
- **Voice Type Filtering**: Filter voices by category (premade, cloned, generated, professional)
- **Voice Search**: Search voices by name, description, or labels (e.g., "british", "male", "authoritative")
- **Smart Voice Selection**: Use filters in automations to dynamically select the perfect voice

### Direct Media Player Integration
- **Instant Playback**: Send TTS audio directly to media player entities without file system
- **Multi-Room Audio**: Easily broadcast announcements to multiple speakers
- **Streamlined Workflow**: No need to manage temporary files or complex automation chains

### Backward Compatibility
- All existing automations continue to work unchanged
- File output and base64 encoding still fully supported
- Gradual migration path to new features

## Installation

### Via HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Go to "Integrations"
3. Click the three dots menu and select "Custom repositories"
4. Add `https://github.com/loryanstrant/HA-ElevenLabs-Custom-TTS` as repository
5. Set category to "Integration"
6. Click "Add"
7. Find "ElevenLabs Custom TTS" in the integration list and install it
8. Restart Home Assistant
9. Go to Configuration > Integrations
10. Click "Add Integration" and search for "ElevenLabs Custom TTS"
11. Enter your ElevenLabs API key

Or replace steps 1-6 with this:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=loryanstrant&repository=HA-ElevenLabs-Custom-TTS&category=integration)

### Manual Installation

1. Copy the `custom_components/elevenlabs_custom_tts` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Configuration > Integrations
4. Click "Add Integration" and search for "ElevenLabs Custom TTS"
5. Enter your ElevenLabs API key

## Usage

### Get Voices Service

Retrieves all available voices from your ElevenLabs account with optional filtering:

```yaml
# Get all voices
service: elevenlabs_custom_tts.get_voices

# Filter by voice type
service: elevenlabs_custom_tts.get_voices
data:
  voice_type: "premade"  # Options: premade, cloned, generated, professional

# Search for voices
service: elevenlabs_custom_tts.get_voices
data:
  search_text: "british"  # Search by name, description, or labels

# Combined filtering
service: elevenlabs_custom_tts.get_voices
data:
  voice_type: "premade"
  search_text: "male"
```

This returns a list of voices with their IDs, names, categories, and other metadata.

### Generate Voice Service

Generate speech with custom parameters:

```yaml
service: elevenlabs_custom_tts.generate_voice
data:
  text: "Hello, this is a test message."
  voice_id: "21m00Tcm4TlvDq8ikWAM"  # Required
  model_id: "eleven_multilingual_v2"  # Optional, default: eleven_multilingual_v2
  stability: 0.5  # Optional, default: 0.5 (0.0-1.0)
  similarity_boost: 0.75  # Optional, default: 0.75 (0.0-1.0)
  style: 0.0  # Optional, default: 0.0 (0.0-1.0)
  speed: 1.0  # Optional, default: 1.0 (0.25-4.0)
  use_speaker_boost: true  # Optional, default: true
  output_path: "/config/www/tts_output.mp3"  # Optional, saves to file if provided
```

#### NEW: Direct Media Player Output

Send audio directly to a media player entity without saving to file:

```yaml
service: elevenlabs_custom_tts.generate_voice
data:
  text: "Good morning! The weather today is sunny."
  voice_id: "21m00Tcm4TlvDq8ikWAM"
  media_player_entity: "media_player.living_room_speaker"
```

### Example Automation

#### Traditional File Output
```yaml
automation:
  - alias: "Generate Custom TTS"
    trigger:
      - platform: state
        entity_id: input_button.test_tts
    action:
      - service: elevenlabs_custom_tts.get_voices
        response_variable: voices_response
      - service: elevenlabs_custom_tts.generate_voice
        data:
          text: "Hello from Home Assistant!"
          voice_id: "{{ voices_response.voices[0].voice_id }}"
          stability: 0.7
          similarity_boost: 0.8
          style: 0.2
          use_speaker_boost: true
          output_path: "/config/www/custom_tts.mp3"
```

#### NEW: Smart Voice Selection with Media Player Output
```yaml
automation:
  - alias: "Smart Morning Announcement"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      # Get male voices for morning announcements
      - service: elevenlabs_custom_tts.get_voices
        data:
          voice_type: "premade"
          search_text: "male"
        response_variable: male_voices
      
      # Generate and play directly to speakers
      - service: elevenlabs_custom_tts.generate_voice
        data:
          text: "Good morning! Today is {{ now().strftime('%A, %B %d') }}. The weather is {{ states('weather.home') }}."
          voice_id: "{{ male_voices.voices[0].voice_id }}"
          stability: 0.6
          similarity_boost: 0.8
          media_player_entity: "media_player.all_speakers"
```

#### NEW: Dynamic Voice Search and Multi-Room Announcements
```yaml
automation:
  - alias: "Security Alert with Voice Selection"
    trigger:
      - platform: state
        entity_id: binary_sensor.front_door
        to: "on"
    action:
      # Find authoritative voices for security alerts
      - service: elevenlabs_custom_tts.get_voices
        data:
          search_text: "authoritative"
        response_variable: security_voices
        
      # Announce to all rooms simultaneously
      - service: elevenlabs_custom_tts.generate_voice
        data:
          text: "Security alert: Front door has been opened."
          voice_id: "{{ security_voices.voices[0].voice_id if security_voices.voices else '21m00Tcm4TlvDq8ikWAM' }}"
          stability: 0.9
          style: 0.3
          media_player_entity: "media_player.living_room_speaker"
      - service: elevenlabs_custom_tts.generate_voice
        data:
          text: "Security alert: Front door has been opened."
          voice_id: "{{ security_voices.voices[0].voice_id if security_voices.voices else '21m00Tcm4TlvDq8ikWAM' }}"
          stability: 0.9
          style: 0.3
          media_player_entity: "media_player.bedroom_speaker"

## Parameters

### Get Voices Parameters

- **voice_type** (optional): Filter voices by category
  - Options: "premade", "cloned", "generated", "professional"
- **search_text** (optional): Search for voices by name, description, or labels
  - Example: "british", "male", "authoritative"

### Generate Voice Parameters

- **text** (required): Text to convert to speech
- **voice_id** (required): ElevenLabs voice ID to use
- **model_id** (optional): ElevenLabs model ID (default: "eleven_multilingual_v2")
- **stability** (optional): Voice stability (0.0-1.0, default: 0.5)
- **similarity_boost** (optional): Similarity boost (0.0-1.0, default: 0.75)
- **style** (optional): Voice style (0.0-1.0, default: 0.0)
- **speed** (optional): Speech speed multiplier (0.25-4.0, default: 1.0)
- **use_speaker_boost** (optional): Enable speaker boost (default: true)
- **output_path** (optional): File path to save audio file
- **media_player_entity** (optional): Send audio directly to media player entity

### Response

The generate_voice service returns:
- **success**: Boolean indicating success
- **audio_size**: Size of generated audio in bytes
- **parameters**: Echo of the parameters used
- **output_path**: Path where file was saved (if provided)
- **media_player_entity**: Media player entity used (if provided)
- **audio_data**: Base64 encoded audio data (if no output_path or media_player_entity provided)
- **error**: Error message (if any issues occurred)

## Requirements

- Home Assistant 2023.1 or later
- ElevenLabs API key
- Internet connection for API calls


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Development Approach
<img width="256" height="256" alt="Vibe Coding with GitHub Copilot 256x256" src="https://github.com/user-attachments/assets/bb41d075-6b3e-4f2b-a88e-94b2022b5d4f" />


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues, please report them on the [GitHub Issues page](https://github.com/loryanstrant/HA-ElevenLabs-Custom-TTS/issues).
