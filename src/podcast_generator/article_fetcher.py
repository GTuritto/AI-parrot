"""Article fetching and processing module for podcast generation.

🎓 Learning Objectives:
- Understand hybrid content sourcing strategies (MCP + RSS)
- Learn fallback patterns for resilient systems
- Practice async content aggregation from multiple sources
- Implement content deduplication and filtering algorithms

🔍 Pattern Analysis:
This module implements the Strategy Pattern with Fallback:
- Primary Strategy: MCP server-based dynamic content fetching
- Fallback Strategy: Traditional RSS feed parsing
- Content Aggregator: Combines and deduplicates from all sources
- Filter Chain: Applies keyword and date filtering

💡 Real-world Applications:
- News aggregation platforms
- Content management systems
- Social media feed aggregators
- Research paper collection systems
"""
import asyncio
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

import feedparser
from bs4 import BeautifulSoup
import requests

from podcast_generator.mcp_client import MCPClient, MCPArticle

# Configure logging
logger = logging.getLogger(__name__)

# A2A-enhanced article fetching with MCP integration

# Define keywords for interesting articles
INTERESTING_KEYWORDS = [
    "AI", "Artificial Intelligence", "Machine Learning", "Deep Learning", 
    "LLM", "GPT", "Large Language Model", "ChatGPT", "ChatGPT-4", 
    "Mistral", "MistralAI", "Llama", "Ollama", "OpenAI", "Anthropic", 
    "Claude", "AI Ethics", "AI Policy", "AI Regulation", "AI Governance"
]

# MCP Server Configuration
# 🎓 Learning Note: This configuration allows dynamic server discovery
# You can add multiple MCP servers for redundancy and diverse content sources
def get_mcp_server_configs() -> List[Dict[str, Any]]:
    """Get MCP server configurations from environment or defaults.
    
    Returns:
        List of MCP server configurations
        
    🔍 Pattern: Configuration Factory
    This centralizes server configuration and allows environment-based setup.
    """
    configs = []
    
    # Check for environment-based MCP server configuration
    mcp_server_url = os.getenv('MCP_SERVER_URL')  # HTTP transport
    mcp_sse_url = os.getenv('MCP_SSE_URL')        # SSE transport
    mcp_server_name = os.getenv('MCP_SERVER_NAME', 'local-mcp-server')
    mcp_api_key = os.getenv('MCP_API_KEY')
    
    if mcp_server_url or mcp_sse_url:
        config = {
            'name': mcp_server_name,
        }
        
        # Add both transport URLs if available
        if mcp_server_url:
            config['base_url'] = mcp_server_url
        if mcp_sse_url:
            config['sse_url'] = mcp_sse_url
            
        if mcp_api_key:
            config['api_key'] = mcp_api_key
            
        configs.append(config)
        transport_info = []
        if mcp_server_url:
            transport_info.append(f"HTTP: {mcp_server_url}")
        if mcp_sse_url:
            transport_info.append(f"SSE: {mcp_sse_url}")
        logger.info(f"Added MCP server '{mcp_server_name}' with transports: {', '.join(transport_info)}")
    
    # Add additional servers from environment variables
    # Format: MCP_SERVER_1_URL, MCP_SERVER_1_SSE_URL, MCP_SERVER_1_NAME, MCP_SERVER_1_API_KEY, etc.
    server_index = 1
    while True:
        url_key = f'MCP_SERVER_{server_index}_URL'
        sse_key = f'MCP_SERVER_{server_index}_SSE_URL'
        name_key = f'MCP_SERVER_{server_index}_NAME'
        api_key_key = f'MCP_SERVER_{server_index}_API_KEY'
        
        server_url = os.getenv(url_key)
        sse_url = os.getenv(sse_key)
        
        if not server_url and not sse_url:
            break
            
        config = {
            'name': os.getenv(name_key, f'mcp-server-{server_index}'),
        }
        
        if server_url:
            config['base_url'] = server_url
        if sse_url:
            config['sse_url'] = sse_url
        
        api_key = os.getenv(api_key_key)
        if api_key:
            config['api_key'] = api_key
            
        configs.append(config)
        logger.info(f"Added MCP server {server_index}: {config['name']}")
        server_index += 1
    
    return configs


def is_within_last_two_weeks(published_date: datetime) -> bool:
    """Check if a date is within the last two weeks.
    
    Args:
        published_date: The date to check.
        
    Returns:
        True if the date is within the last two weeks, False otherwise.
    """
    two_weeks_ago = datetime.now() - timedelta(days=14)
    return published_date >= two_weeks_ago


