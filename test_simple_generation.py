#!/usr/bin/env python3
"""
Simple test script that bypasses article fetching and tests podcast generation directly.
"""

import sys
import os
from pathlib import Path
import asyncio

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Set working directory to project root
os.chdir(project_root)

def main():
    print("🎙️ AI-Parrot Simple Generation Test")
    print("=" * 50)
    
    # Load environment
    try:
        from utils.env import load_env_vars, validate_api_keys
        print("📦 Loading environment variables...")
        load_env_vars()
        
        # Check API keys
        api_status = validate_api_keys()
        print("🔑 API Keys status:")
        for key, status in api_status.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {key}: {'Available' if status else 'Missing'}")
        
        if not api_status.get("anthropic", False):
            print("\n❌ ANTHROPIC_API_KEY is missing!")
            return
        
        if not api_status.get("elevenlabs", False):
            print("\n❌ ELEVENLABS_API_KEY is missing!")
            return
        
    except Exception as e:
        print(f"❌ Error loading environment: {e}")
        return
    
    # Test with sample articles
    try:
        print("\n🎙️ Testing podcast generation with sample content...")
        
        # Import required modules
        from podcast_generator.content_processor import ContentProcessor
        from podcast_generator.audio_generator import AudioGenerator
        
        async def test_simple_generation():
            try:
                # Create sample articles
                sample_articles = [
                    {
                        "title": "AI Breakthrough in Language Models",
                        "content": "Researchers have announced a significant breakthrough in large language models, improving their ability to understand context and generate more accurate responses. This development could revolutionize how we interact with AI systems.",
                        "url": "https://example.com/ai-breakthrough",
                        "published_date": "2025-09-25"
                    },
                    {
                        "title": "New Framework for AI Agent Coordination",
                        "content": "A new framework for coordinating multiple AI agents has been developed, allowing for better collaboration and task distribution. The framework includes supervisor patterns and agent-to-agent communication protocols.",
                        "url": "https://example.com/ai-agents",
                        "published_date": "2025-09-25"
                    }
                ]
                
                print(f"📰 Using {len(sample_articles)} sample articles")
                
                # Process content
                print("🔄 Processing content...")
                processor = ContentProcessor()
                
                # Generate podcast script
                script = await processor.generate_podcast_script(
                    articles=sample_articles,
                    language="en"
                )
                
                if script:
                    print("✅ Podcast script generated successfully!")
                    print(f"📝 Script length: {len(script)} characters")
                    
                    # Test audio generation
                    print("🎵 Testing audio generation...")
                    audio_gen = AudioGenerator()
                    
                    # Generate a short test audio
                    test_text = "Welcome to AI Parrot, your AI-powered tech podcast."
                    audio_path = await audio_gen.text_to_speech(
                        text=test_text,
                        voice="Aria",
                        output_path="PodcastOutput/test_audio.mp3"
                    )
                    
                    if audio_path and Path(audio_path).exists():
                        print("✅ Audio generation successful!")
                        print(f"🎵 Audio file: {audio_path}")
                        print(f"📊 File size: {Path(audio_path).stat().st_size} bytes")
                        return True
                    else:
                        print("❌ Audio generation failed")
                        return False
                else:
                    print("❌ Script generation failed")
                    return False
                    
            except Exception as e:
                print(f"❌ Generation failed: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        # Run the test
        success = asyncio.run(test_simple_generation())
        
        if success:
            print("\n🎉 Simple generation test PASSED!")
            print("💡 The core podcast generation works. The issue is with article fetching.")
            print("🔧 You can now use the Streamlit interface to generate podcasts.")
        else:
            print("\n💥 Simple generation test FAILED.")
            print("🔍 Check the error details above.")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
