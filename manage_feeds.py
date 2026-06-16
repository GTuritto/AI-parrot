#!/usr/bin/env python3
"""RSS Feed Management CLI Tool for AI-Parrot.

This tool allows you to manage RSS feeds without editing JSON files directly.

Usage:
    python manage_feeds.py list                    # List all feeds
    python manage_feeds.py add <name> <url>        # Add a new feed
    python manage_feeds.py enable <url>            # Enable a feed
    python manage_feeds.py disable <url>           # Disable a feed
    python manage_feeds.py test <url>              # Test a feed URL
"""

import sys
import argparse
import asyncio
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent
src_dir = project_root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from podcast_generator.config_loader import get_config_loader, RSSFeedConfig
from podcast_generator.article_fetcher import fetch_rss_feed_articles

def list_feeds():
    """List all configured RSS feeds."""
    config_loader = get_config_loader()
    feeds = config_loader.get_enabled_feeds()
    disabled_feeds = []
    
    # Get all feeds (including disabled)
    config = config_loader.load_config()
    all_feeds = config.get('rss_feeds', [])
    
    print("📰 RSS Feed Configuration")
    print("=" * 50)
    
    print("\n✅ ENABLED FEEDS:")
    if feeds:
        for i, feed in enumerate(feeds, 1):
            print(f"  {i}. {feed.name}")
            print(f"     URL: {feed.url}")
            print(f"     Source: {feed.source_label}")
            print(f"     Max Articles: {feed.max_articles}")
            if feed.description:
                print(f"     Description: {feed.description}")
            print()
    else:
        print("  No enabled feeds found.")
    
    # Show disabled feeds
    disabled_feeds = [feed for feed in all_feeds if not feed.get('enabled', True)]
    if disabled_feeds:
        print("\n❌ DISABLED FEEDS:")
        for i, feed in enumerate(disabled_feeds, 1):
            print(f"  {i}. {feed['name']}")
            print(f"     URL: {feed['url']}")
            print()

def add_feed(name: str, url: str, source_label: str = None, max_articles: int = 30):
    """Add a new RSS feed."""
    config_loader = get_config_loader()
    
    if source_label is None:
        # Try to extract source label from URL
        from urllib.parse import urlparse
        parsed = urlparse(url)
        source_label = parsed.netloc.replace('www.', '').title()
    
    feed_config = RSSFeedConfig(
        name=name,
        url=url,
        source_label=source_label,
        max_articles=max_articles,
        description=f"RSS feed for {name}",
        enabled=True
    )
    
    if config_loader.add_feed(feed_config):
        print(f"✅ Successfully added feed: {name}")
        print(f"   URL: {url}")
        print(f"   Source: {source_label}")
    else:
        print(f"❌ Failed to add feed: {name}")

def toggle_feed(url: str, enabled: bool):
    """Enable or disable a feed."""
    config_loader = get_config_loader()
    
    if config_loader.toggle_feed(url, enabled):
        status = "enabled" if enabled else "disabled"
        print(f"✅ Feed {status}: {url}")
    else:
        print(f"❌ Feed not found: {url}")

async def test_feed(url: str):
    """Test fetching from a specific RSS feed URL."""
    print(f"🧪 Testing RSS feed: {url}")
    print("-" * 50)
    
    # Create a temporary feed config for testing
    test_config = RSSFeedConfig(
        name="Test Feed",
        url=url,
        source_label="Test",
        max_articles=5,  # Limit for testing
        enabled=True
    )
    
    try:
        articles = await fetch_rss_feed_articles(test_config)
        
        if articles:
            print(f"✅ Successfully fetched {len(articles)} articles:")
            print()
            
            for i, article in enumerate(articles[:3], 1):  # Show first 3
                print(f"{i}. {article['title']}")
                print(f"   Source: {article['source']}")
                print(f"   Published: {article['published']}")
                print(f"   URL: {article['link']}")
                print()
            
            if len(articles) > 3:
                print(f"   ... and {len(articles) - 3} more articles")
        else:
            print("⚠️  No articles found or feed is empty")
            
    except Exception as e:
        print(f"❌ Error testing feed: {e}")

def show_config():
    """Show current configuration details."""
    config_loader = get_config_loader()
    filter_config = config_loader.get_content_filter_config()
    fetch_config = config_loader.get_fetching_config()
    
    print("⚙️  Current Configuration")
    print("=" * 50)
    
    print("\n📅 Content Filters:")
    print(f"   Date Range: {filter_config.date_range_days} days")
    print(f"   Min Content Length: {filter_config.min_content_length} chars")
    print(f"   Keywords: {len(filter_config.keywords)} configured")
    
    print("\n🔧 Fetching Config:")
    print(f"   Concurrent Requests: {fetch_config.concurrent_requests}")
    print(f"   Timeout: {fetch_config.timeout_seconds}s")
    print(f"   Retry Attempts: {fetch_config.retry_attempts}")
    print(f"   User Agent: {fetch_config.user_agent}")

def main():
    parser = argparse.ArgumentParser(
        description="Manage RSS feeds for AI-Parrot podcast generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python manage_feeds.py list
  python manage_feeds.py add "AI News" "https://example.com/ai/feed/"
  python manage_feeds.py enable "https://techcrunch.com/tag/artificial-intelligence/feed/"
  python manage_feeds.py disable "https://venturebeat.com/category/ai/feed/"
  python manage_feeds.py test "https://www.technologyreview.com/topic/artificial-intelligence/feed/"
  python manage_feeds.py config
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    subparsers.add_parser('list', help='List all RSS feeds')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new RSS feed')
    add_parser.add_argument('name', help='Feed name')
    add_parser.add_argument('url', help='Feed URL')
    add_parser.add_argument('--source', help='Source label (auto-detected if not provided)')
    add_parser.add_argument('--max-articles', type=int, default=30, help='Maximum articles to fetch')
    
    # Enable command
    enable_parser = subparsers.add_parser('enable', help='Enable a feed')
    enable_parser.add_argument('url', help='Feed URL to enable')
    
    # Disable command
    disable_parser = subparsers.add_parser('disable', help='Disable a feed')
    disable_parser.add_argument('url', help='Feed URL to disable')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test a feed URL')
    test_parser.add_argument('url', help='Feed URL to test')
    
    # Config command
    subparsers.add_parser('config', help='Show current configuration')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'list':
        list_feeds()
    elif args.command == 'add':
        add_feed(args.name, args.url, args.source, args.max_articles)
    elif args.command == 'enable':
        toggle_feed(args.url, True)
    elif args.command == 'disable':
        toggle_feed(args.url, False)
    elif args.command == 'test':
        asyncio.run(test_feed(args.url))
    elif args.command == 'config':
        show_config()

if __name__ == "__main__":
    main()
