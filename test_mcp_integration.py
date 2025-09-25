#!/usr/bin/env python3
"""Test script for MCP integration with the AI-Parrot podcast generator.

This script tests the MCP client functionality and article fetching
to ensure your MCP server is properly integrated.

🎓 Learning Objectives:
- Test MCP server connectivity
- Verify resource discovery functionality
- Validate article fetching pipeline
- Debug MCP integration issues

Usage:
    python test_mcp_integration.py
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

from podcast_generator.article_fetcher import (
    get_mcp_server_configs, 
    fetch_articles_from_mcp,
    fetch_multiple_sources
)
from podcast_generator.mcp_client import MCPClient
from utils.env import load_env_vars

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_mcp_server_connectivity():
    """Test basic connectivity to MCP servers."""
    print("🔍 Testing MCP Server Connectivity")
    print("=" * 50)
    
    configs = get_mcp_server_configs()
    
    if not configs:
        print("❌ No MCP servers configured!")
        print("\nTo configure your MCP server, add these to your .env file:")
        print("MCP_SERVER_URL=http://localhost:3000/mcp")
        print("MCP_SSE_URL=http://localhost:3000/sse")
        print("MCP_SERVER_NAME=local-mcp-server")
        return False
    
    print(f"✅ Found {len(configs)} MCP server(s) configured:")
    for config in configs:
        print(f"   - {config['name']}")
        if config.get('base_url'):
            print(f"     HTTP: {config['base_url']}")
        if config.get('sse_url'):
            print(f"     SSE:  {config['sse_url']}")
    
    # Test connectivity
    try:
        async with MCPClient(configs) as client:
            print("\n🔗 Testing server connections...")
            
            for config in configs:
                server_name = config['name']
                print(f"\n📡 Testing {server_name}...")
                
                try:
                    resources = await client.discover_resources(server_name)
                    if resources:
                        print(f"   ✅ Connected! Found {len(resources)} resources:")
                        for resource in resources[:3]:  # Show first 3
                            print(f"      - {resource.name}: {resource.description}")
                        if len(resources) > 3:
                            print(f"      ... and {len(resources) - 3} more")
                    else:
                        print(f"   ⚠️  Connected but no resources found")
                        
                except Exception as e:
                    print(f"   ❌ Connection failed: {e}")
                    return False
                    
    except Exception as e:
        print(f"❌ MCP client initialization failed: {e}")
        return False
    
    return True


async def test_article_fetching():
    """Test article fetching from MCP servers."""
    print("\n📰 Testing Article Fetching")
    print("=" * 50)
    
    try:
        # Test MCP-only fetching
        print("🔍 Testing MCP article fetching...")
        mcp_articles = await fetch_articles_from_mcp()
        
        if mcp_articles:
            print(f"✅ Successfully fetched {len(mcp_articles)} articles from MCP servers:")
            for i, article in enumerate(mcp_articles[:3], 1):
                print(f"   {i}. {article['title'][:60]}...")
                print(f"      Source: {article['source']}")
                print(f"      Published: {article['published']}")
            if len(mcp_articles) > 3:
                print(f"      ... and {len(mcp_articles) - 3} more articles")
        else:
            print("⚠️  No articles fetched from MCP servers")
        
        # Test hybrid fetching (MCP + RSS)
        print("\n🔍 Testing hybrid article fetching (MCP + RSS)...")
        all_articles = await fetch_multiple_sources()
        
        if all_articles:
            print(f"✅ Successfully fetched {len(all_articles)} total articles:")
            
            # Count by source type
            mcp_count = len([a for a in all_articles if a['source'].startswith('MCP-')])
            rss_count = len(all_articles) - mcp_count
            
            print(f"   - MCP articles: {mcp_count}")
            print(f"   - RSS articles: {rss_count}")
            
            print("\n📋 Sample articles:")
            for i, article in enumerate(all_articles[:5], 1):
                print(f"   {i}. {article['title'][:60]}...")
                print(f"      Source: {article['source']}")
                print(f"      Published: {article['published']}")
        else:
            print("❌ No articles fetched from any source!")
            return False
            
    except Exception as e:
        print(f"❌ Article fetching failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def test_resource_discovery():
    """Test detailed resource discovery."""
    print("\n🔍 Testing Resource Discovery")
    print("=" * 50)
    
    configs = get_mcp_server_configs()
    if not configs:
        print("❌ No MCP servers configured")
        return False
    
    try:
        async with MCPClient(configs) as client:
            for config in configs:
                server_name = config['name']
                print(f"\n📡 Discovering resources from {server_name}...")
                
                resources = await client.discover_resources(server_name)
                
                if resources:
                    print(f"✅ Found {len(resources)} resources:")
                    for resource in resources:
                        print(f"   📄 {resource.name}")
                        print(f"      URI: {resource.uri}")
                        print(f"      Type: {resource.mime_type}")
                        print(f"      Description: {resource.description}")
                        
                        # Test fetching content from first resource
                        if resource == resources[0]:
                            print(f"   🔍 Testing content fetch...")
                            content = await client.fetch_resource_content(server_name, resource.uri)
                            if content:
                                content_preview = content[:200] + "..." if len(content) > 200 else content
                                print(f"      ✅ Content preview: {content_preview}")
                            else:
                                print(f"      ⚠️  No content returned")
                        print()
                else:
                    print(f"⚠️  No resources found on {server_name}")
                    
    except Exception as e:
        print(f"❌ Resource discovery failed: {e}")
        return False
    
    return True


async def main():
    """Run all MCP integration tests."""
    print("🚀 AI-Parrot MCP Integration Test")
    print("=" * 50)
    
    # Load environment variables
    if not load_env_vars():
        print("❌ Could not load .env file")
        return
    
    print(f"📁 Project root: {project_root}")
    print(f"🔧 Environment loaded from: {project_root / '.env'}")
    
    # Run tests
    tests = [
        ("MCP Server Connectivity", test_mcp_server_connectivity),
        ("Resource Discovery", test_resource_discovery),
        ("Article Fetching", test_article_fetching),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 Running: {test_name}")
        print(f"{'='*60}")
        
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your MCP integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure your MCP server is running on localhost:3000")
        print("2. Check your .env file has the correct MCP_SERVER_URL and MCP_SSE_URL")
        print("3. Verify your MCP server is responding to /resources endpoint")


if __name__ == "__main__":
    asyncio.run(main())
