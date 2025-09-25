#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR" || exit 1

echo -e "${GREEN}=== AI Podcast Generator ===${NC}"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating one...${NC}"
    uv venv || { echo -e "${RED}Failed to create virtual environment${NC}"; exit 1; }
    
    echo -e "${GREEN}Installing dependencies...${NC}"
    source .venv/bin/activate
    uv pip install -e . || { echo -e "${RED}Failed to install dependencies${NC}"; exit 1; }
else
    # Activate the virtual environment
    source .venv/bin/activate || { echo -e "${RED}Failed to activate virtual environment${NC}"; exit 1; }
fi

# Add the src directory to the Python path
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

# Check for required API keys
if [ -z "$ANTHROPIC_API_KEY" ] && [ -f ".env" ]; then
    # Try to load from .env file if not set
    export $(grep -v '^#' .env | xargs)
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${YELLOW}Warning: ANTHROPIC_API_KEY not found. Some features may not work.${NC}"
fi

# Parse command line arguments
LANGUAGE="es"  # Default to Spanish
VOICE="Sarah"   # Default voice (optimized for Spanish)

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -l|--language)
            LANGUAGE="$2"
            shift # past argument
            shift # past value
            ;;
        -v|--voice)
            VOICE="$2"
            shift # past argument
            shift # past value
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -l, --language LANGUAGE  Set the podcast language (en/es). Default: en"
            echo "  -v, --voice VOICE       Set the voice for the podcast. Default: Aria"
            echo "  -h, --help             Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown parameter: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Validate language
if [[ "$LANGUAGE" != "en" && "$LANGUAGE" != "es" ]]; then
    echo -e "${RED}Error: Invalid language. Use 'en' for English or 'es' for Spanish.${NC}"
    exit 1
fi

# Show configuration
echo -e "\n${GREEN}=== AI-Parrot Configuration ===${NC}"
echo -e "Language: ${YELLOW}${LANGUAGE}${NC}"
echo -e "Voice:    ${YELLOW}${VOICE}${NC}"
echo -e "\n${GREEN}Enterprise AI Agent Patterns:${NC}"
echo -e "🤝 A2A Collaborative Assessment"
echo -e "🏛️ Agent Supervisor Coordination"
echo -e "🔗 MCP Integration with SSE Transport"
echo -e "🔄 Circuit Breaker Resilience"
echo -e "👁️ Observer Pattern Monitoring"

# Run the podcast generator
echo -e "\n${GREEN}🚀 Starting AI-Parrot Enterprise System...${NC}"

# Run the podcast generator with full AI Agent Patterns (A2A + Supervisor always enabled)
python -m podcast_generator.main --language "$LANGUAGE" --voice "$VOICE"
EXIT_CODE=$?

# Check the exit status and display appropriate message
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "\n${GREEN}✓ Podcast generated successfully!${NC}"
    echo -e "Check the 'PodcastOutput' directory for the generated files."
    
    # List the generated files
    if [ -d "PodcastOutput" ]; then
        echo -e "\n${GREEN}Generated files:${NC}"
        ls -l PodcastOutput/*
    fi
else
    echo -e "\n${RED}✗ Podcast generation failed with exit code $EXIT_CODE${NC}"
    
    # Provide troubleshooting tips for common issues
    if [ $EXIT_CODE -eq 1 ]; then
        echo -e "\n${YELLOW}Possible issues:${NC}"
        
        if [ -z "$ANTHROPIC_API_KEY" ]; then
            echo "- Missing ANTHROPIC_API_KEY in environment variables"
        fi
        
        if [ "$LANGUAGE" = "es" ] && [ -z "$OPENAI_API_KEY" ]; then
            echo "- Spanish translation requires OPENAI_API_KEY to be set"
        fi
        
        if [ -z "$ELEVENLABS_API_KEY" ]; then
            echo "- Audio generation requires ELEVENLABS_API_KEY to be set"
        fi
        
        echo -e "\nCheck the error message above for more details."
    fi
    
    exit $EXIT_CODE
fi
