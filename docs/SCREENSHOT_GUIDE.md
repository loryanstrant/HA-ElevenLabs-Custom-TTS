# Screenshot Guide for ElevenLabs Custom TTS Documentation

This guide outlines the screenshots needed for the comprehensive README documentation.

## Required Screenshots

### 1. Integration Settings Page (`voice-profile-management.png`)
**Location:** Settings → Devices & Services → Integrations → ElevenLabs Custom TTS → Configure
**Description:** Main voice profile management interface showing the available actions
**Content Should Show:**
- Current voice profiles list
- Action buttons: "Add New Voice Profile", "Modify Existing Profile", "Delete Voice Profile", "Finish Configuration"

### 2. Add Voice Profile Form (`add-voice-profile.png`)
**Location:** Voice Profile Management → Add New Voice Profile
**Description:** Form for creating a new voice profile
**Content Should Show:**
- Profile Name field
- Voice ID field
- Model dropdown (showing available models)
- Voice Stability slider/field
- Similarity Boost slider/field
- Style Exaggeration slider/field
- Speech Speed slider/field
- Enable Speaker Boost checkbox
- Submit button

### 3. Modify Voice Profile Interface (`modify-voice-profile.png`)
**Location:** Voice Profile Management → Modify Existing Profile
**Description:** Interface for selecting and editing existing profiles
**Content Should Show:**
- Dropdown with existing voice profiles
- Selected profile showing edit form with current values
- All the same fields as add form but populated with existing data

### 4. Delete Voice Profile Interface (`delete-voice-profile.png`)
**Location:** Voice Profile Management → Delete Voice Profile
**Description:** Interface for deleting voice profiles
**Content Should Show:**
- Dropdown with existing voice profiles to delete
- Warning/confirmation message
- Delete/Submit button

### 5. Entity Usage Example (`entity-usage-example.png`)
**Location:** Developer Tools → Services
**Description:** Example of using the TTS service with voice profiles
**Content Should Show:**
- Service: `tts.speak`
- Service data showing:
  ```yaml
  entity_id: tts.elevenlabs_custom_tts
  message: "Hello from Home Assistant!"
  media_player_entity_id: media_player.living_room_speaker
  options:
    voice_profile: "Morgan Freeman Style"
  ```

## Screenshot Guidelines

1. **Resolution:** Capture at high resolution (at least 1920x1080)
2. **Browser:** Use Chrome or Edge for consistent UI rendering
3. **Theme:** Use Home Assistant's default light theme for consistency
4. **Cropping:** Crop screenshots to show only relevant UI elements
5. **Privacy:** Ensure no personal information (API keys, personal voice names) is visible
6. **File Format:** Save as PNG for best quality
7. **File Size:** Optimize for web (under 500KB each if possible)

## Mock Data for Screenshots

Use these example profiles for screenshots:
- **"News Anchor"**: Professional, stable voice settings
- **"Storyteller"**: Expressive settings with higher style values
- **"Morning Announcer"**: Pleasant, clear voice for daily announcements

## Implementation Notes

- Screenshots are commented out in the README with `<!-- TODO: ... -->`
- Once screenshots are taken, uncomment and update the image paths
- Consider adding alt text for accessibility
- Screenshots should be stored in `docs/images/` directory

## Testing the Screenshots

After taking screenshots:
1. Add them to the repository
2. Update the README to uncomment the image references
3. Test that images render correctly in GitHub
4. Verify images are accessible and informative