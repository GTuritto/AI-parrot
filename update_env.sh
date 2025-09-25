#!/bin/bash
# Script to update .env file with API keys

echo "🔧 Updating .env file with API keys..."

# Create .env file with all API keys
cat > .env << 'EOF'
# AI-Parrot Podcast Generator Environment Configuration
# Required API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Optional API Keys
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
MISTRAL_API_KEY=your_mistral_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
NEWS_API_KEY=your_news_api_key_here

# MCP Server Configuration
MCP_SERVER_URL=http://localhost:3002/mcp
MCP_SERVER_NAME=local-mcp-server
MCP_SSE_URL=http://localhost:3002/sse

# Logging Configuration
LOG_LEVEL=INFO
EOF

echo "✅ .env file updated successfully!"
echo "🔑 API Keys configured:"
echo "   ✅ Anthropic Claude"
echo "   ✅ OpenAI GPT"
echo "   ✅ Google Gemini"
echo "   ✅ Mistral"
echo "   ✅ OpenRouter"
echo "   ✅ ElevenLabs TTS"
echo "   ✅ Tavily Search"
echo ""
echo "🚀 Ready to test podcast generation!"
