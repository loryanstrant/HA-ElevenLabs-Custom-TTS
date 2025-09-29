# HA-ElevenLabs-custom-TTS

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/loryanstrant/HA-ElevenLabs-Custom-TTS.svg)](https://github.com/loryanstrant/HA-ElevenLabs-Custom-TTS/releases/)

An ElevenLabs TTS integration for Home Assistant that provides enhanced voice discovery and integrates with Home Assistant's native TTS platform.

This custom component provides:
1. **Get Voices Service** - Retrieve and filter available voices from ElevenLabs API  
2. **Native TTS Platform** - Full integration with Home Assistant's TTS system with custom voice parameters
3. **Voice Profile Management** - Create, modify, and delete named voice profiles through the Home Assistant UI

## ✨ Features

> **📝 Note:** The default TTS entity ID is `tts.elevenlabs_custom_tts`. This is used in all the examples below.

### Enhanced Voice Discovery
- **Voice Type Filtering**: Filter voices by category (premade, cloned, generated, professional)
- **Voice Search**: Search voices by name, description, or labels (e.g., "british", "male", "authoritative")
- **Smart Voice Selection**: Use filters in automations to dynamically select the perfect voice

### Native TTS Platform Integration
- **Seamless Integration**: Works with Home Assistant's native TTS services (`tts.speak`, `tts.cloud_say`, etc.)
- **Custom Voice Parameters**: Full control over stability, similarity_boost, style, speed, and speaker_boost
- **Media Player Support**: Use with any Home Assistant media player through the TTS platform
- **Multi-Language Support**: Supports multiple languages through ElevenLabs' multilingual models

### Voice Profile Management
- **Create Named Profiles**: Save your favorite voice configurations with custom names
- **Easy Profile Management**: Add, modify, or delete voice profiles through the Home Assistant UI
- **Quick Profile Selection**: Use saved profiles with the `voice_profile` option in TTS calls
- **Profile Storage**: Profiles are stored in Home Assistant configuration and persist across restarts

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

## 🎭 Voice Profile Management

After installation, you can create and manage voice profiles through the Home Assistant UI. Voice profiles allow you to save your favorite voice configurations with custom names for easy reuse.

### Accessing Voice Profile Settings

1. Go to **Settings** → **Devices & Services** → **Integrations**
2. Find your **ElevenLabs Custom TTS** integration
3. Click **Configure** (or the gear icon)
4. You'll see the Voice Profile Management interface

<img width="1555" height="879" alt="Voice Profile Management interface in Home Assistant" src="https://github.com/user-attachments/assets/316fce70-0322-41c3-98e3-4badb423e7de" />


### Managing Voice Profiles

#### Adding a New Voice Profile

1. In the Voice Profile Management interface, select **"Add New Voice Profile"**
2. Fill out the profile details:
   - **Profile Name**: A descriptive name for your profile (e.g., "Morgan Freeman Style")
   - **Voice ID**: The ElevenLabs voice ID to use
   - **Model**: Choose the ElevenLabs model (default: "eleven_multilingual_v2")
   - **Voice Stability**: Control voice consistency (0.0-1.0, default: 0.5)
   - **Similarity Boost**: Enhance voice similarity (0.0-1.0, default: 0.75)
   - **Style Exaggeration**: Control voice style intensity (0.0-1.0, default: 0.0)
   - **Speech Speed**: Speech rate multiplier (0.25-4.0, default: 1.0)
   - **Enable Speaker Boost**: Enhance speaker clarity (default: true)
3. Click **Submit** to save the profile

<img width="1282" height="1184" alt="image" src="https://github.com/user-attachments/assets/6c9d8f81-7062-4abb-970e-7a850013cb8a" />



#### Modifying an Existing Profile

1. Select **"Modify Existing Profile"** 
2. Choose the profile you want to edit from the dropdown
3. Update any settings you want to change
4. Click **Submit** to save changes

<img width="1250" height="741" alt="Modify Voice Profile interface showing editable settings" src="https://github.com/user-attachments/assets/ba26b3b7-a753-445e-a491-1525d52e7b79" />


#### Deleting a Profile

1. Select **"Delete Voice Profile"**
2. Choose the profile to delete from the dropdown
3. Confirm the deletion


### Using Voice Profiles

Once you've created voice profiles, you can use them in your TTS calls:

```yaml
service: tts.speak
data:
  entity_id: tts.elevenlabs_custom_tts  # Note: Default entity ID
  message: "This message uses my custom voice profile!"
  media_player_entity_id: media_player.living_room_speaker
  options:
    voice_profile: "Morgan Freeman Style"  # Use your saved profile
```

<img width="1771" height="1233" alt="image" src="https://github.com/user-attachments/assets/624e6595-e8d4-4c2e-bf18-af6a38d14bcb" />


You can also combine voice profiles with custom options (custom options override profile settings):

```yaml
service: tts.speak
data:
  entity_id: tts.elevenlabs_custom_tts
  message: "This uses the profile but with faster speed."
  media_player_entity_id: media_player.living_room_speaker
  options:
    voice_profile: "Morgan Freeman Style"
    speed: 1.5  # This overrides the profile's speed setting
```

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
  entity_id: tts.elevenlabs_custom_tts  # Default entity ID
  message: "Hello from Home Assistant!"
  media_player_entity_id: media_player.living_room_speaker
```

#### Advanced TTS with Custom Voice Parameters
```yaml
service: tts.speak  
data:
  entity_id: tts.elevenlabs_custom_tts
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

#### Using Voice Profiles
```yaml
service: tts.speak  
data:
  entity_id: tts.elevenlabs_custom_tts
  message: "This announcement uses my custom voice profile."
  media_player_entity_id: media_player.living_room_speaker
  options:
    voice_profile: "News Anchor"  # Use your saved voice profile
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
          entity_id: tts.elevenlabs_custom_tts
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
          entity_id: tts.elevenlabs_custom_tts
          message: "Security alert: Front door has been opened."
          media_player_entity_id: media_player.living_room_speaker
          options:
            voice: "{{ security_voices.voices[0].voice_id if security_voices.voices else '21m00Tcm4TlvDq8ikWAM' }}"
            stability: 0.9
            style: 0.3
            
      # Also announce to bedroom
      - service: tts.speak
        data:
          entity_id: tts.elevenlabs_custom_tts
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
          entity_id: tts.elevenlabs_custom_tts
          message: "Hello from Home Assistant!"
          media_player_entity_id: media_player.living_room_speaker
          options:
            voice: "21m00Tcm4TlvDq8ikWAM"
            stability: 0.7
            similarity_boost: 0.8
```

#### Using Voice Profiles in Automations
```yaml
automation:
  - alias: "Morning Announcement with Voice Profile"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: tts.speak
        data:
          entity_id: tts.elevenlabs_custom_tts
          message: "Good morning! Today's weather is {{ states('weather.home') }}."
          media_player_entity_id: media_player.bedroom_speaker
          options:
            voice_profile: "Morning Announcer"  # Use saved voice profile
            
  - alias: "Bedtime Story with Custom Profile"
    trigger:
      - platform: time
        at: "20:00:00"
    action:
      - service: tts.speak
        data:
          entity_id: tts.elevenlabs_custom_tts
          message: "Once upon a time, in a land far away..."
          media_player_entity_id: media_player.kids_room_speaker
          options:
            voice_profile: "Storyteller"
            speed: 0.9  # Override profile speed for bedtime
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

- **voice_profile** (optional): Use a saved voice profile by name (overrides individual settings)
- **voice** (optional): ElevenLabs voice ID to use (default: "21m00Tcm4TlvDq8ikWAM")
- **model_id** (optional): ElevenLabs model ID (default: "eleven_multilingual_v2") 
- **stability** (optional): Voice stability (0.0-1.0, default: 0.5)
- **similarity_boost** (optional): Similarity boost (0.0-1.0, default: 0.75)
- **style** (optional): Voice style (0.0-1.0, default: 0.0)
- **speed** (optional): Speech speed multiplier (0.25-4.0, default: 1.0)
- **use_speaker_boost** (optional): Enable speaker boost (default: true)

**Note:** When using `voice_profile`, the profile settings are applied first, then any additional options override specific profile settings.

## 🚨 Troubleshooting

### Entity ID Not Found
- **Default Entity ID**: `tts.elevenlabs_custom_tts`
- **Check Entity Registry**: Go to Settings → Devices & Services → Entities and search for "elevenlabs"
- **Alternative Entity Names**: The entity might appear as `tts.elevenlabs` in some configurations

### Voice Profiles Not Working
- Ensure you're using the correct `voice_profile` name (case-sensitive)
- Check that the profile exists in Settings → Integrations → ElevenLabs Custom TTS → Configure
- Verify the voice profile contains valid ElevenLabs voice IDs

### API Errors
- Verify your ElevenLabs API key is correct and has sufficient quota
- Check Home Assistant logs for detailed error messages
- Ensure your internet connection is stable

### Integration Not Loading
- Restart Home Assistant after installation
- Check that the `custom_components` directory structure is correct:
  ```
  custom_components/
  └── elevenlabs_custom_tts/
      ├── __init__.py
      ├── manifest.json
      ├── config_flow.py
      ├── tts.py
      ├── const.py
      ├── strings.json
      └── services.yaml
  ```

## 📝 Changelog

### Version 0.5.7
- **Improved logging**: Fixed debug logging levels for cleaner logs
- **Code quality**: Addressed GitHub code quality recommendations

### Version 0.5.6
- **Voice Profile Management**: Complete UI for creating, modifying, and deleting voice profiles
- **Enhanced Configuration**: User-friendly field labels and descriptions in config flow
- **Service Cleanup**: Removed redundant `save_voice_profile` service
- **Better Error Handling**: Improved error messages and validation

### Version 0.5.x and earlier
- Native TTS platform integration
- Voice filtering and search capabilities
- Enhanced voice discovery features
- Multi-language support

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
