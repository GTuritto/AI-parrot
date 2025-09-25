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
COPY unified_server.py ./unified_server.py
COPY .env.template .env.template

# Set Python path
ENV PYTHONPATH="/app/src:/app"

# Create output directory
RUN mkdir -p PodcastOutput

# Expose unified server port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the unified server
CMD ["python", "unified_server.py"]
