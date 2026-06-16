<p align="center">
  <img src="assets/ai-parrot-logo.png" alt="AI-Parrot logo" width="320" />
</p>

# 🤖 AI-Parrot Podcast Generator

**Enterprise AI Agent System for Intelligent Podcast Generation**

🏗️ **Core Architecture**: Built with enterprise-grade AI Agent Patterns as the fundamental system design. This isn't just a podcast generator - it's a comprehensive demonstration of production-ready multi-agent coordination.

🤖 **Built-in Enterprise Patterns**:
- 🤝 **A2A Collaborative Assessment** - Agents collaborate on quality scoring
- 🏛️ **Agent Supervisor Coordination** - Hierarchical task orchestration
- 🔗 **MCP Integration with SSE Transport** - Dynamic content sourcing
- 🔄 **Circuit Breaker Resilience** - Fault tolerance and graceful degradation
- 👁️ **Observer Pattern Monitoring** - Real-time system observability

## ✨ Features
| Task | Model | Purpose |
|------|-------|---------|
| Article Ranking | Claude Haiku | Fast and cost-effective relevance scoring |
| Article Summarization | Claude Sonnet | Balanced speed and quality |
| Script Generation | Claude Opus | High-quality creative content |
| Script Refinement | GPT-4 (or Claude Sonnet) | Precise TTS optimization |

## 🌟 Features

