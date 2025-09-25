#!/usr/bin/env python3
"""
Test script to run podcast generation locally and debug the API 500 error.
"""

import sys
import os
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Set working directory to project root
os.chdir(project_root)

def main():
    print("🔍 AI-Parrot Local Debug Test")
    print("=" * 50)
    
    # Check environment
    print("📁 Working directory:", os.getcwd())
    print("🐍 Python path:", sys.path[:3])
    
    # Check .env file
    env_file = project_root / ".env"
    if env_file.exists():
        print("✅ .env file found")
    else:
        print("❌ .env file not found")
        return
    
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
            print("\n❌ ANTHROPIC_API_KEY is missing or invalid!")
            print("💡 This is likely the cause of the 401 authentication errors.")
            print("📝 Please check your .env file and ensure you have a valid Anthropic API key.")
            return
        
    except Exception as e:
        print(f"❌ Error loading environment: {e}")
        return
    
    # Test podcast generation
    try:
        print("\n🎙️ Testing podcast generation...")
        from podcast_generator.langgraph_workflow import run_podcast_workflow
        
        # Run with minimal parameters
        import asyncio
        
        async def test_generation():
            try:
                result = await run_podcast_workflow(
                    language="en",
                    voice_name="Aria"
                )
                print("✅ Podcast generation successful!")
                return result
            except Exception as e:
                print(f"❌ Podcast generation failed: {e}")
                print(f"🔍 Error type: {type(e).__name__}")
                import traceback
                traceback.print_exc()
                return None
        
        # Run the test
        result = asyncio.run(test_generation())
        
        if result:
            print("🎉 Local generation works! The issue is likely in the API layer.")
        else:
            print("💥 Local generation also fails. Check the error details above.")
            
    except Exception as e:
        print(f"❌ Error importing or running podcast generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
