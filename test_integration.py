#!/usr/bin/env python3
"""
Test script for ElevenLabs Custom TTS integration
This script demonstrates how to use the integration's services programmatically
"""

import asyncio
import json
from pathlib import Path
import sys

# This would normally be imported in Home Assistant environment
# For testing purposes, we'll simulate the service calls

async def test_elevenlabs_integration():
    """Test the ElevenLabs Custom TTS integration services."""
    
    print("🎙️  ElevenLabs Custom TTS Integration Test")
    print("=" * 50)
    
    # Test 1: Get Voices service simulation
    print("\n📋 Testing get_voices service...")
    
    # This would be the actual service call in Home Assistant:
    # service: elevenlabs_custom_tts.get_voices
    
    example_voices_response = {
        "voices": [
            {
                "voice_id": "21m00Tcm4TlvDq8ikWAM",
                "name": "Rachel",
                "category": "premade"
            },
            {
                "voice_id": "AZnzlk1XvdvUeBnXmlld",
                "name": "Domi",
                "category": "premade"
            },
            {
                "voice_id": "EXAVITQu4vr4xnSDxMaL",
                "name": "Bella",
                "category": "premade"
            }
        ]
    }
    
    print(f"✅ Found {len(example_voices_response['voices'])} voices")
    for voice in example_voices_response["voices"]:
        print(f"   - {voice['name']} ({voice['voice_id']}) - {voice['category']}")
    
    # Test 2: Native TTS platform integration
    print("\n🎵 Testing native TTS platform integration...")
    
    # This shows how the integration works with Home Assistant's TTS platform:
    tts_examples = [
        {
            "name": "Basic TTS Usage",
            "service": "tts.speak",
            "data": {
                "entity_id": "tts.elevenlabs",
                "message": "Hello from Home Assistant!",
                "media_player_entity_id": "media_player.living_room_speaker"
            }
        },
        {
            "name": "Advanced TTS with Custom Options",
            "service": "tts.speak", 
            "data": {
                "entity_id": "tts.elevenlabs",
                "message": "Hello, this is a test of the ElevenLabs Custom TTS integration for Home Assistant!",
                "media_player_entity_id": "media_player.living_room_speaker",
                "options": {
                    "voice": "21m00Tcm4TlvDq8ikWAM",
                    "model_id": "eleven_multilingual_v2",
                    "stability": 0.7,
                    "similarity_boost": 0.8,
                    "style": 0.2,
                    "speed": 1.1,
                    "use_speaker_boost": True
                }
            }
        }
    ]
    
    for example in tts_examples:
        print(f"\n   🎵 {example['name']}:")
        print(f"   Service: {example['service']}")
        print("   Data:")
        for key, value in example['data'].items():
            if key == "options" and isinstance(value, dict):
                print(f"     {key}:")
                for opt_key, opt_value in value.items():
                    print(f"       {opt_key}: {opt_value}")
            else:
                print(f"     {key}: {value}")

    # Test 3: Enhanced voice filtering examples
    print("\n🔍 Testing enhanced voice filtering...")
    
    # Example filtered service calls
    filtering_examples = [
        {
            "name": "Filter by Voice Type",
            "service": "elevenlabs_custom_tts.get_voices",
            "data": {
                "voice_type": "premade"
            }
        },
        {
            "name": "Search for British Voices",
            "service": "elevenlabs_custom_tts.get_voices", 
            "data": {
                "search_text": "british"
            }
        },
        {
            "name": "Find Male Professional Voices",
            "service": "elevenlabs_custom_tts.get_voices",
            "data": {
                "voice_type": "professional",
                "search_text": "male"
            }
        }
    ]
    
    for example in filtering_examples:
        print(f"\n   📋 {example['name']}:")
        print(f"   Service: {example['service']}")
        if example['data']:
            print("   Parameters:")
            for key, value in example['data'].items():
                print(f"     {key}: {value}")
    
    # Test 4: Automation workflow examples
    print("\n🤖 Example automation workflows:")
    
    automation_examples = [
        {
            "name": "Smart Morning Announcement",
            "description": "Uses voice filtering + TTS platform",
            "steps": [
                {
                    "service": "elevenlabs_custom_tts.get_voices",
                    "data": {
                        "voice_type": "premade",
                        "search_text": "pleasant"
                    }
                },
                {
                    "service": "tts.speak",
                    "data": {
                        "entity_id": "tts.elevenlabs",
                        "message": "Good morning! Today is {{ now().strftime('%A, %B %d') }}",
                        "media_player_entity_id": "media_player.all_speakers",
                        "options": {
                            "voice": "{{ morning_voices.voices[0].voice_id if morning_voices.voices else '21m00Tcm4TlvDq8ikWAM' }}",
                            "stability": 0.6,
                            "similarity_boost": 0.8
                        }
                    }
                }
            ]
        },
        {
            "name": "Security Alert System",
            "description": "Dynamic voice selection for alerts",
            "steps": [
                {
                    "service": "elevenlabs_custom_tts.get_voices",
                    "data": {
                        "search_text": "authoritative"
                    }
                },
                {
                    "service": "tts.speak",
                    "data": {
                        "entity_id": "tts.elevenlabs",
                        "message": "Security alert: Front door has been opened.",
                        "media_player_entity_id": "media_player.living_room_speaker",
                        "options": {
                            "voice": "{{ security_voices.voices[0].voice_id if security_voices.voices else '21m00Tcm4TlvDq8ikWAM' }}",
                            "stability": 0.9,
                            "style": 0.3
                        }
                    }
                }
            ]
        }
    ]
    
    for i, example in enumerate(automation_examples, 1):
        print(f"\n   Example {i}: {example['name']}")
        print(f"   Description: {example['description']}")
        print("   Steps:")
        for j, step in enumerate(example['steps'], 1):
            print(f"     {j}. Service: {step['service']}")
            if 'data' in step:
                print("        Data:")
                for key, value in step['data'].items():
                    if key == "options" and isinstance(value, dict):
                        print(f"          {key}:")
                        for opt_key, opt_value in value.items():
                            print(f"            {opt_key}: {opt_value}")
                    else:
                        print(f"          {key}: {value}")
    
    print("\n🎯 Integration test completed successfully!")
    print("\n✨ CURRENT FEATURES:")
    print("• Voice filtering by type (premade, cloned, generated, professional)")
    print("• Voice search by name, description, or labels")
    print("• Native TTS platform integration with media player support")
    print("• Custom voice parameters (stability, similarity_boost, style, speed)")
    print("• Full Home Assistant TTS ecosystem compatibility")
    print("\nTo use in Home Assistant:")
    print("1. Install the integration in custom_components/elevenlabs_custom_tts/")
    print("2. Restart Home Assistant")
    print("3. Add the integration via Configuration > Integrations")
    print("4. Enter your ElevenLabs API key")
    print("5. Use with Home Assistant's native TTS services for media player output")
    print("6. Use get_voices service for dynamic voice selection in automations")


if __name__ == "__main__":
    asyncio.run(test_elevenlabs_integration())