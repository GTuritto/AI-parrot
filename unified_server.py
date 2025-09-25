"""
AI-Parrot Unified Server

Serves both FastAPI and Streamlit on the same port (8000).
- FastAPI endpoints available at /api/*
- Streamlit UI available at / (root)
"""

import asyncio
import subprocess
import threading
import time
import sys
import os
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import httpx

# Import the existing FastAPI app
from api.main import app as fastapi_app

def start_streamlit():
    """Start Streamlit server in a separate process"""
    print("🎨 Starting Streamlit server on port 8501...")
    subprocess.run([
        "streamlit", "run", "streamlit_app.py",
        "--server.port=8501",
        "--server.address=0.0.0.0",
        "--server.headless=true",
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false"
    ])

def wait_for_streamlit():
    """Wait for Streamlit to be ready"""
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = httpx.get("http://localhost:8501", timeout=1.0)
            if response.status_code == 200:
                print("✅ Streamlit is ready!")
                return True
        except:
            pass
        time.sleep(1)
    print("❌ Streamlit failed to start")
    return False

# Create the unified app
app = FastAPI(
    title="AI-Parrot Enterprise System",
    description="Unified FastAPI + Streamlit Interface",
    version="1.0.0"
)

# Mount the existing FastAPI app under /api
app.mount("/api", fastapi_app)

# Proxy requests to Streamlit
@app.get("/")
async def root():
    """Redirect to Streamlit UI"""
    return RedirectResponse(url="http://localhost:8501")

@app.get("/streamlit")
async def streamlit_redirect():
    """Redirect to Streamlit UI"""
    return RedirectResponse(url="http://localhost:8501")

@app.get("/info")
async def system_info():
    """System information endpoint"""
    return {
        "name": "AI-Parrot Enterprise Unified System",
        "version": "1.0.0",
        "services": {
            "fastapi": "http://localhost:8000/api",
            "streamlit_ui": "http://localhost:8501",
            "api_docs": "http://localhost:8000/api/docs",
            "health_check": "http://localhost:8000/api/health"
        },
        "enterprise_patterns": [
            "A2A Collaborative Assessment",
            "Agent Supervisor Coordination", 
            "MCP Integration with SSE Transport",
            "Circuit Breaker Resilience",
            "Observer Pattern Monitoring"
        ],
        "note": "Streamlit UI runs on port 8501, FastAPI on port 8000"
    }

def main():
    """Main function to start both servers"""
    print("🤖 AI-Parrot Enterprise Unified Server")
    print("=" * 50)
    print("🚀 Starting unified FastAPI + Streamlit server...")
    
    # Start Streamlit in a separate thread
    streamlit_thread = threading.Thread(target=start_streamlit, daemon=True)
    streamlit_thread.start()
    
    # Wait for Streamlit to be ready
    print("⏳ Waiting for Streamlit to start...")
    wait_for_streamlit()
    
    print("🌐 Starting unified server on port 8000...")
    print("📍 Access points:")
    print("   - Main UI: http://localhost:8000")
    print("   - API: http://localhost:8000/api")
    print("   - API Docs: http://localhost:8000/api/docs")
    print("   - Streamlit: http://localhost:8000/streamlit")
    print("   - System Info: http://localhost:8000/info")
    
    # Start the unified FastAPI server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

if __name__ == "__main__":
    main()
