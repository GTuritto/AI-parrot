# AI-Parrot Enterprise System - Production Container
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
COPY requirements-api.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-api.txt

# Copy application code
COPY src/ ./src/
COPY api/ ./api/
COPY streamlit_app.py ./streamlit_app.py
COPY config/ ./config/
COPY manage_feeds.py ./manage_feeds.py
COPY .env.template .env.template

# Set Python path
ENV PYTHONPATH="/app/src:/app"

# Create necessary directories
RUN mkdir -p PodcastOutput memory config

# Expose ports for API and Streamlit
EXPOSE 8000 8501

# Health check for API service
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
