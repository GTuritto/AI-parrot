#!/usr/bin/env python3
"""
AI-Parrot Enterprise API Client Example

This script demonstrates how to interact with the AI-Parrot Enterprise API
to generate podcasts using the enterprise AI agent patterns.
"""

import requests
import json
import time
import os
from pathlib import Path
from typing import Dict, Any, Optional

class AIParrotClient:
    """Client for the AI-Parrot Enterprise API."""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token or os.getenv("AI_PARROT_API_TOKEN", "")

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}
        
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the API."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def system_status(self) -> Dict[str, Any]:
        """Get detailed system status."""
        response = requests.get(f"{self.base_url}/status", headers=self._headers())
        response.raise_for_status()
        return response.json()
    
    def generate_podcast(self, language: str = "en", voice: str = "Aria") -> Dict[str, Any]:
        """Generate a podcast using the enterprise AI agent system."""
        payload = {
            "language": language,
            "voice": voice
        }
        
        print(f"🚀 Generating podcast: {language}/{voice}")
        response = requests.post(
            f"{self.base_url}/generate",
            json=payload,
            headers=self._headers(),
            timeout=30
        )
        response.raise_for_status()
        queued = response.json()
        task_id = queued.get("task_id")
        if not task_id:
            return queued

        deadline = time.time() + 900
        while time.time() < deadline:
            task = self.get_task_status(task_id)
            if task["status"] == "completed":
                return task.get("result", {})
            if task["status"] == "failed":
                raise RuntimeError(task.get("error") or "Podcast generation failed")
            time.sleep(5)

        raise TimeoutError(f"Podcast generation task timed out: {task_id}")

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status of a podcast generation task."""
        response = requests.get(
            f"{self.base_url}/tasks/{task_id}",
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    
    def list_files(self) -> Dict[str, Any]:
        """List all generated podcast files."""
        response = requests.get(f"{self.base_url}/files", headers=self._headers())
        response.raise_for_status()
        return response.json()
    
    def download_file(self, filename: str, output_path: str = None) -> str:
        """Download a generated podcast file."""
        if output_path is None:
            output_path = filename
            
        response = requests.get(f"{self.base_url}/download/{filename}", headers=self._headers())
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        return output_path

def main():
    """Main example function."""
    print("🤖 AI-Parrot Enterprise API Client Example")
    print("=" * 50)
    
    # Initialize client
    client = AIParrotClient()
    
    try:
        # Check health
        print("\n💚 Checking API health...")
        health = client.health_check()
        print(f"Status: {health['status']}")
        print(f"Enterprise Patterns: {health['enterprise_patterns']}")
        
        # Check system status
        print("\n📊 Getting system status...")
        status = client.system_status()
        print(f"System: {status['system']}")
        print(f"Podcasts Generated: {status['statistics']['podcasts_generated']}")
        
        # Generate a podcast
        print("\n🎙️ Generating English podcast...")
        result = client.generate_podcast("en", "Aria")
        
        if result['success']:
            print("✅ Podcast generated successfully!")
            print(f"   🎵 Audio: {result['audio_path']}")
            print(f"   📰 Articles: {result['articles_processed']}")
            print(f"   🤝 A2A Score: {result['a2a_quality_score']}")
            print(f"   ⏱️ Time: {result['generation_time']:.2f}s")
            
            # List files
            print("\n📁 Listing generated files...")
            files = client.list_files()
            for file_info in files['files'][:3]:  # Show first 3 files
                print(f"   📄 {file_info['name']} ({file_info['size']} bytes)")
        else:
            print(f"❌ Generation failed: {result['message']}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running:")
        print("   docker-compose up")
        print("   or")
        print("   ./run_api.sh")
    except requests.exceptions.HTTPError as e:
        print(f"❌ API Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
