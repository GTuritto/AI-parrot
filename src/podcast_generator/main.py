"""Main script to run the podcast generator workflow."""
import asyncio
import os
import sys
import argparse
from pathlib import Path

# Add the project root to the Python path to enable imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from podcast_generator.langgraph_workflow import run_podcast_workflow
from utils.env import validate_api_keys, load_env_vars


async def main(language: str = 'en', voice: str = 'Aria'):
    """Run the podcast generator workflow.
    
    Args:
        language: Language code ('en' for English, 'es' for Spanish).
        voice: Voice to use for the podcast.
    """
    print("AI Podcast Generator")
    print("-------------------")
    print(f"Language: {'Spanish' if language == 'es' else 'English'}")
    print(f"Voice: {voice}")
    print("-------------------")
    
    # Load environment variables
    env_loaded = load_env_vars()
    if not env_loaded:
        print("Error: Could not load .env file. Please make sure it exists in the project root.")
        return
    
    # Print current working directory and .env path for debugging
    print(f"Current working directory: {os.getcwd()}")
    print(f"Loading .env from: {os.path.abspath('.env')}")
    
    # Validate API keys
    api_key_status = validate_api_keys()
    
    # Check for required API keys
    required_keys = ["ANTHROPIC_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        print("\nError: The following required API keys are missing from your .env file:")
        for key in missing_keys:
            print(f"- {key}")
        print("\nPlease add the missing API keys and try again.")
        return
    
    # Check for optional API keys
    optional_keys = {
        "OPENAI_API_KEY": "GPT-4 will be used for script refinement if available, otherwise Claude Sonnet will be used",
        "NEWS_API_KEY": "Using RSS feeds only (no News API functionality)"
    }
    
    print("\nAPI Key Status:")
    print(f"- Anthropic API: {'✅ Available' if os.getenv('ANTHROPIC_API_KEY') else '❌ Missing (Required)'}")
    print(f"- OpenAI API: {'✅ Available' if os.getenv('OPENAI_API_KEY') else '⚠️  Missing (Optional)'}")
    print(f"- News API: {'✅ Available' if os.getenv('NEWS_API_KEY') else '⚠️  Missing (Optional, using RSS feeds only)'}")
    
    # News API is optional since we're using RSS feeds
    if not api_key_status.get("news_api", False):
        print("\nInfo: NEWS_API_KEY not found. Using RSS feeds only.")
    
    print("Starting podcast generation workflow...")
    try:
        # Run the podcast workflow
        await run_podcast_workflow(language=language, voice_name=voice)
        print("\n✓ Podcast generation completed successfully!")
    except Exception as e:
        print(f"\n✗ An error occurred during podcast generation: {e}")
        if "ELEVEN_API_KEY" in str(e):
            print("Please make sure you have set the ELEVEN_API_KEY environment variable.")
        if "voice" in str(e).lower():
            print("Please check that the specified voice is available in your ElevenLabs account.")
        raise


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Generate an AI podcast.')
    parser.add_argument('-l', '--language', type=str, default='en',
                      choices=['en', 'es'],
                      help='Language for the podcast (en/es)')
    parser.add_argument('-v', '--voice', type=str, default='Aria',
                      help='Voice to use for the podcast')
    
    # Parse command line arguments
    args = parser.parse_args()
    
    # Run the main function with the parsed arguments
    asyncio.run(main(language=args.language, voice=args.voice))
