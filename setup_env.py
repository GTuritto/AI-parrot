#!/usr/bin/env python3
"""Helper script to create .env file with required API keys."""
import os
from pathlib import Path

def main():
    env_path = Path(".env")
    
    if env_path.exists():
        print(".env file already exists. Please edit it manually if needed.")
        return
    
    print("Setting up .env file for Mujica Podcast Generator")
    print("-" * 50)
    
    # Get required API keys from user
    mistral_key = input("Enter your Mistral API key (required): ").strip()
    
    # Ask for optional keys
    openai_key = input("Enter your OpenAI API key (optional, press Enter to skip): ").strip()
    anthropic_key = input("Enter your Anthropic API key (optional, press Enter to skip): ").strip()
    news_api_key = input("Enter your News API key (optional, press Enter to skip): ").strip()
    
    # Create .env content
    env_content = [
        "# Required API Keys for the Podcast Generator",
        f"MISTRAL_API_KEY={mistral_key}",
        "",
        "# Optional API Keys (uncomment if you want to use these services)",
    ]
    
    if openai_key:
        env_content.append(f"OPENAI_API_KEY={openai_key}")
    else:
        env_content.append("# OPENAI_API_KEY=your_openai_api_key_here")
    
    if anthropic_key:
        env_content.append(f"ANTHROPIC_API_KEY={anthropic_key}")
    else:
        env_content.append("# ANTHROPIC_API_KEY=your_anthropic_api_key_here")
    
    if news_api_key:
        env_content.append(f"NEWS_API_KEY={news_api_key}")
    else:
        env_content.append("# NEWS_API_KEY=your_news_api_key_here")
    
    # Write to .env file
    with open(env_path, 'w') as f:
        f.write("\n".join(env_content) + "\n")
    
    print("\n.env file has been created successfully!")
    print("You can now run the podcast generator with: python -m podcast_generator.main")

if __name__ == "__main__":
    main()
