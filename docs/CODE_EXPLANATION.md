# Podcast Generator - Code Explanation

## Table of Contents
1. [Core Components](#core-components)
2. [Workflow](#workflow)
3. [Key Classes](#key-classes)
4. [Important Methods](#important-methods)
5. [Configuration](#configuration)
6. [Extending the System](#extending-the-system)

## Core Components

### 1. Article Fetcher (`article_fetcher.py`)
Responsible for fetching articles from RSS feeds and formatting them for processing.

### 2. AI Processor (`ai_processor.py`)
Handles all AI-related operations including article summarization and content generation.

### 3. File Utils (`file_utils.py`)
Manages file operations including saving text and audio files.

### 4. LangGraph Workflow (`langgraph_workflow.py`)
Orchestrates the podcast generation process using a state machine pattern.

### 5. Main Entry Point (`main.py`)
Provides the command-line interface for the application.

## Workflow

```mermaid
graph LR
    A[Start] --> B[Fetch Articles]
    B --> C[Process Articles]
    C --> D[Generate Script]
    D --> E[Generate Audio]
    E --> F[Save Files]
    F --> G[End]
    
    style A fill:#9f9,stroke:#333
    style G fill:#f99,stroke:#333
```

## Key Classes

### 1. `AIProcessor`
Handles all AI-related operations using Claude AI.

**Key Methods:**
- `summarize_article`: Summarizes a single article
- `generate_podcast_script`: Creates a podcast script from article summaries

### 2. `FileManager`
Manages all file operations.

**Key Methods:**
- `save_text_file`: Saves text content to a file
- `save_mp3_file`: Converts text to speech and saves as MP3
- `save_articles_to_csv`: Saves article data to a CSV file

### 3. `ArticleFetcher`
Fetches and processes articles from RSS feeds.

**Key Methods:**
- `fetch_articles`: Fetches articles from configured sources
- `process_article`: Processes raw article data into a structured format

## Important Methods

### Article Processing
```python
def summarize_article(self, article: Dict[str, Any]) -> str:
    """Summarize an article using Claude AI."""
    # Implementation details...
```

### Script Generation
```python
async def generate_podcast_script(articles: List[Dict[str, Any]]) -> str:
    """Generate a podcast script from article summaries."""
    # Implementation details...
```

### Audio Generation
```python
def save_mp3_file(self, text_content: str, voice_name: str = "Aria") -> str:
    """Convert text to speech and save as MP3."""
    # Implementation details...
```

## Configuration

The system is configured using environment variables loaded from a `.env` file:

```ini
# Required
ELEVENLABS_API_KEY=your_api_key
ANTHROPIC_API_KEY=your_api_key

# Optional
NEWS_API_KEY=your_news_api_key
OUTPUT_DIR=./output
```

## Extending the System

### Adding New Article Sources
1. Create a new method in `ArticleFetcher`
2. Update the `fetch_articles` method to include the new source

### Adding New AI Models
1. Create a new processor class
2. Implement the required interface
3. Update the factory method in `AIProcessor`

### Customizing Voice Output
Modify the `save_mp3_file` method in `FileManager` to support additional voice parameters.

## Error Handling

The system includes comprehensive error handling for:
- API failures
- Network issues
- File system errors
- Invalid input data

## Testing

Run the test suite with:

```bash
pytest tests/
```

## Performance Considerations

- Uses asynchronous I/O for network operations
- Implements caching where appropriate
- Handles large files efficiently

## Security Considerations

- API keys are never hardcoded
- Input validation is performed on all external data
- Sensitive files are excluded from version control
