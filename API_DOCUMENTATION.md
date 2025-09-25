# 🌐 AI-Parrot Enterprise API Documentation

## 🚀 **Quick Start**

### **Docker Deployment (Recommended)**

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd AI-parrot
   cp .env.template .env
   # Edit .env with your API keys
   ```

2. **Build and Run**
   ```bash
   docker-compose up --build
   ```

3. **Access the API**
   - API: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### **Local Development**

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-api.txt

# Run the API server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## 📋 **API Endpoints**

### **🏠 Root Endpoint**
```http
GET /
```
Returns system information and available endpoints.

**Response:**
```json
{
  "name": "AI-Parrot Enterprise Podcast Generator",
  "version": "1.0.0",
  "description": "Enterprise AI Agent System for Intelligent Podcast Generation",
  "enterprise_patterns": "A2A + Supervisor + MCP + Circuit Breaker + Observer",
  "docs": "/docs",
  "health": "/health"
}
```

### **💚 Health Check**
```http
GET /health
```
Returns system health status and API key validation.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-25T06:51:40",
  "version": "1.0.0",
  "enterprise_patterns": {
    "a2a_collaborative_assessment": true,
    "agent_supervisor_coordination": true,
    "mcp_integration_sse_transport": true,
    "circuit_breaker_resilience": true,
    "observer_pattern_monitoring": true
  },
  "api_keys": {
    "anthropic": true,
    "openai": true,
    "elevenlabs": true,
    "news_api": false
  }
}
```

### **🎙️ Generate Podcast**
```http
POST /generate
```
Generates a podcast using the enterprise AI agent system.

**Request Body:**
```json
{
  "language": "en",
  "voice": "Aria"
}
```

**Parameters:**
- `language` (string): "en" for English, "es" for Spanish
- `voice` (string): ElevenLabs voice name (e.g., "Aria", "Sarah", "Lily")

**Response:**
```json
{
  "success": true,
  "message": "Podcast generated successfully with enterprise AI agent patterns",
  "audio_path": "PodcastOutput/podcast_20250925_065140.mp3",
  "articles_processed": 15,
  "tasks_completed": 4,
  "a2a_quality_score": 0.92,
  "system_status": {
    "system_health": "healthy",
    "active_agents": 4
  },
  "generation_time": 45.3
}
```

### **📁 List Files**
```http
GET /files
```
Lists all generated podcast files.

**Response:**
```json
{
  "files": [
    {
      "name": "podcast_20250925_065140.mp3",
      "size": 2457600,
      "created": "2025-09-25T06:51:40",
      "modified": "2025-09-25T06:52:25",
      "download_url": "/download/podcast_20250925_065140.mp3"
    }
  ]
}
```

### **📥 Download File**
```http
GET /download/{filename}
```
Downloads a generated podcast file.

**Parameters:**
- `filename` (string): Name of the file to download

**Response:** Binary file download

### **📊 System Status**
```http
GET /status
```
Returns detailed system status and metrics.

**Response:**
```json
{
  "system": "AI-Parrot Enterprise System",
  "status": "operational",
  "enterprise_patterns": {
    "a2a_collaborative_assessment": "active",
    "agent_supervisor_coordination": "active",
    "mcp_integration_sse_transport": "active",
    "circuit_breaker_resilience": "active",
    "observer_pattern_monitoring": "active"
  },
  "api_keys": {
    "anthropic": "✅ Available",
    "openai": "✅ Available",
    "elevenlabs": "✅ Available",
    "news_api": "⚠️ Optional"
  },
  "statistics": {
    "podcasts_generated": 5,
    "supported_languages": ["en", "es"],
    "supported_voices": ["Aria", "Sarah", "Lily", "Custom"]
  },
  "timestamp": "2025-09-25T06:51:40"
}
```

## 🔧 **Usage Examples**

### **cURL Examples**

```bash
# Health check
curl -X GET "http://localhost:8000/health"

# Generate English podcast
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"language": "en", "voice": "Aria"}'

# Generate Spanish podcast
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"language": "es", "voice": "Sarah"}'

# List generated files
curl -X GET "http://localhost:8000/files"

# Download a podcast
curl -X GET "http://localhost:8000/download/podcast_20250925_065140.mp3" \
  --output podcast.mp3
```

### **Python Client Example**

```python
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def generate_podcast(language="en", voice="Aria"):
    """Generate a podcast using the API."""
    response = requests.post(
        f"{BASE_URL}/generate",
        json={"language": language, "voice": voice}
    )
    return response.json()

def download_podcast(filename, output_path):
    """Download a generated podcast."""
    response = requests.get(f"{BASE_URL}/download/{filename}")
    with open(output_path, 'wb') as f:
        f.write(response.content)

# Usage
result = generate_podcast("en", "Aria")
if result["success"]:
    print(f"Podcast generated: {result['audio_path']}")
    print(f"A2A Quality Score: {result['a2a_quality_score']}")
```

### **JavaScript/Node.js Example**

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';

async function generatePodcast(language = 'en', voice = 'Aria') {
  try {
    const response = await axios.post(`${BASE_URL}/generate`, {
      language,
      voice
    });
    return response.data;
  } catch (error) {
    console.error('Error generating podcast:', error.response?.data);
    throw error;
  }
}

// Usage
generatePodcast('en', 'Aria')
  .then(result => {
    console.log('Podcast generated:', result.audio_path);
    console.log('A2A Quality Score:', result.a2a_quality_score);
  })
  .catch(console.error);
```

## 🐳 **Docker Configuration**

### **Environment Variables**

```env
# Required API Keys
ANTHROPIC_API_KEY=your_anthropic_key_here
ELEVEN_API_KEY=your_elevenlabs_key_here

# Optional API Keys
OPENAI_API_KEY=your_openai_key_here
NEWS_API_KEY=your_news_api_key_here

# MCP Server Configuration
MCP_SERVER_URL=http://localhost:3002/mcp
MCP_SSE_URL=http://localhost:3002/sse
MCP_SERVER_NAME=local-mcp-server

# Logging
LOG_LEVEL=INFO
```

### **Docker Commands**

```bash
# Build the image
docker build -t ai-parrot-enterprise .

# Run the container
docker run -p 8000:8000 --env-file .env ai-parrot-enterprise

# Run with docker-compose
docker-compose up --build

# View logs
docker-compose logs -f ai-parrot

# Stop the service
docker-compose down
```

## 🔒 **Security Considerations**

1. **API Keys**: Never commit API keys to version control
2. **Environment**: Use `.env` files or environment variables
3. **Network**: Consider running behind a reverse proxy (nginx)
4. **Authentication**: Add API authentication for production use
5. **Rate Limiting**: Implement rate limiting for production deployments

## 📈 **Monitoring**

The API provides several monitoring endpoints:

- `/health` - Basic health check
- `/status` - Detailed system status
- Container health checks via Docker

## 🚀 **Production Deployment**

For production deployment, consider:

1. **Reverse Proxy**: Use nginx or Traefik
2. **SSL/TLS**: Enable HTTPS
3. **Authentication**: Add API key authentication
4. **Rate Limiting**: Implement request rate limiting
5. **Monitoring**: Add Prometheus metrics
6. **Logging**: Centralized logging with ELK stack
7. **Scaling**: Use Kubernetes for horizontal scaling

---

**The AI-Parrot Enterprise API provides a clean, RESTful interface to the powerful enterprise AI agent system, making it easy to integrate podcast generation into any application or workflow.** 🎯