async def fetch_techcrunch_articles() -> List[Dict[str, Any]]:
    """Fetch AI articles from TechCrunch.
    
    Returns:
        List of article dictionaries with title, link, description, and published date.
    """
    techcrunch_url = "https://techcrunch.com/tag/artificial-intelligence/feed/"
    feed = feedparser.parse(techcrunch_url)
    articles = []
    
    for entry in feed.entries[:50]:  # Increased from 30 to 50 to get more articles
        try:
            published = datetime(*entry.published_parsed[:6])
            if is_within_last_two_weeks(published):
                articles.append({
                    'title': entry.title,
                    'link': entry.link,
                    'description': entry.summary,
                    'published': published,
                    'source': 'TechCrunch'
                })
        except Exception as e:
            print(f"Error processing TechCrunch article: {e}")
    
    return articles


async def fetch_mit_tech_review_ai() -> List[Dict[str, Any]]:
    """Fetch AI articles from MIT Technology Review's AI section.
    
    Returns:
        List of article dictionaries with title, link, description, and published date.
    """
    url = "https://www.technologyreview.com/topic/artificial-intelligence/feed/"
    feed = feedparser.parse(url)
    articles = []
    
    for entry in feed.entries[:40]:
        try:
            published = datetime(*entry.published_parsed[:6])
            if is_within_last_two_weeks(published):
                articles.append({
                    'title': entry.title,
                    'link': entry.link,
                    'description': entry.summary,
                    'published': published,
                    'source': 'MIT Tech Review'
                })
        except Exception as e:
            print(f"Error processing MIT Tech Review article: {e}")
    
    return articles


async def fetch_venturebeat_ai() -> List[Dict[str, Any]]:
    """Fetch AI articles from VentureBeat's AI section.
    
    Returns:
        List of article dictionaries with title, link, description, and published date.
    """
    url = "https://venturebeat.com/category/ai/feed/"
    feed = feedparser.parse(url)
    articles = []
    
    for entry in feed.entries[:40]:
        try:
            published = datetime(*entry.published_parsed[:6])
            if is_within_last_two_weeks(published):
                articles.append({
                    'title': entry.title,
                    'link': entry.link,
                    'description': entry.summary,
                    'published': published,
                    'source': 'VentureBeat'
                })
        except Exception as e:
            print(f"Error processing VentureBeat article: {e}")
    
    return articles


async def fetch_articles_from_mcp() -> List[Dict[str, Any]]:
    """Fetch articles from MCP servers (primary method).
    
    🎓 Learning Objective: Understand how to implement primary/fallback patterns
    for resilient content sourcing.
    
    Returns:
        List of articles from MCP sources, or empty list if no MCP servers configured.
    """
    mcp_configs = get_mcp_server_configs()
    
    if not mcp_configs:
        logger.info("No MCP servers configured, skipping MCP fetch")
        return []
    
    try:
        async with MCPClient(mcp_configs) as mcp_client:
            logger.info(f"Fetching articles from {len(mcp_configs)} MCP servers")
            mcp_articles = await mcp_client.fetch_articles_from_mcp(max_articles=50)
            
            # Convert MCPArticle objects to the expected dictionary format
            articles = []
            for mcp_article in mcp_articles:
                # Filter by date (last two weeks)
                if is_within_last_two_weeks(mcp_article.published):
                    # Filter by keywords
                    if _contains_interesting_keywords(mcp_article.title, mcp_article.description):
                        article_dict = {
                            'title': mcp_article.title,
                            'link': mcp_article.link,
                            'description': mcp_article.description,
                            'published': mcp_article.published,
                            'source': f"MCP-{mcp_article.source}",
                            'content': mcp_article.content,
                            'metadata': mcp_article.metadata
                        }
                        articles.append(article_dict)
            
            logger.info(f"Successfully fetched {len(articles)} relevant articles from MCP servers")
            return articles
            
    except Exception as e:
        logger.error(f"Error fetching articles from MCP servers: {e}")
        return []


