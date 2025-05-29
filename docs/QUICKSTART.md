# Podcast Generator - Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- [UV](https://github.com/astral-sh/uv) for virtual environment and dependency management
- API keys for required services (see Configuration)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Mujica
   ```

2. Set up the environment:
   ```bash
   # Create and activate virtual environment
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   uv pip install -e .
   
   # Copy and configure environment variables
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Configuration

### API Keys

Create a `.env` file in the project root with the following variables:

```bash
# Required API Keys
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Optional: News API key if using RSS feed fallback
NEWS_API_KEY=your_news_api_key
```

### Environment Variables

The script will automatically load variables from the `.env` file. You can also set them in your environment:

```bash
export ANTHROPIC_API_KEY='your_key_here'
export ELEVENLABS_API_KEY='your_key_here'
```

## Troubleshooting

### Common Issues

1. **Permission Denied** when running the script:
   ```bash
   chmod +x run_podcast.sh
   ```

2. **Virtual Environment Not Found**:
   The script will automatically create one if it doesn't exist.

3. **Missing Dependencies**:
   The script will automatically install required dependencies.
```

## Usage

### Basic Usage (Recommended)

Run the podcast generator using the provided script:

```bash
# Make the script executable (only needed once)
chmod +x run_podcast.sh

# Run the podcast generator
./run_podcast.sh
```

### Manual Execution

If you prefer to run it manually:

```bash
# Activate the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run the podcast generator
python -m podcast_generator.main
```

### Advanced Options

```bash
# Generate a podcast with custom settings
poetry run python run_podcast.py \
    --num-articles 5 \
    --output-dir ./my_podcasts \
    --voice "Aria" \
    --topic "AI and Technology"
```

### Available Arguments

- `--num-articles`: Number of articles to include (default: 5)
- `--output-dir`: Directory to save generated files (default: ./PodcastOutput)
- `--voice`: Voice to use for TTS (default: "Aria")
- `--topic`: Topic for the podcast (default: "AI and Technology")

## Output Files

The generator creates the following files in the output directory:

- `AIpodcast_<DATE>_narrative.txt`: The generated podcast script
- `AIpodcast_<DATE>.mp3`: The generated audio file

## Available Voices

To list all available voices:

```bash
poetry run python -c "from elevenlabs import voices; print([v.name for v in voices()])"
```

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure all required API keys are set in the `.env` file
   - Verify the keys have the correct permissions

2. **Audio Generation Fails**
   - Check your ElevenLabs API key and quota
   - Ensure you have a stable internet connection

3. **Article Fetching Issues**
   - Check if the RSS feed URLs are accessible
   - Verify your network connection

## Updating

To update to the latest version:

```bash
git pull origin main
poetry install
```

## Support

For issues and feature requests, please use the [issue tracker](<repository-url>/issues).

## License

[Specify your license here]
