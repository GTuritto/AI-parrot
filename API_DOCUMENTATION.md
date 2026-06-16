<p align="center">
  <img src="assets/ai-parrot-logo.png" alt="AI-Parrot logo" width="320" />
</p>

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

# Run the API server on localhost
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

## 📋 **API Endpoints**

### **🔐 Optional Authentication**

By default, local development does not require an API token. If you set `AI_PARROT_API_TOKEN`, protected endpoints require one of these headers:

```http
Authorization: Bearer your_token
```

```http
X-API-Key: your_token
```

Use this for non-local deployments. It protects endpoints that can spend API credits, expose logs, list files, download outputs, or inspect memory state. Health checks remain open so Docker and uptime monitors can work without a secret.

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
POST /api/generate
```
Queues a podcast generation task and returns immediately.

Podcast generation calls external RSS/MCP services, LLMs, translation, and text-to-speech. The API therefore uses a task workflow:

1. Submit `POST /generate` or `POST /api/generate`.
2. Read the returned `task_id`.
3. Poll `GET /tasks/{task_id}` or `GET /api/tasks/{task_id}` until the task is `completed` or `failed`.
4. Download the generated file from `/download/{filename}`.

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

**Queued Response (`202 Accepted`):**
```json
{
  "success": true,
  "message": "Podcast generation queued",
  "task_id": "8d6f68b8-6c1a-4b72-a6db-0cbb24a2a1d0"
}
```

### **⏳ Task Status**
```http
GET /tasks/{task_id}
GET /api/tasks/{task_id}
```
Returns the current state of a queued podcast generation task.

**States:**
- `queued`: The API accepted the request and has not started work yet.
- `running`: Agents are fetching, summarizing, scripting, translating, or generating audio.
- `completed`: The task finished and `result` contains the output metadata.
- `failed`: The task failed and `error` explains why.

**Completed Response:**
```json
{
  "task_id": "8d6f68b8-6c1a-4b72-a6db-0cbb24a2a1d0",
  "status": "completed",
  "created_at": "2026-06-16T18:30:00",
  "updated_at": "2026-06-16T18:31:15",
  "request": {
    "language": "en",
    "voice": "Aria"
  },
  "result": {
    "success": true,
    "audio_path": "PodcastOutput/podcast_20260616_183115_Aria_en.mp3",
    "articles_processed": 15,
    "tasks_completed": 4,
    "generation_time": 75.3
  },
  "error": null
}
```

### **📁 List Files**
```http
GET /files
GET /api/files
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
      "download_url": "/download/podcast_20260616_183115_Aria_en.mp3"
    }
  ]
}
```

### **📥 Download File**
```http
GET /download/{filename}
GET /api/download/{filename}
```
Downloads a generated podcast file.

**Parameters:**
- `filename` (string): Name of the file to download

**Response:** Binary file download

### **📊 System Status**
```http
GET /status
GET /api/status
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

# Queue an English podcast
TASK_ID=$(curl -s -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{"language": "en", "voice": "Aria"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['task_id'])")

# Poll until status is completed or failed
curl -X GET "http://localhost:8000/api/tasks/${TASK_ID}"

# List generated files
curl -X GET "http://localhost:8000/api/files"

# Download a podcast
curl -X GET "http://localhost:8000/api/download/podcast_20260616_183115_Aria_en.mp3" \
  --output podcast.mp3
```

### **Python Client Example**

```python
import requests
import time
import os

# API base URL
BASE_URL = "http://localhost:8000"
HEADERS = {}
if os.getenv("AI_PARROT_API_TOKEN"):
    HEADERS["Authorization"] = f"Bearer {os.environ['AI_PARROT_API_TOKEN']}"

def generate_podcast(language="en", voice="Aria"):
    """Queue a podcast and wait for completion."""
    response = requests.post(
        f"{BASE_URL}/api/generate",
        json={"language": language, "voice": voice},
        headers=HEADERS,
        timeout=30,
    )
    response.raise_for_status()
    task_id = response.json()["task_id"]

    while True:
        task_response = requests.get(
            f"{BASE_URL}/api/tasks/{task_id}",
            headers=HEADERS,
            timeout=10,
        )
        task_response.raise_for_status()
        task = task_response.json()

        if task["status"] == "completed":
            return task["result"]
        if task["status"] == "failed":
            raise RuntimeError(task["error"])

        time.sleep(5)

def download_podcast(filename, output_path):
    """Download a generated podcast."""
    response = requests.get(f"{BASE_URL}/api/download/{filename}", headers=HEADERS)
    response.raise_for_status()
    with open(output_path, 'wb') as f:
        f.write(response.content)

# Usage
result = generate_podcast("en", "Aria")
if result["success"]:
    print(f"Podcast generated: {result['audio_path']}")
```

### **JavaScript/Node.js Example**

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';
const HEADERS = process.env.AI_PARROT_API_TOKEN
  ? { Authorization: `Bearer ${process.env.AI_PARROT_API_TOKEN}` }
  : {};

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function generatePodcast(language = 'en', voice = 'Aria') {
  try {
    const queued = await axios.post(
      `${BASE_URL}/api/generate`,
      { language, voice },
      { headers: HEADERS }
    );

    const taskId = queued.data.task_id;
    while (true) {
      const task = await axios.get(`${BASE_URL}/api/tasks/${taskId}`, { headers: HEADERS });
      if (task.data.status === 'completed') return task.data.result;
      if (task.data.status === 'failed') throw new Error(task.data.error);
      await sleep(5000);
    }
  } catch (error) {
    console.error('Error generating podcast:', error.response?.data);
    throw error;
  }
}

// Usage
generatePodcast('en', 'Aria')
  .then(result => {
    console.log('Podcast generated:', result.audio_path);
  })
  .catch(console.error);
```

## 🐳 **Docker Configuration**

### **Environment Variables**

```env
# Required API Keys
ANTHROPIC_API_KEY=your_anthropic_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here

# Optional API Keys
OPENAI_API_KEY=your_openai_key_here
NEWS_API_KEY=your_news_api_key_here
AI_PARROT_API_TOKEN=change_me_for_non_local_deployments

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

# Run the container on localhost
docker run -p 127.0.0.1:8000:8000 --env-file .env ai-parrot-enterprise

# Run with docker-compose
docker-compose up --build

# View logs
docker-compose logs -f ai-parrot-api

# Stop the service
docker-compose down
```

## 🔒 **Security Considerations**

1. **API Keys**: Never commit API keys to version control
2. **Environment**: Use `.env` files or environment variables
3. **Network**: Consider running behind a reverse proxy (nginx)
4. **Authentication**: Set `AI_PARROT_API_TOKEN` for non-local deployments
5. **Rate Limiting**: Implement rate limiting for production deployments

## 📈 **Monitoring**

The API provides several monitoring endpoints:

- `/health` or `/api/health` - Basic health check
- `/status` or `/api/status` - Detailed system status
- `/tasks/{task_id}` or `/api/tasks/{task_id}` - Podcast generation progress
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
