from datetime import datetime, timedelta, timezone

from podcast_generator.article_fetcher import _remove_duplicates, is_within_date_range
from podcast_generator.mcp_client import MCPClient, MCPResource


def test_rss_date_filter_accepts_recent_articles_and_rejects_old_ones():
    now = datetime.now(timezone.utc)

    assert is_within_date_range(now - timedelta(hours=1), days=1)
    assert not is_within_date_range(now - timedelta(days=3), days=1)


def test_rss_deduplication_keeps_more_detailed_duplicate():
    articles = [
        {
            "title": "AI Agents in Production",
            "link": "https://example.com/post",
            "description": "short",
            "content": "",
        },
        {
            "title": " AI Agents in Production ",
            "link": "https://example.com/post",
            "description": "longer description",
            "content": "with additional context",
        },
    ]

    unique_articles = _remove_duplicates(articles)

    assert len(unique_articles) == 1
    assert unique_articles[0]["description"] == "longer description"


def test_mcp_client_parses_json_article_resources():
    client = MCPClient(server_configs=[])
    resource = MCPResource(
        uri="news://article/1",
        name="article",
        description="JSON article",
        mime_type="application/json",
        metadata={},
    )

    articles = client._parse_article_content(
        '{"title": "MCP for Agents", "description": "Context protocol", '
        '"url": "https://example.com/mcp"}',
        "test-server",
        resource,
    )

    assert len(articles) == 1
    assert articles[0].title == "MCP for Agents"
    assert articles[0].source == "test-server"
