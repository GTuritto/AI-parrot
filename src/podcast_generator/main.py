"""Main script to run the podcast generator workflow."""
import asyncio
import os
import sys
import argparse
from pathlib import Path

# Add the project root to the Python path to enable imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from podcast_generator.langgraph_workflow import run_podcast_workflow, run_podcast_workflow_with_patterns
from utils.env import validate_api_keys, load_env_vars


async def main(
    language: str = 'en', 
    voice: str = 'Aria'
):
    """Run the AI-Parrot podcast generator with full AI Agent Patterns.
    
    The system is built with enterprise-grade AI Agent Patterns as core architecture:
    - A2A Collaborative Assessment
    - Agent Supervisor Coordination
    - MCP Integration with SSE Transport
    - Circuit Breaker Resilience
    - Observer Pattern Monitoring
    
    Args:
        language: Language code ('en' for English, 'es' for Spanish).
        voice: Voice to use for the podcast.
    """
    print("🤖 AI-Parrot Podcast Generator")
    print("Built with Enterprise AI Agent Patterns")
    print("=" * 45)
    print(f"Language: {'Spanish' if language == 'es' else 'English'}")
    print(f"Voice: {voice}")
    print("=" * 45)
    
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
    
    print("Starting AI Agent workflow...")
    try:
        # Run the AI-Parrot system with full enterprise patterns
        result = await run_podcast_workflow_with_patterns(
            language=language, 
            voice_name=voice, 
            enable_a2a=True,
            use_supervisor=True,
            use_resilience=True
        )
        
        if result.get("success"):
            print(f"\n🎉 Podcast generated successfully!")
            print(f"   🎵 Audio: {result.get('audio_path')}")
            print(f"   📰 Articles: {result.get('articles_processed')}")
            print(f"   ✅ Tasks: {result.get('tasks_completed', 'N/A')}")
            print(f"   🤝 A2A Score: {result.get('a2a_quality_score', 'N/A')}")
            
            if 'system_status' in result:
                print(f"   💚 Health: {result['system_status'].get('system_health')}")
                print(f"   🤖 Agents: {result['system_status'].get('active_agents', 'N/A')}")
        else:
            print(f"\n❌ Generation failed: {result.get('error')}")
    except Exception as e:
        print(f"\n✗ An error occurred during podcast generation: {e}")
        if "ELEVEN" in str(e):
            print("Please make sure you have set the ELEVENLABS_API_KEY environment variable.")
        if "voice" in str(e).lower():
            print("Please check that the specified voice is available in your ElevenLabs account.")
        raise


if __name__ == "__main__":
    # Set up argument parser - only language and voice options
    parser = argparse.ArgumentParser(
        description='AI-Parrot Podcast Generator with Enterprise AI Agent Patterns'
    )
    parser.add_argument('-l', '--language', type=str, default='en',
                      choices=['en', 'es'],
                      help='Language for the podcast (en/es)')
    parser.add_argument('-v', '--voice', type=str, default='Aria',
                      help='Voice to use for the podcast')
    
    # Parse command line arguments
    args = parser.parse_args()
    
    # Run the main function
    asyncio.run(main(
        language=args.language, 
        voice=args.voice
    ))
