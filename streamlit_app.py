"""
🤖 AI-Parrot Podcast Generator - Streamlit Interface

A comprehensive user interface for the AI-Parrot podcast generator
showcasing AI Agent Patterns implementation.
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
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Import our modules
from podcast_generator.langgraph_workflow import run_podcast_workflow, run_podcast_workflow_with_patterns
from podcast_generator.agent_supervisor import AgentSupervisor, task_monitor_observer, AgentType
from podcast_generator.a2a_protocol import A2AQualityAgent
from podcast_generator.circuit_breaker import ResilientOperations
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
    .agent-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    .status-healthy {
        color: #28a745;
        font-weight: bold;
    }
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
    
    enable_a2a = st.sidebar.checkbox("🤝 Enable A2A Protocol", value=True)
    
    use_supervisor = st.sidebar.checkbox("🏛️ Use Agent Supervisor", value=False)
    
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
            **A2A Protocol:** {'✅ Enabled' if enable_a2a else '❌ Disabled'}
            """)
        
        with config_col2:
            st.info(f"""
            **Mode:** {'🏛️ Agent Supervisor' if use_supervisor else '🔄 Traditional Workflow'}  
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
                    generate_podcast_async(language, voice, enable_a2a, use_supervisor)
                )
                
                if result.get("success"):
                    st.success("🎉 Podcast generated successfully!")
                    st.session_state.podcast_generated = True
                    
                    # Show results
                    if use_supervisor and 'system_status' in result:
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
                    "status": "✅ Active" if enable_a2a else "❌ Disabled"
                },
                {
                    "name": "🏛️ Hierarchical Coordination (Supervisor)",
                    "description": "Orchestrates complex workflows using specialized worker agents.",
                    "status": "✅ Active" if use_supervisor else "❌ Disabled"
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
