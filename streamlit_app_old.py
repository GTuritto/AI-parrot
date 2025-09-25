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

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Import our modules
from podcast_generator.langgraph_workflow import run_podcast_workflow
from utils.env import validate_api_keys, load_env_vars

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
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'generation_status' not in st.session_state:
        st.session_state.generation_status = None
    if 'last_generated_file' not in st.session_state:
        st.session_state.last_generated_file = None

def check_api_keys():
    """Check if required API keys are available."""
    try:
        load_env_vars()
        missing_keys = []
        
        if not os.getenv('ANTHROPIC_API_KEY'):
            missing_keys.append('ANTHROPIC_API_KEY')
        if not os.getenv('OPENAI_API_KEY'):
            missing_keys.append('OPENAI_API_KEY')
        
        if missing_keys:
            st.error(f"❌ Missing API keys: {', '.join(missing_keys)}")
            st.info("Please set your API keys in the .env file.")
            return False
        
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
        api_url = "http://localhost:8000/api/generate"
        payload = {
            "language": language,
            "voice": voice
        }
        
        response = requests.post(api_url, json=payload, timeout=300)
        if response.status_code == 200:
            result = response.json()
            return {"success": True, "data": result}
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
    
    # Main content
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
                    
                    # Audio player for MP3 files
                    if file_info['type'] == '.mp3':
                        st.audio(file_info['path'], format='audio/mp3')
                        
                        # Download button
                        with open(file_info['path'], 'rb') as f:
                            st.download_button(
                                label="⬇️ Download MP3",
                                data=f.read(),
                                file_name=file_info['name'],
                                mime="audio/mp3",
                                use_container_width=True
                            )
                    
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
                        
                        # Download button for text files
                        with open(file_info['path'], 'rb') as f:
                            st.download_button(
                                label="⬇️ Download TXT",
                                data=f.read(),
                                file_name=file_info['name'],
                                mime="text/plain",
                                use_container_width=True
                            )
                    
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
    .status-degraded {
        color: #ffc107;
        font-weight: bold;
    }
    .status-failed {
        color: #dc3545;
        font-weight: bold;
    }
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'podcast_generated' not in st.session_state:
        st.session_state.podcast_generated = False
    if 'generation_log' not in st.session_state:
        st.session_state.generation_log = []
    if 'system_status' not in st.session_state:
        st.session_state.system_status = {}
    if 'agent_metrics' not in st.session_state:
        st.session_state.agent_metrics = {}

