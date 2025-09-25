# 📰 RSS Feed Configuration Guide

## 🌟 **Overview**

The AI-Parrot system now uses a flexible, configuration-driven approach for managing RSS feeds. Instead of hardcoded feed URLs, all RSS sources are defined in a JSON configuration file that can be easily updated without touching the code.

## 📁 **Configuration Files**

### **Main Configuration File**
- **Location**: `config/rss_feeds.json`
- **Format**: JSON
- **Purpose**: Defines all RSS feeds, content filters, and fetching behavior

### **Configuration Structure**
```json
{
  "rss_feeds": [
    {
      "name": "TechCrunch AI",
      "url": "https://techcrunch.com/tag/artificial-intelligence/feed/",
      "source_label": "TechCrunch",
      "max_articles": 50,
      "description": "TechCrunch's artificial intelligence news",
      "enabled": true
    }
  ],
  "content_filters": {
    "keywords": ["AI", "Machine Learning", "..."],
    "date_range_days": 14,
    "min_content_length": 50
  },
  "fetching_config": {
    "concurrent_requests": true,
    "timeout_seconds": 30,
    "retry_attempts": 3,
    "user_agent": "AI-Parrot Podcast Generator/1.0"
  }
}
```

## 🛠️ **Managing RSS Feeds**

### **Using the Management CLI**

The system includes a command-line tool for managing RSS feeds:

```bash
# List all configured feeds
python manage_feeds.py list

# Add a new feed
python manage_feeds.py add "AI News" "https://example.com/ai/feed/"

# Enable/disable feeds
python manage_feeds.py enable "https://techcrunch.com/tag/artificial-intelligence/feed/"
python manage_feeds.py disable "https://venturebeat.com/category/ai/feed/"

# Test a feed URL
python manage_feeds.py test "https://www.technologyreview.com/topic/artificial-intelligence/feed/"

# Show current configuration
python manage_feeds.py config
```

### **Manual Configuration**

You can also edit the `config/rss_feeds.json` file directly:

#### **Adding a New Feed**
```json
{
  "name": "Your Feed Name",
  "url": "https://example.com/feed.xml",
  "source_label": "Example Source",
  "max_articles": 30,
  "description": "Description of the feed",
  "enabled": true
}
```

#### **Feed Properties**
- **`name`** (required): Human-readable name for the feed
- **`url`** (required): RSS/Atom feed URL
- **`source_label`** (required): Short label used in articles
- **`max_articles`** (optional): Maximum articles to fetch (default: 30)
- **`description`** (optional): Description of the feed
- **`enabled`** (optional): Whether the feed is active (default: true)

## 🔍 **Content Filtering**

### **Keywords**
Configure which keywords make articles "interesting":

```json
"content_filters": {
  "keywords": [
    "AI", "Artificial Intelligence", "Machine Learning", "Deep Learning",
    "LLM", "GPT", "Large Language Model", "ChatGPT", "Claude",
    "AI Ethics", "AI Policy", "AI Regulation", "Neural Network"
  ]
}
```

### **Date Range**
Control how recent articles must be:

```json
"content_filters": {
  "date_range_days": 14  // Only articles from last 14 days
}
```

### **Content Length**
Filter out very short articles:

```json
"content_filters": {
  "min_content_length": 50  // Minimum 50 characters
}
```

## ⚙️ **Fetching Configuration**

### **Performance Settings**
```json
"fetching_config": {
  "concurrent_requests": true,     // Fetch feeds in parallel
  "timeout_seconds": 30,           // Request timeout
  "retry_attempts": 3,             // Retry failed requests
  "user_agent": "AI-Parrot/1.0"   // HTTP User-Agent header
}
```

## 📊 **Default RSS Feeds**

The system comes pre-configured with these RSS feeds:

### **Enabled by Default**
1. **TechCrunch AI**
   - URL: `https://techcrunch.com/tag/artificial-intelligence/feed/`
   - Focus: AI startup news and industry developments

2. **MIT Technology Review AI**
   - URL: `https://www.technologyreview.com/topic/artificial-intelligence/feed/`
   - Focus: Academic and research-oriented AI news

3. **VentureBeat AI**
   - URL: `https://venturebeat.com/category/ai/feed/`
   - Focus: Business and enterprise AI news

### **Available but Disabled**
4. **Ars Technica Technology**
5. **The Verge AI**
6. **AI News**
7. **Wired AI**

## 🔄 **Hot Reloading**

The configuration system supports hot reloading:
- Changes to `config/rss_feeds.json` are automatically detected
- No need to restart the application
- Configuration is cached for performance but reloaded when file changes

## 🧪 **Testing New Feeds**

Before adding a feed permanently, test it:

```bash
# Test if a feed URL works
python manage_feeds.py test "https://example.com/feed.xml"
```

This will:
- Fetch a few sample articles
- Show article titles and metadata
- Verify the feed format is compatible

## 🔧 **Advanced Configuration**

### **Environment Variables**
You can override the configuration file location:

```bash
export RSS_CONFIG_FILE="/path/to/custom/config.json"
```

### **Multiple Configuration Files**
For different environments:

```bash
# Development
python manage_feeds.py --config config/rss_feeds_dev.json list

# Production
python manage_feeds.py --config config/rss_feeds_prod.json list
```

### **Programmatic Access**
Use the configuration loader in your own code:

```python
from podcast_generator.config_loader import get_config_loader

config_loader = get_config_loader()
enabled_feeds = config_loader.get_enabled_feeds()
filter_config = config_loader.get_content_filter_config()
```

## 🚀 **Benefits of Configuration-Driven Approach**

### **✅ Advantages**
- **No Code Changes**: Add/remove feeds without touching Python code
- **Dynamic Control**: Enable/disable feeds based on quality or relevance
- **Easy Maintenance**: Non-technical users can manage feed lists
- **Testing**: Test new feeds before adding them permanently
- **Backup/Restore**: Configuration files can be version controlled
- **Environment-Specific**: Different configs for dev/staging/production

### **🎯 Use Cases**
- **Content Curation**: Quickly adjust content sources based on quality
- **A/B Testing**: Test different feed combinations
- **Seasonal Adjustments**: Add temporary feeds for events or topics
- **Quality Control**: Disable feeds that provide low-quality content
- **Scaling**: Easily add new content sources as they become available

## 📝 **Configuration Examples**

### **Minimal Configuration**
```json
{
  "rss_feeds": [
    {
      "name": "TechCrunch AI",
      "url": "https://techcrunch.com/tag/artificial-intelligence/feed/",
      "source_label": "TechCrunch"
    }
  ]
}
```

### **Full Configuration with All Options**
```json
{
  "rss_feeds": [
    {
      "name": "TechCrunch AI",
      "url": "https://techcrunch.com/tag/artificial-intelligence/feed/",
      "source_label": "TechCrunch",
      "max_articles": 50,
      "description": "TechCrunch's artificial intelligence news and articles",
      "enabled": true
    }
  ],
  "content_filters": {
    "keywords": [
      "AI", "Artificial Intelligence", "Machine Learning", "Deep Learning",
      "LLM", "GPT", "Large Language Model", "ChatGPT", "Claude",
      "Neural Network", "Transformer", "Computer Vision", "NLP"
    ],
    "date_range_days": 14,
    "min_content_length": 50
  },
  "fetching_config": {
    "concurrent_requests": true,
    "timeout_seconds": 30,
    "retry_attempts": 3,
    "user_agent": "AI-Parrot Podcast Generator/1.0"
  }
}
```

---

**🎯 The configuration-driven RSS system makes AI-Parrot highly flexible and maintainable, allowing you to adapt content sources without any code changes!**
