"""Article fetching and processing module for podcast generation."""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any

import feedparser
from bs4 import BeautifulSoup
import requests

# A2A-enhanced article fetching

# Define keywords for interesting articles
INTERESTING_KEYWORDS = [
    "AI", "Artificial Intelligence", "Machine Learning", "Deep Learning", 
    "LLM", "GPT", "Large Language Model", "ChatGPT", "ChatGPT-4", 
    "Mistral", "MistralAI", "Llama", "Ollama", "OpenAI", "Anthropic", 
    "Claude", "AI Ethics", "AI Policy", "AI Regulation", "AI Governance"
]


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


async def fetch_multiple_sources() -> List[Dict[str, Any]]:
    """Fetch articles from multiple sources using direct RSS (original method).
    
    Fetches from multiple AI news sources and combines the results.
    
    Returns:
        Combined list of articles from all sources.
    """
    # Fetch from multiple sources concurrently
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
    
    return _remove_duplicates(all_articles)


def _remove_duplicates(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate articles based on title.
    
    Args:
        articles: List of article dictionaries.
        
    Returns:
        List of unique articles.
    """
    # Remove duplicates based on article title
    seen_titles = set()
    unique_articles = []
    for article in articles:
        title = article['title'].lower().strip()
        if title not in seen_titles:
            seen_titles.add(title)
            unique_articles.append(article)
    
    return unique_articles