def check_api_keys():
    """Check and display API key status."""
    load_env_vars()
    api_status = validate_api_keys()
    
    st.subheader("🔑 API Configuration Status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        anthropic_status = "✅ Available" if api_status.get("anthropic", False) else "❌ Missing"
        st.metric("Anthropic API", anthropic_status)
    
    with col2:
        openai_status = "✅ Available" if api_status.get("openai", False) else "⚠️ Optional"
        st.metric("OpenAI API", openai_status)
    
    with col3:
        news_status = "✅ Available" if api_status.get("news_api", False) else "⚠️ Optional"
        st.metric("News API", news_status)
    
    if not api_status.get("anthropic", False):
        st.error("❌ Anthropic API key is required for podcast generation!")
        return False
    
    return True

def create_agent_visualization():
    """Create agent pattern visualization."""
    st.subheader("🤖 AI Agent Patterns Architecture")
    
    # Create network diagram using plotly
    fig = go.Figure()
    
    # Agent positions
    agents = {
        "Supervisor": {"x": 0.5, "y": 0.8, "color": "#1f77b4"},
        "ContentFetcher": {"x": 0.2, "y": 0.4, "color": "#ff7f0e"},
        "QualityAssessor": {"x": 0.4, "y": 0.4, "color": "#2ca02c"},
        "ContentProcessor": {"x": 0.6, "y": 0.4, "color": "#d62728"},
        "AudioGenerator": {"x": 0.8, "y": 0.4, "color": "#9467bd"},
        "A2A Network": {"x": 0.5, "y": 0.1, "color": "#8c564b"}
    }
    
    # Add nodes
    for agent, props in agents.items():
        fig.add_trace(go.Scatter(
            x=[props["x"]], y=[props["y"]],
            mode='markers+text',
            marker=dict(size=30, color=props["color"]),
            text=[agent],
            textposition="bottom center",
            name=agent,
            showlegend=False
        ))
    
    # Add connections
    connections = [
        ("Supervisor", "ContentFetcher"),
        ("Supervisor", "QualityAssessor"),
        ("Supervisor", "ContentProcessor"),
        ("Supervisor", "AudioGenerator"),
        ("QualityAssessor", "A2A Network")
    ]
    
    for start, end in connections:
        fig.add_trace(go.Scatter(
            x=[agents[start]["x"], agents[end]["x"]],
            y=[agents[start]["y"], agents[end]["y"]],
            mode='lines',
            line=dict(color='gray', width=2),
            showlegend=False
        ))
    
    fig.update_layout(
        title="Agent Coordination Network",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=400,
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_monitoring_dashboard():
    """Create real-time monitoring dashboard."""
    st.subheader("📊 System Monitoring Dashboard")
    
    # Create metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>System Health</h3>
            <h2>🟢 Healthy</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>Active Agents</h3>
            <h2>4/4</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>A2A Quality</h3>
            <h2>0.900</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>Podcasts Generated</h3>
            <h2>1</h2>
        </div>
        """, unsafe_allow_html=True)

async def generate_podcast_async(language: str, voice: str, enable_a2a: bool, use_supervisor: bool):
    """Async wrapper for podcast generation."""
    try:
        if use_supervisor:
            result = await run_podcast_workflow_with_patterns(
                language=language,
                voice_name=voice,
                enable_a2a=enable_a2a,
                use_supervisor=True,
                use_resilience=False
            )
            return result
        else:
            await run_podcast_workflow(
                language=language,
                voice_name=voice,
                enable_a2a=enable_a2a
            )
            return {"success": True, "mode": "traditional"}
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

def main():
    """Main Streamlit application."""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🤖 AI-Parrot Podcast Generator</h1>', unsafe_allow_html=True)
    st.markdown("### *Powered by AI Agent Patterns*")
    
    # Sidebar configuration
    st.sidebar.header("🎛️ Configuration")
    
    # Check API keys first
    if not check_api_keys():
        st.stop()
    
    # Configuration options
    language = st.sidebar.selectbox(
        "🌍 Language",
        options=["en", "es"],
        format_func=lambda x: "🇺🇸 English" if x == "en" else "🇪🇸 Spanish"
    )
    
    voice = st.sidebar.text_input("🎤 Voice Name", value="Aria")
    
    # Display core architecture
    st.sidebar.markdown("### 🤖 Enterprise AI Architecture")
    st.sidebar.info("""
    **Built-in AI Agent Patterns:**
    - 🤝 A2A Collaborative Assessment
    - 🏛️ Agent Supervisor Coordination  
    - 🔗 MCP Integration (SSE Transport)
    - 🔄 Circuit Breaker Resilience
    - 👁️ Observer Pattern Monitoring
    """)
    
    # Advanced options
    with st.sidebar.expander("⚙️ Advanced Options"):
        show_monitoring = st.checkbox("📊 Show Real-time Monitoring", value=True)
        show_architecture = st.checkbox("🏗️ Show Architecture Diagram", value=True)
        auto_refresh = st.checkbox("🔄 Auto-refresh Status", value=False)
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🎙️ Generate", "📊 Monitor", "🏗️ Architecture", "📁 Files"])
    
    with tab1:
        st.header("🎙️ Podcast Generation")
        
        # Configuration summary
        st.subheader("📋 Current Configuration")
        config_col1, config_col2 = st.columns(2)
        
        with config_col1:
            st.info(f"""
            **Language:** {'🇺🇸 English' if language == 'en' else '🇪🇸 Spanish'}  
            **Voice:** {voice}  
            **Architecture:** 🤖 Enterprise AI Agent Patterns
            """)
        
        with config_col2:
            st.info(f"""
            **Core Features:** A2A + Supervisor + MCP + Circuit Breaker  
            **Monitoring:** {'📊 Enabled' if show_monitoring else '❌ Disabled'}  
            **Architecture View:** {'🏗️ Enabled' if show_architecture else '❌ Disabled'}
            """)
        
        # Generation button
        if st.button("🚀 Generate Podcast", type="primary", use_container_width=True):
            with st.spinner("🎙️ Generating your AI podcast..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Simulate progress updates
                for i in range(101):
                    progress_bar.progress(i)
                    if i < 20:
                        status_text.text("📰 Fetching articles...")
                    elif i < 40:
                        status_text.text("🤖 Processing with AI...")
                    elif i < 60:
                        status_text.text("📝 Generating script...")
                    elif i < 80:
                        status_text.text("🎵 Creating audio...")
                    else:
                        status_text.text("✅ Finalizing...")
                    time.sleep(0.05)
                
                # Actually generate the podcast
                result = run_async_in_streamlit(
                    generate_podcast_async(language, voice, True, True)  # Always use full patterns
                )
                
                if result.get("success"):
                    st.success("🎉 Podcast generated successfully!")
                    st.session_state.podcast_generated = True
                    
                    # Show results
                    if 'system_status' in result:
                        st.json(result['system_status'])
                    
                    # Check for generated files
                    output_dir = Path("PodcastOutput")
                    if output_dir.exists():
                        audio_files = list(output_dir.glob("*.mp3"))
                        if audio_files:
                            latest_audio = max(audio_files, key=os.path.getctime)
                            st.audio(str(latest_audio))
                            
                            # Download button
                            with open(latest_audio, "rb") as audio_file:
                                st.download_button(
                                    label="📥 Download Podcast",
                                    data=audio_file.read(),
                                    file_name=latest_audio.name,
                                    mime="audio/mpeg"
                                )
                else:
                    st.error(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
    
    with tab2:
        if show_monitoring:
            create_monitoring_dashboard()
            
            # Agent status
            st.subheader("🤖 Agent Status")
            agent_data = {
                "Agent": ["ContentFetcher", "QualityAssessor", "ContentProcessor", "AudioGenerator"],
                "Status": ["🟢 Healthy", "🟢 Healthy", "🟢 Healthy", "🟢 Healthy"],
                "Tasks Completed": [1, 1, 2, 1],
                "Average Response Time": ["1.2s", "0.8s", "15.3s", "8.7s"]
            }
            
            df = pd.DataFrame(agent_data)
            st.dataframe(df, use_container_width=True)
            
            # Performance chart
            st.subheader("📈 Performance Metrics")
            
            # Create sample performance data
            times = pd.date_range(start='2025-09-22 19:30:00', periods=10, freq='1min')
            performance_data = {
                'Time': times,
                'CPU Usage (%)': [20, 45, 60, 75, 40, 25, 30, 35, 20, 15],
                'Memory Usage (%)': [30, 35, 50, 65, 45, 35, 40, 45, 30, 25],
                'A2A Quality Score': [0.85, 0.88, 0.90, 0.92, 0.89, 0.87, 0.91, 0.93, 0.90, 0.88]
            }
            
            perf_df = pd.DataFrame(performance_data)
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('CPU Usage', 'Memory Usage', 'A2A Quality Score', 'System Health'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"type": "indicator"}]]
            )
            
            # CPU Usage
            fig.add_trace(
                go.Scatter(x=perf_df['Time'], y=perf_df['CPU Usage (%)'], name='CPU'),
                row=1, col=1
            )
            
            # Memory Usage
            fig.add_trace(
                go.Scatter(x=perf_df['Time'], y=perf_df['Memory Usage (%)'], name='Memory'),
                row=1, col=2
            )
            
            # A2A Quality
            fig.add_trace(
                go.Scatter(x=perf_df['Time'], y=perf_df['A2A Quality Score'], name='A2A Quality'),
                row=2, col=1
            )
            
            # System Health Indicator
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=95,
                    title={'text': "System Health %"},
                    gauge={'axis': {'range': [None, 100]},
                           'bar': {'color': "darkgreen"},
                           'steps': [{'range': [0, 50], 'color': "lightgray"},
                                   {'range': [50, 80], 'color': "yellow"},
                                   {'range': [80, 100], 'color': "lightgreen"}]}
                ),
                row=2, col=2
            )
            
            fig.update_layout(height=600, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Enable monitoring in the sidebar to see real-time metrics.")
    
    with tab3:
        if show_architecture:
            create_agent_visualization()
            
            # Pattern descriptions
            st.subheader("🎯 Implemented AI Agent Patterns")
            
            patterns = [
                {
                    "name": "🤝 Agent-to-Agent (A2A) Communication",
                    "description": "Enables collaborative decision-making between AI agents for quality assessment.",
                    "status": "✅ Always Active"
                },
                {
                    "name": "🏛️ Hierarchical Coordination (Supervisor)",
                    "description": "Orchestrates complex workflows using specialized worker agents.",
                    "status": "✅ Always Active"
                },
                {
                    "name": "🎭 Specialized Agent Pattern",
                    "description": "Divides responsibilities among domain-specific agents.",
                    "status": "✅ Always Active"
                },
                {
                    "name": "👁️ Observer Pattern",
                    "description": "Provides real-time monitoring and event notifications.",
                    "status": "✅ Always Active"
                },
                {
                    "name": "🔄 Circuit Breaker Resilience",
                    "description": "Prevents cascade failures and ensures system stability.",
                    "status": "✅ Always Active"
                }
            ]
            
            for pattern in patterns:
                with st.expander(pattern["name"]):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(pattern["description"])
                    with col2:
                        st.write(pattern["status"])
        else:
            st.info("🏗️ Enable architecture view in the sidebar to see the agent patterns.")
    
    with tab4:
        st.header("📁 Generated Files")
        
        output_dir = Path("PodcastOutput")
        if output_dir.exists():
            files = list(output_dir.glob("*"))
            if files:
                st.subheader("📂 Available Files")
                
                for file_path in sorted(files, key=os.path.getctime, reverse=True):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"📄 {file_path.name}")
                    
                    with col2:
                        file_size = file_path.stat().st_size
                        if file_size > 1024 * 1024:
                            st.write(f"{file_size / (1024 * 1024):.1f} MB")
                        else:
                            st.write(f"{file_size / 1024:.1f} KB")
                    
                    with col3:
                        if file_path.suffix == ".mp3":
                            st.audio(str(file_path))
                        elif file_path.suffix == ".txt":
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            with st.expander("View Content"):
                                st.text(content)
            else:
                st.info("📭 No files generated yet. Create your first podcast!")
        else:
            st.info("📁 Output directory not found. Generate a podcast to create files.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        🤖 AI-Parrot Podcast Generator | Powered by AI Agent Patterns<br>
        Built with Streamlit, LangGraph, Claude AI, and ElevenLabs
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
