#!/bin/bash

# AI-Parrot Streamlit UI Launcher
echo "🤖 Starting AI-Parrot Podcast Generator UI..."
echo "🌐 The interface will open in your browser at http://localhost:8501"
echo ""

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
fi

# Install dependencies if needed
echo "📋 Checking dependencies..."
pip install streamlit plotly pandas

# Set Python path
export PYTHONPATH="./src:$PYTHONPATH"

# Launch Streamlit
echo "🚀 Launching Streamlit interface..."
streamlit run streamlit_app.py
