#!/usr/bin/env python3
"""Utility script to list available ElevenLabs voices."""
from elevenlabs.client import ElevenLabs

def list_voices():
    """List all available voices with their details."""
    client = ElevenLabs()
    voices = client.voices.get_all()
    
    print("\nAvailable Voices:")
    print("-" * 80)
    
    for i, voice in enumerate(voices.voices, 1):
        print(f"{i}. {voice.name}")
        print(f"   ID: {voice.voice_id}")
        print(f"   Labels: {voice.labels}")
        print(f"   Preview: https://api.elevenlabs.io/v1/voices/{voice.voice_id}/preview")
        print("-" * 80)

if __name__ == "__main__":
    list_voices()