- **Automated Article Fetching**: Fetches the latest articles from RSS feeds
- **AI-Powered Summarization**: Uses Claude AI to process and summarize content
- **Natural-Sounding Narration**: Converts text to speech using ElevenLabs' high-quality voices
- **Multi-language Support**: Generate podcasts in English or Spanish
- **Customizable Voices**: Choose from multiple high-quality voices
- **Customizable Output**: Control voice, number of articles, and output format
- **LangGraph Workflow**: Robust pipeline for podcast generation

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- [UV](https://github.com/astral-sh/uv) for virtual environment and dependency management
- API keys for required services (see below)
- (Optional) `ffmpeg` for audio processing (installed by default on most systems)

### Required API Keys

#### 🔑 Required
- `ANTHROPIC_API_KEY` - For Claude AI models (Sonnet, Haiku, Opus)

#### 📝 Optional but Recommended
- `OPENAI_API_KEY` - For GPT-4 script refinement (falls back to Claude Sonnet if not available)
- `ELEVENLABS_API_KEY` - For high-quality text-to-speech (required for audio output)
- `NEWS_API_KEY` - For News API integration (falls back to RSS feeds if not available)

Add these to your `.env` file in the project root.

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd AI-parrot
   ```

2. Set up the environment (automatic with the script):
   ```bash
   # Make the script executable
   chmod +x run_podcast.sh
   
   # Run the script (it will set up the environment if needed)
   ./run_podcast.sh --help
   ```

### Using the Script (Recommended)

```bash
# Make the script executable (only needed once)
chmod +x run_podcast.sh

# Generate English podcast with default voice
./run_podcast.sh --language en --voice "Aria"

# Generate Spanish podcast
./run_podcast.sh --language es --voice "Sarah"

# Show help
./run_podcast.sh --help
```

### Manual Execution

```bash
# Activate the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Generate podcast with enterprise AI patterns
python -m podcast_generator.main --language en --voice "Aria"

# Spanish podcast
python -m podcast_generator.main --language es --voice "Sarah"
```

### 🌐 Unified Web Interface

The system provides both FastAPI and Streamlit in a single container:

```bash
# Run unified service with Docker (Recommended)
docker-compose up --build

# Or run locally
./run_api.sh      # API only
./run_ui.sh       # Streamlit only

# Access the unified system
# - Streamlit UI: http://localhost:8501 (Interactive Interface)
# - FastAPI: http://localhost:8000/api (REST API)
# - Interactive Docs: http://localhost:8000/api/docs
# - System Info: http://localhost:8000/info
# - Health Check: http://localhost:8000/api/health
```

**API Usage:**
```bash
# Generate podcast via API
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{"language": "en", "voice": "Aria"}'

# Check system status
curl -X GET "http://localhost:8000/api/status"
```

## 📚 Documentation

### **English Documentation**

For detailed documentation, please refer to the following files:

- [EDUCATIONAL_GUIDE.md](EDUCATIONAL_GUIDE.md): Comprehensive learning path for AI Agent Patterns
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md): Complete API reference and examples
- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md): System architecture and capabilities
- [CODE_WALKTHROUGH.md](CODE_WALKTHROUGH.md): In-depth code documentation
- [LEARNING_OUTCOMES.md](LEARNING_OUTCOMES.md): Skills assessment and career readiness

### **Documentación en Español**

Para documentación detallada en español, consulta los siguientes archivos:

- [README_ES.md](README_ES.md): Guía completa del sistema en español
- [GUIA_EDUCATIVA_ES.md](GUIA_EDUCATIVA_ES.md): Ruta de aprendizaje integral para Patrones de Agentes IA
- [DOCUMENTACION_API_ES.md](DOCUMENTACION_API_ES.md): Referencia completa de API y ejemplos
- [RESUMEN_SISTEMA_ES.md](RESUMEN_SISTEMA_ES.md): Arquitectura del sistema y capacidades

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required
ANTHROPIC_API_KEY=your_anthropic_key_here

# Optional but recommended
OPENAI_API_KEY=your_openai_key_here  # Required for Spanish translation
ELEVENLABS_API_KEY=your_elevenlabs_key_here  # Required for audio generation
NEWS_API_KEY=your_newsapi_key_here  # Falls back to RSS feeds if not available

# MCP Server Configuration (Optional)
MCP_SERVER_URL=http://localhost:3002/mcp
MCP_SSE_URL=http://localhost:3002/sse
MCP_SERVER_NAME=local-mcp-server
```

### 🔗 MCP Integration

The system supports **Model Context Protocol (MCP)** for dynamic content sourcing with intelligent fallback to RSS feeds.

**MCP Server**: For enhanced article fetching, you can use our companion RSS MCP Server:

- **Repository**: [RSS-MCPserver](https://github.com/GTuritto/RSS-MCPserver)
- **Purpose**: Provides dynamic RSS content via MCP protocol with SSE transport
- **Features**: Real-time content sourcing, intelligent caching, multi-feed aggregation
- **Fallback**: System automatically falls back to direct RSS feeds if MCP server is unavailable

The MCP integration demonstrates enterprise-grade content sourcing patterns with resilient fallback mechanisms.

**Quick MCP Setup:**
```bash
# Clone and run the MCP server
git clone https://github.com/GTuritto/RSS-MCPserver
cd RSS-MCPserver
npm install && npm start

# The AI-Parrot system will automatically detect and use the MCP server
```

### Language and Voice Options

The podcast generator supports multiple languages and voices:

#### Languages
- `en` - English (default)
- `es` - Spanish

#### Recommended Voices
- **English**: Aria (default), Sarah, Lily
- **Spanish**: Aria, Sarah, Lily (optimized for Spanish)

To specify a language and voice when running the script:

```bash
# English with default voice (Aria)
./run_podcast.sh

# Spanish with default voice
./run_podcast.sh --language es

# Specify a different voice
./run_podcast.sh --language es --voice "Sarah"
```

### Script Usage

```bash
# Show help
./run_podcast.sh --help

# Generate podcast with custom options
./run_podcast.sh --language es --voice "Lily"
NEWS_API_KEY=your_news_api_key
OUTPUT_DIR=./PodcastOutput
```

## 🎙️ Usage

### Basic Usage

```bash
poetry run python run_podcast.py
```

### Advanced Options

```bash
poetry run python run_podcast.py \
    --num-articles 5 \
    --output-dir ./my_podcasts \
    --voice "Aria" \
    --topic "AI and Technology"
```

## 📂 Output Files

The application generates the following files in the `PodcastOutput` directory:

- `AIpodcast_YYYYMMDD_narrative.txt`: The generated podcast script
- `AIpodcast_YYYYMMDD.mp3`: The audio file of the podcast (if ElevenLabs API key is provided)
- `podcast_articles_YYYYMMDD.csv`: CSV file containing the processed articles

## 🔍 Troubleshooting

### Common Issues

1. **Permission Denied** when running the script:
   ```bash
   chmod +x run_podcast.sh
   ```

2. **Missing Dependencies**:
   The script will automatically install required dependencies.

3. **API Key Errors**:
   Make sure your API keys are correctly set in the `.env` file or environment variables.

4. **Audio Generation Fails**:
   - Check your ElevenLabs API key
   - Ensure you have enough credits in your ElevenLabs account
   - Verify your internet connection

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

## 📄 License

This project is licensed under the [MIT License](LICENSE).

## Project Structure

```text
AI-parrot/
├── .venv/                      # Virtual environment
├── pyproject.toml              # Project configuration
├── README.md                   # This file
├── .env                        # Environment variables (API keys)
└── src/                        # Source code
    ├── __init__.py             # Package initialization
    ├── utils/                  # Utility modules
    │   ├── __init__.py         # Package initialization
    │   └── env.py              # Environment utilities
    └── podcast_generator/      # Podcast generator system
        ├── __init__.py         # Package initialization
        ├── article_fetcher.py  # Article fetching utilities
        ├── ai_processor.py     # AI processing modules
        ├── file_utils.py       # File handling utilities
        ├── langgraph_workflow.py # LangGraph workflow
        └── main.py             # Main script
```

## Podcast Generator System

The podcast generator system uses LangGraph to orchestrate a workflow that:

1. Fetches recent AI-related articles from various sources
2. Ranks articles by relevance to AI topics
3. Summarizes the most relevant articles using Mistral AI
4. Generates a podcast script with natural transitions between stories
5. Converts the script to an audio file using text-to-speech
6. Saves all outputs (text, audio, and article data)

The system is built with extensibility in mind, making it easy to add new article sources or customize the generation process.
