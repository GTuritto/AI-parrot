"""
🤖 AI-Parrot Podcast Generator - Streamlit Interface

A clean, user-friendly interface for generating and managing AI podcasts.
"""

import streamlit as st
import asyncio
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Import our modules
from podcast_generator.langgraph_workflow import run_podcast_workflow
from utils.env import validate_api_keys, load_env_vars

def api_headers() -> Dict[str, str]:
    """Return API auth headers when a local token is configured."""
    token = os.getenv("AI_PARROT_API_TOKEN", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


def api_base_url() -> str:
    """Return the configured API base URL."""
    return os.getenv("AI_PARROT_API_URL", "http://localhost:8000").rstrip("/")

# Page configuration
st.set_page_config(
    page_title="🤖 AI-Parrot Podcast Generator",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .podcast-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .file-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
    }
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    .metric-card {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .monitoring-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'generation_status' not in st.session_state:
        st.session_state.generation_status = None
    if 'last_generated_file' not in st.session_state:
        st.session_state.last_generated_file = None
    if 'logs' not in st.session_state:
        st.session_state.logs = []

def check_api_keys():
    """Check if required API keys are available."""
    try:
        load_env_vars()
        missing_keys = []
        
        if not os.getenv('ANTHROPIC_API_KEY'):
            missing_keys.append('ANTHROPIC_API_KEY')
        
        if missing_keys:
            st.error(f"❌ Missing API keys: {', '.join(missing_keys)}")
            st.info("Please set your API keys in the .env file.")
            return False

        if not os.getenv('OPENAI_API_KEY'):
            st.info("OPENAI_API_KEY is optional. Spanish translation and GPT refinement may fall back or be skipped.")
        
        return True
    except Exception as e:
        st.error(f"❌ Error loading environment: {str(e)}")
        return False

def get_podcast_files():
    """Get list of generated podcast files."""
    output_dir = Path("PodcastOutput")
    if not output_dir.exists():
        return []
    
    files = []
    for file_path in output_dir.iterdir():
        if file_path.is_file():
            files.append({
                'name': file_path.name,
                'path': str(file_path),
                'size': file_path.stat().st_size,
                'modified': datetime.fromtimestamp(file_path.stat().st_mtime),
                'type': file_path.suffix.lower()
            })
    
    return sorted(files, key=lambda x: x['modified'], reverse=True)

async def generate_podcast_async(language: str, voice: str):
    """Generate podcast using the enterprise AI system."""
    try:
        # Use the API endpoint instead of direct function call for better reliability
        base_url = api_base_url()
        api_url = f"{base_url}/generate"
        payload = {
            "language": language,
            "voice": voice
        }
        
        response = requests.post(api_url, json=payload, headers=api_headers(), timeout=30)
        if response.status_code in (200, 202):
            queued = response.json()
            task_id = queued.get("task_id")
            if not task_id:
                return {"success": True, "data": queued}

            deadline = time.time() + 900
            while time.time() < deadline:
                task_response = requests.get(
                    f"{base_url}/tasks/{task_id}",
                    headers=api_headers(),
                    timeout=10,
                )
                task_response.raise_for_status()
                task = task_response.json()

                if task["status"] == "completed":
                    return {"success": True, "data": task.get("result", {}), "task_id": task_id}
                if task["status"] == "failed":
                    return {
                        "success": False,
                        "error": task.get("error") or "Podcast generation failed",
                        "task_id": task_id,
                    }

                await asyncio.sleep(5)

            return {"success": False, "error": "Podcast generation timed out", "task_id": task_id}
        else:
            return {"success": False, "error": f"API Error: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        # Fallback to direct function call if API is not available
        try:
            await run_podcast_workflow(language=language, voice_name=voice)
            return {"success": True, "mode": "direct"}
        except Exception as direct_error:
            return {"success": False, "error": str(direct_error)}
    except Exception as e:
        return {"success": False, "error": str(e)}

def run_async_in_streamlit(coro):
    """Run async function in Streamlit."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

def format_file_size(size_bytes):
    """Format file size in human readable format."""
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes} bytes"

def get_system_status():
    """Get system status from API."""
    try:
        response = requests.get(f"{api_base_url()}/status", headers=api_headers(), timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "message": "API not responding"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_api_health():
    """Get API health status."""
    try:
        response = requests.get(f"{api_base_url()}/health", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "unhealthy", "message": "API not responding"}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}

def create_monitoring_dashboard():
    """Create a clean monitoring dashboard."""
    st.markdown('<div class="monitoring-section">', unsafe_allow_html=True)
    st.subheader("📊 System Monitoring")
    
    # Get system data
    system_status = get_system_status()
    api_health = get_api_health()
    files = get_podcast_files()
    
    # Create metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        health_status = "🟢 Healthy" if api_health.get("status") == "healthy" else "🔴 Unhealthy"
        st.markdown(f"""
        <div class="metric-card">
            <h4>System Health</h4>
            <h2>{health_status}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_files = len(files)
        audio_files = len([f for f in files if f['type'] == '.mp3'])
        st.markdown(f"""
        <div class="metric-card">
            <h4>Podcasts Generated</h4>
            <h2>{audio_files}</h2>
            <small>{total_files} total files</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Calculate total storage used
        total_size = sum([f['size'] for f in files])
        storage_display = format_file_size(total_size)
        st.markdown(f"""
        <div class="metric-card">
            <h4>Storage Used</h4>
            <h2>{storage_display}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Show API key status
        api_keys = api_health.get("api_keys", {})
        active_keys = sum([1 for k, v in api_keys.items() if v])
        total_keys = len(api_keys)
        st.markdown(f"""
        <div class="metric-card">
            <h4>API Keys</h4>
            <h2>{active_keys}/{total_keys}</h2>
            <small>Active</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Enterprise patterns status
    st.subheader("🤖 Enterprise AI Patterns Status")
    patterns_col1, patterns_col2 = st.columns(2)
    
    with patterns_col1:
        enterprise_patterns = api_health.get("enterprise_patterns", {})
        pattern_status = []
        for pattern, status in enterprise_patterns.items():
            status_icon = "✅" if status else "❌"
            pattern_name = pattern.replace("_", " ").title()
            pattern_status.append(f"{status_icon} {pattern_name}")
        
        if pattern_status:
            st.success("**Active Patterns:**\n" + "\n".join(pattern_status))
        else:
            st.info("Enterprise patterns information not available")
    
    with patterns_col2:
        # API Keys detailed status
        st.subheader("🔑 API Keys Status")
        if api_keys:
            for key_name, status in api_keys.items():
                status_icon = "✅" if status else "❌"
                key_display = key_name.replace("_", " ").title()
                st.write(f"{status_icon} **{key_display}**: {'Available' if status else 'Missing'}")
        else:
            st.info("API key status not available")
    
    # Recent activity chart
    if files:
        st.subheader("📈 Recent Activity")
        
        # Create activity timeline
        df_files = pd.DataFrame(files)
        df_files['date'] = pd.to_datetime(df_files['modified']).dt.date
        
        # Count files by date
        activity_data = df_files.groupby(['date', 'type']).size().reset_index(name='count')
        
        if not activity_data.empty:
            fig = px.bar(
                activity_data, 
                x='date', 
                y='count', 
                color='type',
                title="Files Generated Over Time",
                labels={'count': 'Files Generated', 'date': 'Date'}
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No activity data available yet")
    
    # File size distribution
    if files:
        st.subheader("💾 Storage Distribution")
        
        # Create pie chart of file sizes by type
        size_by_type = {}
        for file_info in files:
            file_type = file_info['type']
            if file_type not in size_by_type:
                size_by_type[file_type] = 0
            size_by_type[file_type] += file_info['size']
        
        if size_by_type:
            fig = px.pie(
                values=list(size_by_type.values()),
                names=list(size_by_type.keys()),
                title="Storage Usage by File Type"
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def get_docker_logs():
    """Get Docker container logs."""
    logs = []
    
    # Method 1: Try API endpoint first
    try:
        result = requests.get(f"{api_base_url()}/api/logs", headers=api_headers(), timeout=10)
        if result.status_code == 200:
            api_response = result.json()
            logs = api_response.get("logs", [])
            if logs and len(logs) > 3:  # More than just placeholder messages
                return logs
    except Exception as e:
        logs.append(f"API logs unavailable: {str(e)}")
    
    # Method 2: Try docker-compose logs
    try:
        import subprocess
        import os
        
        # Try to find the project directory
        project_dirs = [
            "/Users/giuseppe/Documents/Coding/AI-parrot",
            os.getcwd(),
            os.path.dirname(os.path.abspath(__file__))
        ]
        
        for project_dir in project_dirs:
            if os.path.exists(os.path.join(project_dir, "docker-compose.yml")):
                result = subprocess.run(
                    ["docker-compose", "logs", "--tail=100", "ai-parrot-api"], 
                    capture_output=True, 
                    text=True, 
                    cwd=project_dir,
                    timeout=15
                )
                if result.returncode == 0 and result.stdout:
                    docker_logs = result.stdout.split('\n')
                    # Filter out empty lines and add timestamps
                    filtered_logs = []
                    for log in docker_logs:
                        if log.strip():
                            # Add timestamp if not present
                            if not log.startswith('[') and not log.startswith('ai-parrot'):
                                log = f"[{datetime.now().strftime('%H:%M:%S')}] {log}"
                            filtered_logs.append(log.strip())
                    return filtered_logs[-100:]  # Return last 100 lines
                elif result.stderr:
                    logs.append(f"Docker logs error: {result.stderr}")
                break
    except Exception as e:
        logs.append(f"Docker command failed: {str(e)}")
    
    # Method 3: Try direct docker logs
    try:
        import subprocess
        result = subprocess.run(
            ["docker", "logs", "--tail=50", "ai-parrot-ai-parrot-api-1"], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout.split('\n')[-50:]
    except Exception as e:
        logs.append(f"Direct docker logs failed: {str(e)}")
    
    # Method 4: Fallback - provide helpful information
    if not logs or len(logs) < 5:
        logs = [
            f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Unable to fetch real-time logs",
            f"[{datetime.now().strftime('%H:%M:%S')}] 📋 To view logs manually:",
            f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Run: docker-compose logs ai-parrot-api",
            f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Or: docker logs ai-parrot-ai-parrot-api-1",
            f"[{datetime.now().strftime('%H:%M:%S')}] 📊 API Status: Check the Monitoring tab",
            f"[{datetime.now().strftime('%H:%M:%S')}] 💡 For terminal debugging: ./run_podcast.sh"
        ]
    
    return logs

def create_logs_tab():
    """Create logs viewing tab."""
    st.subheader("📋 System Logs")
    
    # Control panel
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.info("Real-time system and API logs from Docker container")
    with col2:
        auto_refresh = st.checkbox("🔄 Auto-refresh", value=False, key="auto_refresh_logs")
    with col3:
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.rerun()
    
    # Auto-refresh logic
    if auto_refresh:
        import time
        time.sleep(2)
        st.rerun()
    
    # Get logs
    logs = get_docker_logs()
    
    if logs:
        # Filter options
        log_filter = st.selectbox(
            "Filter logs:",
            ["All", "Errors only", "API calls", "Generation process"],
            key="log_filter"
        )
        
        # Filter logs based on selection
        filtered_logs = []
        for log in logs[-100:]:  # Show last 100 lines
            log_lower = log.lower()
            if log_filter == "All":
                filtered_logs.append(log)
            elif log_filter == "Errors only":
                # Enhanced error detection
                error_keywords = [
                    "error", "failed", "exception", "traceback", "401", "402", "403", "404", "500", "502", "503", "504",
                    "timeout", "connection refused", "quota_exceeded", "overloaded", "retry", "❌", "⚠️"
                ]
                if any(keyword in log_lower for keyword in error_keywords):
                    filtered_logs.append(log)
            elif log_filter == "API calls":
                # Enhanced API call detection
                api_keywords = ["post", "get", "put", "delete", "patch", "http request", "api.", "/api/", "curl"]
                if any(keyword in log_lower for keyword in api_keywords):
                    filtered_logs.append(log)
            elif log_filter == "Generation process":
                # Enhanced generation process detection
                gen_keywords = [
                    "generating", "podcast", "agent", "supervisor", "a2a", "fetch", "articles", "summariz", 
                    "script", "audio", "translation", "workflow", "task", "🤖", "🎙️", "📰", "✅"
                ]
                if any(keyword in log_lower for keyword in gen_keywords):
                    filtered_logs.append(log)
        
        # Display logs in a text area
        log_text = '\n'.join(filtered_logs) if filtered_logs else "No logs match the current filter"
        st.text_area(
            "Logs:",
            value=log_text,
            height=400,
            key="logs_display"
        )
        
        # Download logs button
        if filtered_logs:
            log_content = '\n'.join(filtered_logs)
            st.download_button(
                label="📥 Download Logs",
                data=log_content,
                file_name=f"ai-parrot-logs-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
    else:
        st.warning("No logs available")

def main():
    """Main Streamlit application."""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🤖 AI-Parrot Podcast Generator</h1>', unsafe_allow_html=True)
    st.markdown("### *Enterprise AI-Powered Podcast Creation*")
    
    # Check API keys first
    if not check_api_keys():
        st.stop()
    
    # Sidebar configuration
    st.sidebar.header("🎛️ Podcast Configuration")
    
    language = st.sidebar.selectbox(
        "🌍 Language",
        options=["en", "es"],
        format_func=lambda x: "🇺🇸 English" if x == "en" else "🇪🇸 Spanish"
    )
    
    voice = st.sidebar.selectbox(
        "🎤 Voice",
        options=["Aria", "Sarah", "Lily", "Custom"],
        help="Select the voice for your podcast"
    )
    
    if voice == "Custom":
        voice = st.sidebar.text_input("Enter custom voice name", value="Aria")
    
    # Enterprise features info
    st.sidebar.markdown("### 🤖 AI Features")
    st.sidebar.success("""
    ✅ **Always Active:**
    - A2A Collaborative Assessment
    - Agent Supervisor Coordination  
    - MCP Integration
    - Circuit Breaker Resilience
    - Observer Pattern Monitoring
    """)
    
    # Monitoring options
    st.sidebar.markdown("### 📊 Monitoring")
    show_monitoring = st.sidebar.checkbox("Enable System Monitoring", value=False, help="Show real-time system metrics and charts")
    
    if show_monitoring:
        auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)", value=False)
        if auto_refresh:
            time.sleep(30)
            st.rerun()
    
    # Main content - Add tabs
    tab1, tab2, tab3 = st.tabs(["🎙️ Generate & Files", "📊 Monitoring", "📋 Logs"])
    
    with tab1:
        # Two column layout for generation and files
        col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("🎙️ Generate New Podcast")
        
        # Configuration display
        st.markdown(f"""
        <div class="podcast-card">
            <h3>📋 Current Configuration</h3>
            <p><strong>Language:</strong> {'🇺🇸 English' if language == 'en' else '🇪🇸 Spanish'}</p>
            <p><strong>Voice:</strong> {voice}</p>
            <p><strong>AI System:</strong> Enterprise Agent Patterns</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Generation button
        if st.button("🚀 Generate Podcast", type="primary", use_container_width=True):
            with st.spinner("🤖 AI agents are working on your podcast..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Simulate progress updates
                progress_steps = [
                    (20, "📰 Fetching latest tech articles..."),
                    (40, "🤖 AI agents analyzing content..."),
                    (60, "✍️ Generating podcast script..."),
                    (80, "🎤 Converting text to speech..."),
                    (100, "✅ Podcast generation complete!")
                ]
                
                for progress, message in progress_steps:
                    progress_bar.progress(progress)
                    status_text.text(message)
                    time.sleep(1)
                
                # Generate podcast
                result = run_async_in_streamlit(
                    generate_podcast_async(language, voice)
                )
                
                if result["success"]:
                    st.success("🎉 Podcast generated successfully!")
                    st.session_state.generation_status = "success"
                    st.rerun()
                else:
                    st.error(f"❌ Generation failed: {result['error']}")
                    st.session_state.generation_status = "error"
        
        # Show generation status
        if st.session_state.generation_status == "success":
            st.success("✅ Last generation: Successful")
        elif st.session_state.generation_status == "error":
            st.error("❌ Last generation: Failed")
    
        with col2:
            st.header("📁 Generated Podcasts")
            
            # Refresh button
            if st.button("🔄 Refresh List", use_container_width=True):
                st.rerun()
            
            # Get and display files
            files = get_podcast_files()
            
            if files:
                st.success(f"📊 Found {len(files)} files")
                
                # Filter options
                file_types = list(set([f['type'] for f in files]))
                selected_types = st.multiselect(
                    "Filter by type:",
                    options=file_types,
                    default=file_types,
                    key="file_filter"
                )
                
                # Display files
                filtered_files = [f for f in files if f['type'] in selected_types]
                
                for file_info in filtered_files:
                    with st.container():
                        st.markdown(f"""
                        <div class="file-card">
                            <h4>📄 {file_info['name']}</h4>
                            <p><strong>Size:</strong> {format_file_size(file_info['size'])}</p>
                            <p><strong>Modified:</strong> {file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Action buttons row
                        btn_col1, btn_col2, btn_col3 = st.columns(3)
                        
                        # Audio player for MP3 files
                        if file_info['type'] == '.mp3':
                            st.audio(file_info['path'], format='audio/mp3')
                            
                            with btn_col1:
                                # Download MP3 button
                                with open(file_info['path'], 'rb') as f:
                                    st.download_button(
                                        label="🎵 Download MP3",
                                        data=f.read(),
                                        file_name=file_info['name'],
                                        mime="audio/mp3",
                                        use_container_width=True,
                                        key=f"download_mp3_{file_info['name']}"
                                    )
                        
                            with btn_col2:
                                # Play button (already handled by st.audio)
                                st.info("▶️ Player above")
                            
                            with btn_col3:
                                # Delete button
                                if st.button("🗑️ Delete", key=f"delete_mp3_{file_info['name']}", use_container_width=True):
                                    try:
                                        os.remove(file_info['path'])
                                        st.success(f"Deleted {file_info['name']}")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error deleting file: {e}")
                    
                        # Text content viewer
                        elif file_info['type'] == '.txt':
                            with st.expander("📖 View Content"):
                                try:
                                    with open(file_info['path'], 'r', encoding='utf-8') as f:
                                        content = f.read()
                                    st.text_area(
                                        "Content:",
                                        value=content,
                                        height=200,
                                        key=f"content_{file_info['name']}"
                                    )
                                except Exception as e:
                                    st.error(f"Error reading file: {e}")
                        
                            with btn_col1:
                                # Download TXT button
                                with open(file_info['path'], 'rb') as f:
                                    st.download_button(
                                        label="📄 Download TXT",
                                        data=f.read(),
                                        file_name=file_info['name'],
                                        mime="text/plain",
                                        use_container_width=True,
                                        key=f"download_txt_{file_info['name']}"
                                    )
                        
                            with btn_col2:
                                # View button (already handled by expander)
                                st.info("👁️ Expand above")
                            
                            with btn_col3:
                                # Delete button
                                if st.button("🗑️ Delete", key=f"delete_txt_{file_info['name']}", use_container_width=True):
                                    try:
                                        os.remove(file_info['path'])
                                        st.success(f"Deleted {file_info['name']}")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error deleting file: {e}")
                    
                        # Other file types
                        else:
                            with btn_col1:
                                # Generic download button
                                with open(file_info['path'], 'rb') as f:
                                    st.download_button(
                                        label=f"⬇️ Download {file_info['type'].upper()}",
                                        data=f.read(),
                                        file_name=file_info['name'],
                                        use_container_width=True,
                                        key=f"download_other_{file_info['name']}"
                                    )
                        
                            with btn_col3:
                                # Delete button
                                if st.button("🗑️ Delete", key=f"delete_other_{file_info['name']}", use_container_width=True):
                                    try:
                                        os.remove(file_info['path'])
                                        st.success(f"Deleted {file_info['name']}")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error deleting file: {e}")
                    
                        st.markdown("---")
            else:
                st.info("📭 No podcasts generated yet. Create your first podcast using the generator on the left!")
                
                # Quick start guide
                st.markdown("""
                ### 🚀 Quick Start Guide
                1. **Select Language**: Choose English or Spanish
                2. **Pick a Voice**: Select from available voices
                3. **Generate**: Click the generate button
                4. **Listen**: Your podcast will appear here for playback
                5. **Download**: Save your podcasts locally
                """)
    
    with tab2:
        # Monitoring tab
        if show_monitoring:
            create_monitoring_dashboard()
        else:
            st.info("📊 Enable 'System Monitoring' in the sidebar to view real-time metrics and charts.")
            st.markdown("""
            ### 🔍 What you'll see when monitoring is enabled:
            - **System Health** - API status and connectivity
            - **Enterprise AI Patterns** - Status of all 5 AI agent patterns
            - **Storage Analytics** - File usage and distribution
            - **Activity Timeline** - Generation history over time
            - **API Keys Status** - Configuration validation
            """)
    
    with tab3:
        # Logs tab
        create_logs_tab()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        🤖 <strong>AI-Parrot Podcast Generator</strong> | Powered by Enterprise AI Agent Patterns<br>
        Built with Streamlit, LangGraph, Claude AI, and ElevenLabs TTS
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
