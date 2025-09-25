#!/bin/bash

# AI-Parrot Enterprise API Launcher
echo "🤖 AI-Parrot Enterprise System - API Server"
echo "============================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    cp .env.template .env
    echo -e "${RED}❌ Please edit .env file with your API keys before running the API${NC}"
    exit 1
fi

# Check if API dependencies are installed
echo -e "${GREEN}📦 Checking API dependencies...${NC}"
if ! python3 -c "import fastapi, uvicorn" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Installing API dependencies...${NC}"
    pip3 install -r requirements-api.txt
fi

# Set Python path
export PYTHONPATH="./src:./api:$PYTHONPATH"

# Show configuration
echo -e "\n${GREEN}=== API Configuration ===${NC}"
echo -e "Host: ${YELLOW}0.0.0.0${NC}"
echo -e "Port: ${YELLOW}8000${NC}"
echo -e "Docs: ${YELLOW}http://localhost:8000/docs${NC}"
echo -e "API:  ${YELLOW}http://localhost:8000${NC}"

echo -e "\n${GREEN}Enterprise AI Agent Patterns:${NC}"
echo -e "🤝 A2A Collaborative Assessment"
echo -e "🏛️ Agent Supervisor Coordination"
echo -e "🔗 MCP Integration with SSE Transport"
echo -e "🔄 Circuit Breaker Resilience"
echo -e "👁️ Observer Pattern Monitoring"

# Start the API server
echo -e "\n${GREEN}🚀 Starting AI-Parrot Enterprise API...${NC}"
echo -e "Press ${YELLOW}Ctrl+C${NC} to stop the server"
echo ""

uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