async def fetch_multiple_sources() -> List[Dict[str, Any]]:
    """Fetch articles from multiple sources with MCP-first strategy.
    
    🔍 Pattern: Primary/Fallback Strategy Implementation
    
    This implements a resilient content sourcing strategy:
    1. Primary: Try MCP servers first (dynamic, configurable)
    2. Fallback: Use RSS feeds if MCP fails or returns insufficient articles
    3. Hybrid: Combine both sources for maximum coverage
    
    Returns:
        Combined list of articles from all available sources.
        
    🧪 Experiment: Try disabling MCP servers (remove env vars) and see
    how the system gracefully falls back to RSS feeds.
    """
    all_articles = []
    
    # Step 1: Try MCP servers first
    logger.info("Attempting to fetch articles from MCP servers...")
    mcp_articles = await fetch_articles_from_mcp()
    
    if mcp_articles:
        all_articles.extend(mcp_articles)
        logger.info(f"✅ MCP fetch successful: {len(mcp_articles)} articles")
    else:
        logger.info("⚠️  MCP fetch returned no articles, will rely on RSS fallback")
    
    # Step 2: Fetch from RSS sources (either as fallback or supplement)
    logger.info("Fetching articles from RSS sources...")
    rss_articles = await fetch_rss_sources()
    
    if rss_articles:
        all_articles.extend(rss_articles)
        logger.info(f"✅ RSS fetch successful: {len(rss_articles)} articles")
    else:
        logger.warning("⚠️  RSS fetch also failed")
    
    # Step 3: Remove duplicates and return
    unique_articles = _remove_duplicates(all_articles)
    
    logger.info(f"📊 Final result: {len(unique_articles)} unique articles from {len(all_articles)} total")
    logger.info(f"   - MCP articles: {len(mcp_articles)}")
    logger.info(f"   - RSS articles: {len(rss_articles)}")
    logger.info(f"   - Duplicates removed: {len(all_articles) - len(unique_articles)}")
    
    return unique_articles


async def fetch_rss_sources() -> List[Dict[str, Any]]:
    """Fetch articles from RSS sources (fallback method).
    
    This is the original RSS-based fetching method, now used as a fallback
    or supplement to MCP-based fetching.
    
    Returns:
        Combined list of articles from RSS sources.
    """
    # Fetch from multiple RSS sources concurrently
    tasks = [
        fetch_techcrunch_articles(),
        fetch_mit_tech_review_ai(),
        fetch_venturebeat_ai()
    ]
    
    # Wait for all fetches to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Combine results from all sources
    all_articles = []
    for result in results:
        if isinstance(result, list):
            all_articles.extend(result)
        elif isinstance(result, Exception):
            logger.error(f"RSS fetch error: {result}")
    
    return all_articles


def _contains_interesting_keywords(title: str, description: str) -> bool:
    """Check if article contains interesting AI-related keywords.
    
    Args:
        title: Article title
        description: Article description
        
    Returns:
        True if article contains relevant keywords, False otherwise.
        
    🎓 Learning Note: This implements a simple content filtering algorithm.
    In production, you might use more sophisticated NLP techniques.
    """
    content = f"{title} {description}".lower()
    
    for keyword in INTERESTING_KEYWORDS:
        if keyword.lower() in content:
            return True
    
    return False


def _remove_duplicates(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate articles based on title and URL.
    
    🔍 Pattern: Deduplication Algorithm
    
    This implements a multi-field deduplication strategy:
    1. Primary key: Article title (normalized)
    2. Secondary key: Article URL (for same title, different sources)
    3. Preference: Keep the article with more content/metadata
    
    Args:
        articles: List of article dictionaries.
        
    Returns:
        List of unique articles.
        
    🧪 Experiment: Try modifying the deduplication logic to prefer
    articles from specific sources or with more recent publication dates.
    """
    # Enhanced deduplication based on title and URL
    seen_articles = {}  # key: (title, domain), value: article
    unique_articles = []
    
    for article in articles:
        title = article['title'].lower().strip()
        
        # Extract domain from URL for better deduplication
        try:
            from urllib.parse import urlparse
            domain = urlparse(article.get('link', '')).netloc
        except:
            domain = article.get('source', 'unknown')
        
        key = (title, domain)
        
        # If we haven't seen this article, add it
        if key not in seen_articles:
            seen_articles[key] = article
            unique_articles.append(article)
        else:
            # If we have seen it, keep the one with more content
            existing = seen_articles[key]
            current_content_length = len(article.get('description', '') + article.get('content', ''))
            existing_content_length = len(existing.get('description', '') + existing.get('content', ''))
            
            if current_content_length > existing_content_length:
                # Replace with the more detailed version
                unique_articles.remove(existing)
                unique_articles.append(article)
                seen_articles[key] = article
    
    logger.info(f"Deduplication: {len(articles)} -> {len(unique_articles)} articles")
    return unique_articles


