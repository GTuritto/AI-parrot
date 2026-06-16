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
import aiohttp

from podcast_generator.mcp_client import MCPClient
from podcast_generator.config_loader import get_config_loader, RSSFeedConfig

# Configure logging
logger = logging.getLogger(__name__)

# A2A-enhanced article fetching with MCP integration

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


def is_within_date_range(published_date: datetime, days: Optional[int] = None) -> bool:
    """Check if a date is within the configured date range.
    
    Args:
        published_date: The date to check.
        days: Number of days to check. If None, uses configuration.
        
    Returns:
        True if the date is within the date range, False otherwise.
        
    🎓 Learning Note: Configuration-driven date filtering allows dynamic
    adjustment of content freshness requirements.
    """
    if days is None:
        config_loader = get_config_loader()
        filter_config = config_loader.get_content_filter_config()
        days = filter_config.date_range_days
    
    if published_date.tzinfo is not None:
        published_date = published_date.replace(tzinfo=None)

    cutoff_date = datetime.now() - timedelta(days=days)
    return published_date >= cutoff_date


async def fetch_rss_feed_articles(feed_config: RSSFeedConfig) -> List[Dict[str, Any]]:
    """Fetch articles from a single RSS feed using configuration.
    
    Args:
        feed_config: RSS feed configuration.
        
    Returns:
        List of article dictionaries with title, link, description, and published date.
        
    🎓 Learning Objective: Understand how to create generic, configurable
    functions that can handle multiple data sources.
    
    🔍 Pattern: Strategy Pattern
    This function implements a generic strategy for RSS feed processing,
    making it easy to add new feeds without code changes.
    """
    try:
        logger.info(f"Fetching articles from {feed_config.name} ({feed_config.url})")
        
        # Get fetching configuration
        config_loader = get_config_loader()
        fetch_config = config_loader.get_fetching_config()
        
        headers = {"User-Agent": fetch_config.user_agent}
        timeout = aiohttp.ClientTimeout(total=fetch_config.timeout_seconds)

        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            async with session.get(feed_config.url) as response:
                response.raise_for_status()
                feed_content = await response.read()

        # Parse the RSS feed from fetched bytes. feedparser itself is synchronous,
        # but parsing local content avoids blocking the event loop on network I/O.
        feed = feedparser.parse(feed_content)
        articles = []
        
        # Process entries up to the configured maximum
        max_entries = min(len(feed.entries), feed_config.max_articles)
        
        for entry in feed.entries[:max_entries]:
            try:
                # Parse publication date
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6])
                else:
                    # If no date available, use current time
                    published = datetime.now()
                
                # Check if article is within date range
                if is_within_date_range(published):
                    article = {
                        'title': entry.title,
                        'link': entry.link,
                        'description': getattr(entry, 'summary', ''),
                        'published': published,
                        'source': feed_config.source_label
                    }
                    
                    # Add content if available
                    if hasattr(entry, 'content') and entry.content:
                        article['content'] = entry.content[0].value if isinstance(entry.content, list) else str(entry.content)
                    
                    articles.append(article)
                    
            except Exception as e:
                logger.warning(f"Error processing article from {feed_config.name}: {e}")
                continue
        
        logger.info(f"✅ Fetched {len(articles)} articles from {feed_config.name}")
        return articles
        
    except Exception as e:
        logger.error(f"❌ Error fetching from {feed_config.name}: {e}")
        return []


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
                if is_within_date_range(mcp_article.published):
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
    """Fetch articles from RSS sources using configuration (fallback method).
    
    This method dynamically loads RSS feeds from configuration and fetches
    articles from all enabled feeds concurrently.
    
    Returns:
        Combined list of articles from all configured RSS sources.
        
    🎓 Learning Objective: See how configuration-driven systems enable
    dynamic behavior without code changes.
    
    🔍 Pattern: Configuration-Driven Execution
    The system behavior is controlled by external configuration, making it
    highly flexible and maintainable.
    """
    try:
        # Load RSS feed configurations
        config_loader = get_config_loader()
        enabled_feeds = config_loader.get_enabled_feeds()
        
        if not enabled_feeds:
            logger.warning("⚠️  No RSS feeds configured or enabled")
            return []
        
        logger.info(f"📡 Fetching from {len(enabled_feeds)} RSS sources")
        
        # Create tasks for concurrent fetching
        tasks = [fetch_rss_feed_articles(feed_config) for feed_config in enabled_feeds]
        
        # Wait for all fetches to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results from all sources
        all_articles = []
        successful_fetches = 0
        
        for i, result in enumerate(results):
            if isinstance(result, list):
                all_articles.extend(result)
                successful_fetches += 1
                logger.info(f"✅ {enabled_feeds[i].name}: {len(result)} articles")
            elif isinstance(result, Exception):
                logger.error(f"❌ {enabled_feeds[i].name}: {result}")
        
        logger.info(f"📊 RSS Summary: {len(all_articles)} articles from {successful_fetches}/{len(enabled_feeds)} sources")
        return all_articles
        
    except Exception as e:
        logger.error(f"❌ Error in RSS fetching: {e}")
        return []


def _contains_interesting_keywords(title: str, description: str) -> bool:
    """Check if article contains interesting AI-related keywords from configuration.
    
    Args:
        title: Article title
        description: Article description
        
    Returns:
        True if article contains relevant keywords, False otherwise.
        
    🎓 Learning Note: Configuration-driven keyword filtering allows dynamic
    content relevance adjustment without code changes.
    
    🔍 Pattern: Strategy Pattern with Configuration
    The filtering strategy is externalized to configuration, making it
    easily modifiable for different use cases.
    """
    try:
        # Get keywords from configuration
        config_loader = get_config_loader()
        filter_config = config_loader.get_content_filter_config()
        keywords = filter_config.keywords
        
        content = f"{title} {description}".lower()
        
        for keyword in keywords:
            if keyword.lower() in content:
                return True
        
        return False
        
    except Exception as e:
        logger.warning(f"Error in keyword filtering: {e}")
        # Fallback to basic AI keywords if configuration fails
        basic_keywords = ["AI", "Artificial Intelligence", "Machine Learning"]
        content = f"{title} {description}".lower()
        return any(keyword.lower() in content for keyword in basic_keywords)


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
