# HA-ElevenLabs-custom-TTS

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/loryanstrant/HA-ElevenLabs-Custom-TTS.svg)](https://github.com/loryanstrant/HA-ElevenLabs-Custom-TTS/releases/)

An ElevenLabs TTS integration for Home Assistant that provides enhanced voice discovery and integrates with Home Assistant's native TTS platform.

This custom component provides:
1. **Get Voices Service** - Retrieve and filter available voices from ElevenLabs API  
2. **Native TTS Platform** - Full integration with Home Assistant's TTS system with custom voice parameters

## ✨ Features

### Enhanced Voice Discovery
- **Voice Type Filtering**: Filter voices by category (premade, cloned, generated, professional)
- **Voice Search**: Search voices by name, description, or labels (e.g., "british", "male", "authoritative")
- **Smart Voice Selection**: Use filters in automations to dynamically select the perfect voice

### Native TTS Platform Integration
- **Seamless Integration**: Works with Home Assistant's native TTS services (`tts.speak`, `tts.cloud_say`, etc.)
- **Custom Voice Parameters**: Full control over stability, similarity_boost, style, speed, and speaker_boost
- **Media Player Support**: Use with any Home Assistant media player through the TTS platform
- **Multi-Language Support**: Supports multiple languages through ElevenLabs' multilingual models

### Backward Compatibility
- Works with existing Home Assistant TTS automations and scripts
- Gradual migration path from other TTS providers

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

### Native TTS Integration

Use with Home Assistant's native TTS services for direct media player output:

#### Basic TTS Usage
```yaml
service: tts.speak
data:
  entity_id: tts.elevenlabs  # Entity name may vary based on your setup
  message: "Hello from Home Assistant!"
  media_player_entity_id: media_player.living_room_speaker
```

#### Advanced TTS with Custom Voice Parameters
```yaml
service: tts.speak  
data:
  entity_id: tts.elevenlabs
  message: "Good morning! The weather today is sunny."
  media_player_entity_id: media_player.living_room_speaker
  options:
    voice: "21m00Tcm4TlvDq8ikWAM"  # ElevenLabs voice ID
    stability: 0.7
    similarity_boost: 0.8
    style: 0.2
    speed: 1.0
    use_speaker_boost: true
```

### Example Automations

#### Smart Voice Selection with TTS
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
      
      # Generate and play directly to speakers using native TTS
      - service: tts.speak
        data:
          entity_id: tts.elevenlabs
          message: "Good morning! Today is {{ now().strftime('%A, %B %d') }}. The weather is {{ states('weather.home') }}."
          media_player_entity_id: media_player.all_speakers
          options:
            voice: "{{ male_voices.voices[0].voice_id if male_voices.voices else '21m00Tcm4TlvDq8ikWAM' }}"
            stability: 0.6
            similarity_boost: 0.8
```

#### Dynamic Voice Search for Security Alerts
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
        
      # Announce to living room
      - service: tts.speak
        data:
          entity_id: tts.elevenlabs
          message: "Security alert: Front door has been opened."
          media_player_entity_id: media_player.living_room_speaker
          options:
            voice: "{{ security_voices.voices[0].voice_id if security_voices.voices else '21m00Tcm4TlvDq8ikWAM' }}"
            stability: 0.9
            style: 0.3
            
      # Also announce to bedroom
      - service: tts.speak
        data:
          entity_id: tts.elevenlabs
          message: "Security alert: Front door has been opened."
          media_player_entity_id: media_player.bedroom_speaker
          options:
            voice: "{{ security_voices.voices[0].voice_id if security_voices.voices else '21m00Tcm4TlvDq8ikWAM' }}"
            stability: 0.9
            style: 0.3
```

#### Simple TTS Usage
```yaml
automation:
  - alias: "Simple TTS Test"
    trigger:
      - platform: state
        entity_id: input_button.test_tts
    action:
      - service: tts.speak
        data:
          entity_id: tts.elevenlabs
          message: "Hello from Home Assistant!"
          media_player_entity_id: media_player.living_room_speaker
          options:
            voice: "21m00Tcm4TlvDq8ikWAM"
            stability: 0.7
            similarity_boost: 0.8
```

## Parameters

### Get Voices Service Parameters

- **voice_type** (optional): Filter voices by category
  - Options: "premade", "cloned", "generated", "professional"
- **search_text** (optional): Search for voices by name, description, or labels  
  - Example: "british", "male", "authoritative"

**Returns:** List of voices with voice_id, name, category, description, and labels

### TTS Platform Options

When using Home Assistant's native TTS services, you can pass these options:

- **voice** (optional): ElevenLabs voice ID to use (default: "21m00Tcm4TlvDq8ikWAM")
- **model_id** (optional): ElevenLabs model ID (default: "eleven_multilingual_v2") 
- **stability** (optional): Voice stability (0.0-1.0, default: 0.5)
- **similarity_boost** (optional): Similarity boost (0.0-1.0, default: 0.75)
- **style** (optional): Voice style (0.0-1.0, default: 0.0)
- **speed** (optional): Speech speed multiplier (0.25-4.0, default: 1.0)
- **use_speaker_boost** (optional): Enable speaker boost (default: true)

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
