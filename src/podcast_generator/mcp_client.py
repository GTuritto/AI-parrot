"""MCP (Model Context Protocol) client for article fetching and resource management.

This module provides a client interface to interact with MCP servers for
fetching articles and other resources dynamically.

🎓 Learning Objectives:
- Understand MCP (Model Context Protocol) integration patterns
- Learn resource discovery and dynamic content fetching
- Implement resilient client-server communication
- Practice async/await patterns with external services

🔍 Pattern Analysis:
This implements the Client-Server pattern with MCP protocol:
- Client: This MCP client that requests resources
- Server: External MCP server providing article resources
- Protocol: Standardized MCP communication format
- Resources: Dynamic content sources (articles, feeds, etc.)

💡 Real-world Applications:
- News aggregation systems
- Content management platforms  
- API gateway implementations
- Microservices communication
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import aiohttp
from dataclasses import dataclass

# Configure logging for MCP operations
logger = logging.getLogger(__name__)


@dataclass
class MCPResource:
    """Represents an MCP resource with metadata.
    
    🎓 Learning Note: Dataclasses provide a clean way to define
    data structures with automatic __init__, __repr__, etc.
    """
    uri: str
    name: str
    description: str
    mime_type: str
    metadata: Dict[str, Any]


@dataclass
class MCPArticle:
    """Represents an article fetched via MCP.
    
    This standardizes article data regardless of the source.
    """
    title: str
    link: str
    description: str
    published: datetime
    source: str
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MCPClient:
    """MCP client for fetching articles and managing resources.
    
    🔍 Pattern: Client-Server with Multiple Transport Support
    
    This client implements:
    1. Resource discovery from MCP servers
    2. Multiple transport protocols (HTTP, SSE)
    3. Dynamic content fetching
    4. Error handling and retries
    5. Caching for performance
    
    🧪 Experiment: Try switching between HTTP and SSE transports
    to see how they affect performance and real-time capabilities.
    """
    
    def __init__(self, server_configs: List[Dict[str, Any]], timeout: int = 30, prefer_sse: bool = True):
        """Initialize MCP client with server configurations.
        
        Args:
            server_configs: List of server configuration dictionaries
            timeout: Request timeout in seconds
            prefer_sse: Whether to prefer SSE transport over HTTP when available
            
        🎓 Learning Note: The client can connect to multiple MCP servers
        with different transport protocols for optimal performance.
        """
        self.server_configs = server_configs
        self.timeout = timeout
        self.prefer_sse = prefer_sse
        self.session: Optional[aiohttp.ClientSession] = None
        self.resources_cache: Dict[str, List[MCPResource]] = {}
        self.cache_ttl = timedelta(minutes=15)  # Cache resources for 15 minutes
        self.last_cache_update: Dict[str, datetime] = {}
        
        # Process server configs to determine best transport method
        self._process_server_configs()
        
        logger.info(f"Initialized MCP client with {len(server_configs)} servers")
    
    def _process_server_configs(self):
        """Process server configurations to determine optimal transport methods.
        
        🔍 Pattern: Transport Selection Strategy
        This method analyzes available transports and selects the best one.
        """
        for config in self.server_configs:
            # Determine the best transport URL to use
            http_url = config.get('base_url')  # HTTP transport
            sse_url = config.get('sse_url')    # SSE transport
            
            if self.prefer_sse and sse_url:
                config['active_url'] = sse_url
                config['transport'] = 'sse'
                logger.info(f"Using SSE transport for {config['name']}: {sse_url}")
            elif http_url:
                config['active_url'] = http_url
                config['transport'] = 'http'
                logger.info(f"Using HTTP transport for {config['name']}: {http_url}")
            else:
                logger.warning(f"No valid transport URL found for server {config['name']}")
                config['active_url'] = None
                config['transport'] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def discover_resources(self, server_name: str) -> List[MCPResource]:
        """Discover available resources from an MCP server.
        
        Args:
            server_name: Name of the server to query
            
        Returns:
            List of available MCP resources
            
        🎓 Learning Objective: Understand how resource discovery
        enables dynamic content sourcing without hardcoded endpoints.
        """
        # Check cache first
        if self._is_cache_valid(server_name):
            logger.info(f"Using cached resources for {server_name}")
            return self.resources_cache[server_name]
        
        server_config = self._get_server_config(server_name)
        if not server_config or not server_config.get('active_url'):
            logger.error(f"Server configuration not found or no active URL: {server_name}")
            return []
        
        try:
            # Use the active URL (either HTTP or SSE endpoint)
            base_url = server_config['active_url']
            url = f"{base_url}/resources" if not base_url.endswith('/resources') else base_url
            headers = self._get_headers(server_config)
            
            logger.debug(f"Discovering resources from {server_name} using {server_config['transport']} transport: {url}")
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    # Handle different response types based on transport
                    if server_config['transport'] == 'sse':
                        # Parse SSE response
                        data = await self._parse_sse_response(response)
                    else:
                        # Parse JSON response
                        data = await response.json()
                    
                    if data and 'resources' in data:
                        resources = [
                            MCPResource(
                                uri=resource['uri'],
                                name=resource['name'],
                                description=resource.get('description', ''),
                                mime_type=resource.get('mimeType', 'text/plain'),
                                metadata=resource.get('metadata', {})
                            )
                            for resource in data.get('resources', [])
                        ]
                        
                        # Update cache
                        self.resources_cache[server_name] = resources
                        self.last_cache_update[server_name] = datetime.now()
                        
                        logger.info(f"Discovered {len(resources)} resources from {server_name}")
                        return resources
                    else:
                        logger.warning(f"No resources found in response from {server_name}")
                        return []
                else:
                    logger.error(f"Failed to discover resources from {server_name}: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error discovering resources from {server_name}: {e}")
            return []
    
    async def fetch_resource_content(self, server_name: str, resource_uri: str) -> Optional[str]:
        """Fetch content from a specific MCP resource.
        
        Args:
            server_name: Name of the server
            resource_uri: URI of the resource to fetch
            
        Returns:
            Resource content as string, or None if failed
            
        🔍 Pattern Analysis: This implements the Request-Response pattern
        with proper error handling and logging.
        """
        server_config = self._get_server_config(server_name)
        if not server_config or not server_config.get('active_url'):
            logger.error(f"Server configuration not found or no active URL: {server_name}")
            return None
        
        try:
            # Use the active URL for resource fetching
            base_url = server_config['active_url']
            url = f"{base_url}/resources/{resource_uri}"
            headers = self._get_headers(server_config)
            
            logger.debug(f"Fetching resource {resource_uri} from {server_name} using {server_config['transport']} transport")
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    # Handle different response types based on transport
                    if server_config['transport'] == 'sse':
                        # Parse SSE response and extract content
                        data = await self._parse_sse_response(response)
                        if data and 'content' in data:
                            content = data['content']
                        else:
                            content = await response.text()
                    else:
                        content = await response.text()
                    
                    logger.info(f"Successfully fetched resource {resource_uri} from {server_name}")
                    return content
                else:
                    logger.error(f"Failed to fetch resource {resource_uri}: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching resource {resource_uri} from {server_name}: {e}")
            return None
    
    async def fetch_articles_from_mcp(self, max_articles: int = 50) -> List[MCPArticle]:
        """Fetch articles from all configured MCP servers.
        
        Args:
            max_articles: Maximum number of articles to fetch
            
        Returns:
            List of articles from MCP sources
            
        🎓 Learning Objective: See how to aggregate content from
        multiple sources and handle concurrent operations.
        """
        all_articles = []
        
        # Fetch from all servers concurrently
        tasks = []
        for server_config in self.server_configs:
            server_name = server_config['name']
            task = self._fetch_articles_from_server(server_name, max_articles // len(self.server_configs))
            tasks.append(task)
        
        # Wait for all servers to respond
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Error fetching from server: {result}")
        
        # Sort by publication date (newest first) and limit
        all_articles.sort(key=lambda x: x.published, reverse=True)
        return all_articles[:max_articles]
    
    async def _fetch_articles_from_server(self, server_name: str, max_articles: int) -> List[MCPArticle]:
        """Fetch articles from a specific MCP server.
        
        Args:
            server_name: Name of the server
            max_articles: Maximum articles to fetch from this server
            
        Returns:
            List of articles from the server
        """
        articles = []
        
        try:
            # Discover resources
            resources = await self.discover_resources(server_name)
            
            # Filter for article-related resources
            article_resources = [
                r for r in resources 
                if 'article' in r.name.lower() or 'news' in r.name.lower() or 'feed' in r.name.lower()
            ]
            
            logger.info(f"Found {len(article_resources)} article resources on {server_name}")
            
            # Fetch content from article resources
            for resource in article_resources[:5]:  # Limit to 5 resources per server
                content = await self.fetch_resource_content(server_name, resource.uri)
                if content:
                    parsed_articles = self._parse_article_content(content, server_name, resource)
                    articles.extend(parsed_articles)
                    
                    if len(articles) >= max_articles:
                        break
            
        except Exception as e:
            logger.error(f"Error fetching articles from {server_name}: {e}")
        
        return articles[:max_articles]
    
    def _parse_article_content(self, content: str, server_name: str, resource: MCPResource) -> List[MCPArticle]:
        """Parse article content from MCP resource.
        
        Args:
            content: Raw content from MCP resource
            server_name: Name of the source server
            resource: MCP resource metadata
            
        Returns:
            List of parsed articles
            
        🔍 Pattern: Content Parser with Multiple Format Support
        This method handles different content formats (JSON, RSS, etc.)
        """
        articles = []
        
        try:
            # Try parsing as JSON first
            if resource.mime_type == 'application/json' or content.strip().startswith('{'):
                data = json.loads(content)
                
                # Handle different JSON structures
                if 'articles' in data:
                    articles_data = data['articles']
                elif 'items' in data:
                    articles_data = data['items']
                elif isinstance(data, list):
                    articles_data = data
                else:
                    articles_data = [data]
                
                for article_data in articles_data:
                    article = self._create_article_from_json(article_data, server_name)
                    if article:
                        articles.append(article)
            
            # Handle RSS/XML content
            elif 'xml' in resource.mime_type or content.strip().startswith('<'):
                articles = self._parse_rss_content(content, server_name)
            
            # Handle plain text (assume it's a single article)
            else:
                article = MCPArticle(
                    title=resource.name,
                    link=resource.uri,
                    description=content[:200] + "..." if len(content) > 200 else content,
                    published=datetime.now(),
                    source=server_name,
                    content=content,
                    metadata=resource.metadata
                )
                articles.append(article)
                
        except Exception as e:
            logger.error(f"Error parsing content from {resource.uri}: {e}")
        
        return articles
    
    def _create_article_from_json(self, data: Dict[str, Any], server_name: str) -> Optional[MCPArticle]:
        """Create MCPArticle from JSON data.
        
        🎓 Learning Note: This method demonstrates flexible data mapping
        to handle different JSON schemas from various sources.
        """
        try:
            # Handle different field names that might be used
            title = data.get('title') or data.get('headline') or data.get('name', 'Untitled')
            link = data.get('link') or data.get('url') or data.get('uri', '')
            description = data.get('description') or data.get('summary') or data.get('excerpt', '')
            
            # Parse publication date
            published_str = data.get('published') or data.get('publishedAt') or data.get('date')
            if published_str:
                try:
                    published = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
                except:
                    published = datetime.now()
            else:
                published = datetime.now()
            
            return MCPArticle(
                title=title,
                link=link,
                description=description,
                published=published,
                source=server_name,
                content=data.get('content'),
                metadata=data
            )
            
        except Exception as e:
            logger.error(f"Error creating article from JSON: {e}")
            return None
    
    def _parse_rss_content(self, content: str, server_name: str) -> List[MCPArticle]:
        """Parse RSS/XML content into articles.
        
        🎓 Learning Note: This shows how to handle legacy formats
        while maintaining a modern interface.
        """
        articles = []
        try:
            import feedparser
            feed = feedparser.parse(content)
            
            for entry in feed.entries:
                published = datetime.now()
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                
                article = MCPArticle(
                    title=entry.get('title', 'Untitled'),
                    link=entry.get('link', ''),
                    description=entry.get('summary', ''),
                    published=published,
                    source=server_name,
                    metadata={'entry': entry}
                )
                articles.append(article)
                
        except Exception as e:
            logger.error(f"Error parsing RSS content: {e}")
        
        return articles
    
    def _get_server_config(self, server_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific server."""
        for config in self.server_configs:
            if config['name'] == server_name:
                return config
        return None
    
    def _get_headers(self, server_config: Dict[str, str]) -> Dict[str, str]:
        """Get HTTP headers for server requests."""
        transport = server_config.get('transport', 'http')
        
        if transport == 'sse':
            # SSE transport requires specific headers
            headers = {
                'Accept': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
        else:
            # HTTP transport uses JSON
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        
        # Add authentication if configured
        if 'api_key' in server_config:
            headers['Authorization'] = f"Bearer {server_config['api_key']}"
        elif 'auth_header' in server_config:
            headers.update(server_config['auth_header'])
        
        return headers
    
    def _is_cache_valid(self, server_name: str) -> bool:
        """Check if cached resources are still valid."""
        if server_name not in self.resources_cache:
            return False
        
        last_update = self.last_cache_update.get(server_name)
        if not last_update:
            return False
        
        return datetime.now() - last_update < self.cache_ttl
    
    async def _parse_sse_response(self, response) -> Optional[Dict[str, Any]]:
        """Parse Server-Sent Events response.
        
        🔍 Pattern: SSE Response Parser
        This method handles the SSE protocol for real-time communication.
        """
        try:
            content = await response.text()
            logger.debug(f"SSE Response content: {content[:200]}...")
            
            # Parse SSE format: data: {...}
            lines = content.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('data: '):
                    json_data = line[6:]  # Remove 'data: ' prefix
                    try:
                        return json.loads(json_data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse SSE JSON data: {e}")
                        continue
            
            logger.warning("No valid JSON data found in SSE response")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing SSE response: {e}")
            return None


# 🧪 Hands-on Exercise:
# Try creating your own MCP server configuration and test the client:
#
# server_configs = [
#     {
#         'name': 'my-news-server',
#         'base_url': 'http://localhost:8080',
#         'api_key': 'your-api-key'
#     }
# ]
#
# async with MCPClient(server_configs) as client:
#     articles = await client.fetch_articles_from_mcp()
#     print(f"Fetched {len(articles)} articles")
