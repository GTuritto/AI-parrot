"""Configuration loader for RSS feeds and content filtering.

🎓 Learning Objectives:
- Understand configuration management patterns
- Learn JSON-based configuration loading
- Practice error handling for configuration files
- Implement configuration validation

🔍 Pattern Analysis:
This module implements the Configuration Pattern:
- Centralized configuration management
- JSON-based configuration files
- Environment variable overrides
- Configuration validation and defaults
- Hot-reloading capabilities

💡 Real-world Applications:
- Microservices configuration management
- Feature flag systems
- Content management systems
- API endpoint configuration
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class RSSFeedConfig:
    """Configuration for a single RSS feed.
    
    🎓 Learning Note: Using dataclasses for type safety and validation.
    """
    name: str
    url: str
    source_label: str
    max_articles: int = 30
    description: str = ""
    enabled: bool = True

@dataclass
class ContentFilterConfig:
    """Configuration for content filtering.
    
    🔍 Pattern: Value Object
    Encapsulates filtering configuration with validation.
    """
    keywords: List[str]
    date_range_days: int = 14
    min_content_length: int = 50

@dataclass
class FetchingConfig:
    """Configuration for fetching behavior.
    
    💡 Real-world Application: Similar to HTTP client configuration
    in production systems.
    """
    concurrent_requests: bool = True
    timeout_seconds: int = 30
    retry_attempts: int = 3
    user_agent: str = "AI-Parrot Podcast Generator/1.0"

class ConfigLoader:
    """Loads and manages RSS feed configuration.
    
    🎓 Educational Focus:
    - Configuration file management
    - Error handling and fallbacks
    - Environment variable integration
    - Configuration validation
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize the configuration loader.
        
        Args:
            config_file: Path to the configuration file. If None, uses default.
        """
        if config_file is None:
            # Default to config/rss_feeds.json relative to project root
            project_root = Path(__file__).parent.parent.parent
            config_file = project_root / "config" / "rss_feeds.json"
        
        self.config_file = Path(config_file)
        self._config_cache = None
        self._last_modified = None
    
    def load_config(self, force_reload: bool = False) -> Dict[str, Any]:
        """Load configuration from file with caching.
        
        Args:
            force_reload: If True, ignore cache and reload from file.
            
        Returns:
            Configuration dictionary.
            
        🔍 Pattern: Lazy Loading with Cache Invalidation
        """
        try:
            # Check if we need to reload
            if (force_reload or 
                self._config_cache is None or 
                self._file_modified_since_cache()):
                
                logger.info(f"Loading RSS configuration from {self.config_file}")
                
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config_cache = json.load(f)
                
                self._last_modified = self.config_file.stat().st_mtime
                self._validate_config(self._config_cache)
                
                logger.info(f"✅ Loaded configuration with {len(self.get_enabled_feeds())} enabled feeds")
            
            return self._config_cache
            
        except FileNotFoundError:
            logger.warning(f"⚠️  Configuration file not found: {self.config_file}")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in configuration file: {e}")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"❌ Error loading configuration: {e}")
            return self._get_default_config()
    
    def get_enabled_feeds(self) -> List[RSSFeedConfig]:
        """Get list of enabled RSS feeds.
        
        Returns:
            List of enabled RSS feed configurations.
        """
        config = self.load_config()
        feeds = []
        
        for feed_data in config.get('rss_feeds', []):
            if feed_data.get('enabled', True):
                feeds.append(RSSFeedConfig(**feed_data))
        
        return feeds
    
    def get_content_filter_config(self) -> ContentFilterConfig:
        """Get content filtering configuration.
        
        Returns:
            Content filter configuration.
        """
        config = self.load_config()
        filter_data = config.get('content_filters', {})
        
        return ContentFilterConfig(
            keywords=filter_data.get('keywords', self._get_default_keywords()),
            date_range_days=filter_data.get('date_range_days', 14),
            min_content_length=filter_data.get('min_content_length', 50)
        )
    
    def get_fetching_config(self) -> FetchingConfig:
        """Get fetching configuration.
        
        Returns:
            Fetching configuration.
        """
        config = self.load_config()
        fetch_data = config.get('fetching_config', {})
        
        return FetchingConfig(
            concurrent_requests=fetch_data.get('concurrent_requests', True),
            timeout_seconds=fetch_data.get('timeout_seconds', 30),
            retry_attempts=fetch_data.get('retry_attempts', 3),
            user_agent=fetch_data.get('user_agent', "AI-Parrot Podcast Generator/1.0")
        )
    
    def add_feed(self, feed_config: RSSFeedConfig, save: bool = True) -> bool:
        """Add a new RSS feed to the configuration.
        
        Args:
            feed_config: RSS feed configuration to add.
            save: If True, save the configuration to file.
            
        Returns:
            True if feed was added successfully, False otherwise.
            
        🧪 Experiment: Try adding feeds dynamically and see how the system
        adapts to new content sources.
        """
        try:
            config = self.load_config()
            
            # Check if feed already exists
            for existing_feed in config.get('rss_feeds', []):
                if existing_feed.get('url') == feed_config.url:
                    logger.warning(f"Feed already exists: {feed_config.url}")
                    return False
            
            # Add the new feed
            feed_dict = {
                'name': feed_config.name,
                'url': feed_config.url,
                'source_label': feed_config.source_label,
                'max_articles': feed_config.max_articles,
                'description': feed_config.description,
                'enabled': feed_config.enabled
            }
            
            config.setdefault('rss_feeds', []).append(feed_dict)
            
            if save:
                self._save_config(config)
            
            # Invalidate cache
            self._config_cache = None
            
            logger.info(f"✅ Added RSS feed: {feed_config.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding RSS feed: {e}")
            return False
    
    def toggle_feed(self, feed_url: str, enabled: Optional[bool] = None) -> bool:
        """Toggle or set the enabled status of a feed.
        
        Args:
            feed_url: URL of the feed to toggle.
            enabled: If provided, set to this value. If None, toggle current state.
            
        Returns:
            True if feed was found and updated, False otherwise.
        """
        try:
            config = self.load_config()
            
            for feed in config.get('rss_feeds', []):
                if feed.get('url') == feed_url:
                    if enabled is None:
                        feed['enabled'] = not feed.get('enabled', True)
                    else:
                        feed['enabled'] = enabled
                    
                    self._save_config(config)
                    self._config_cache = None  # Invalidate cache
                    
                    status = "enabled" if feed['enabled'] else "disabled"
                    logger.info(f"✅ Feed {status}: {feed.get('name', feed_url)}")
                    return True
            
            logger.warning(f"⚠️  Feed not found: {feed_url}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error toggling feed: {e}")
            return False
    
    def _file_modified_since_cache(self) -> bool:
        """Check if configuration file was modified since last cache.
        
        Returns:
            True if file was modified, False otherwise.
        """
        try:
            if self._last_modified is None:
                return True
            
            current_mtime = self.config_file.stat().st_mtime
            return current_mtime > self._last_modified
        except:
            return True
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration structure.
        
        Args:
            config: Configuration dictionary to validate.
            
        Raises:
            ValueError: If configuration is invalid.
        """
        required_keys = ['rss_feeds']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required configuration key: {key}")
        
        # Validate RSS feeds
        for i, feed in enumerate(config['rss_feeds']):
            required_feed_keys = ['name', 'url', 'source_label']
            for key in required_feed_keys:
                if key not in feed:
                    raise ValueError(f"Missing required key '{key}' in feed {i}")
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file.
        
        Args:
            config: Configuration dictionary to save.
        """
        # Ensure directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Configuration saved to {self.config_file}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration as fallback.
        
        Returns:
            Default configuration dictionary.
        """
        logger.info("🔄 Using default RSS configuration")
        
        return {
            "rss_feeds": [
                {
                    "name": "TechCrunch AI",
                    "url": "https://techcrunch.com/tag/artificial-intelligence/feed/",
                    "source_label": "TechCrunch",
                    "max_articles": 50,
                    "description": "TechCrunch's artificial intelligence news",
                    "enabled": True
                },
                {
                    "name": "MIT Technology Review AI",
                    "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
                    "source_label": "MIT Tech Review",
                    "max_articles": 40,
                    "description": "MIT Technology Review's AI section",
                    "enabled": True
                },
                {
                    "name": "VentureBeat AI",
                    "url": "https://venturebeat.com/category/ai/feed/",
                    "source_label": "VentureBeat",
                    "max_articles": 40,
                    "description": "VentureBeat's AI category feed",
                    "enabled": True
                }
            ],
            "content_filters": {
                "keywords": self._get_default_keywords(),
                "date_range_days": 14,
                "min_content_length": 50
            },
            "fetching_config": {
                "concurrent_requests": True,
                "timeout_seconds": 30,
                "retry_attempts": 3,
                "user_agent": "AI-Parrot Podcast Generator/1.0"
            }
        }
    
    def _get_default_keywords(self) -> List[str]:
        """Get default content filtering keywords.
        
        Returns:
            List of default keywords.
        """
        return [
            "AI", "Artificial Intelligence", "Machine Learning", "Deep Learning", 
            "LLM", "GPT", "Large Language Model", "ChatGPT", "ChatGPT-4", 
            "Mistral", "MistralAI", "Llama", "Ollama", "OpenAI", "Anthropic", 
            "Claude", "AI Ethics", "AI Policy", "AI Regulation", "AI Governance"
        ]


# Global configuration loader instance
_config_loader = None

def get_config_loader() -> ConfigLoader:
    """Get the global configuration loader instance.
    
    Returns:
        ConfigLoader instance.
        
    🔍 Pattern: Singleton Pattern
    Ensures single configuration loader instance across the application.
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader
