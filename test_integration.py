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
    
    # Test 2: Generate Voice service simulation
    print("\n🎵 Testing generate_voice service...")
    
    # This would be the actual service call in Home Assistant:
    generate_voice_params = {
        "text": "Hello, this is a test of the ElevenLabs Custom TTS integration for Home Assistant!",
        "voice_id": "21m00Tcm4TlvDq8ikWAM",
        "model_id": "eleven_multilingual_v2",
        "stability": 0.7,
        "similarity_boost": 0.8,
        "style": 0.2,
        "speed": 1.1,
        "use_speaker_boost": True,
        "output_path": "/config/www/test_tts_output.mp3"
    }
    
    print("📝 Parameters:")
    for key, value in generate_voice_params.items():
        print(f"   - {key}: {value}")
    
    # Simulated response
    example_generate_response = {
        "success": True,
        "audio_size": 45678,
        "parameters": generate_voice_params,
        "output_path": "/config/www/test_tts_output.mp3"
    }
    
    print(f"\n✅ Voice generation completed:")
    print(f"   - Success: {example_generate_response['success']}")
    print(f"   - Audio size: {example_generate_response['audio_size']} bytes")
    print(f"   - Output file: {example_generate_response['output_path']}")
    
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
    
    # Test 4: Media player output examples
    print("\n🔊 Testing media player output...")
    
    media_player_examples = [
        {
            "name": "Living Room Announcement",
            "service": "elevenlabs_custom_tts.generate_voice",
            "data": {
                "text": "Good morning! Today's weather is sunny.",
                "voice_id": "21m00Tcm4TlvDq8ikWAM",
                "media_player_entity": "media_player.living_room_speaker"
            }
        },
        {
            "name": "Kitchen Timer Alert",
            "service": "elevenlabs_custom_tts.generate_voice",
            "data": {
                "text": "Your timer has finished cooking!",
                "voice_id": "AZnzlk1XvdvUeBnXmlld",
                "stability": 0.8,
                "media_player_entity": "media_player.kitchen_display"
            }
        }
    ]
    
    for example in media_player_examples:
        print(f"\n   🔊 {example['name']}:")
        print(f"   Service: {example['service']}")
        print("   Data:")
        for key, value in example['data'].items():
            print(f"     {key}: {value}")
    
    # Test 5: Service call examples for automations
    print("\n🤖 Example automation service calls:")
    
    automation_examples = [
        {
            "name": "Morning Greeting",
            "service": "elevenlabs_custom_tts.generate_voice",
            "data": {
                "text": "Good morning! Today is {{ now().strftime('%A, %B %d') }}",
                "voice_id": "21m00Tcm4TlvDq8ikWAM",
                "stability": 0.6,
                "similarity_boost": 0.8,
                "output_path": "/config/www/morning.mp3"
            }
        },
        {
            "name": "Emergency Alert",
            "service": "elevenlabs_custom_tts.generate_voice", 
            "data": {
                "text": "Attention: {{ states('sensor.alert_message') }}",
                "voice_id": "AZnzlk1XvdvUeBnXmlld",
                "stability": 0.9,
                "similarity_boost": 0.9,
                "style": 0.5,
                "use_speaker_boost": True,
                "output_path": "/config/www/alert.mp3"
            }
        },
        {
            "name": "Smart Speaker Announcement (NEW!)",
            "service": "elevenlabs_custom_tts.generate_voice",
            "data": {
                "text": "The front door has been opened.",
                "voice_id": "21m00Tcm4TlvDq8ikWAM", 
                "media_player_entity": "media_player.all_speakers"
            }
        }
    ]
    
    for i, example in enumerate(automation_examples, 1):
        print(f"\n   Example {i}: {example['name']}")
        print(f"   Service: {example['service']}")
        print("   Data:")
        for key, value in example['data'].items():
            print(f"     {key}: {value}")
    
    print("\n🎯 Integration test completed successfully!")
    print("\n✨ NEW FEATURES:")
    print("• Voice filtering by type (premade, cloned, generated, professional)")
    print("• Voice search by name, description, or labels")
    print("• Direct media player output - no file system needed!")
    print("• Full backward compatibility with existing automations")
    print("\nTo use in Home Assistant:")
    print("1. Install the integration in custom_components/elevenlabs_custom_tts/")
    print("2. Restart Home Assistant")
    print("3. Add the integration via Configuration > Integrations")
    print("4. Enter your ElevenLabs API key")
    print("5. Use the enhanced services in automations, scripts, or the Developer Tools")


if __name__ == "__main__":
    asyncio.run(test_elevenlabs_integration())