import asyncio

import pytest

from podcast_generator.a2a_protocol import A2AQualityAgent, ArticleQualityScore


def test_a2a_quality_assessment_scores_relevant_ai_articles_higher():
    async def scenario():
        agent = A2AQualityAgent(agent_id="local-test-agent")

        score = await agent.assess_article_quality(
            {
                "title": "New LLM research improves AI agents",
                "description": "A detailed machine learning article " * 8,
                "source": "MIT Tech Review",
            }
        )

        assert score.article_id == "New LLM research improves AI agents"
        assert score.agent_id == "local-test-agent"
        assert score.relevance_score > 0
        assert score.quality_score > 0.5
        assert 0 <= score.confidence <= 1

    asyncio.run(scenario())


def test_a2a_consensus_uses_confidence_weighted_scores():
    async def scenario():
        agent = A2AQualityAgent(agent_id="consensus-agent")
        article_title = "AI model evaluation"
        agent.quality_scores[article_title] = [
            ArticleQualityScore(
                article_id=article_title,
                agent_id="agent-a",
                relevance_score=1.0,
                quality_score=0.8,
                confidence=0.9,
                reasoning="strong match",
                timestamp="2026-01-01T00:00:00",
            ),
            ArticleQualityScore(
                article_id=article_title,
                agent_id="agent-b",
                relevance_score=0.2,
                quality_score=0.4,
                confidence=0.1,
                reasoning="weak match",
                timestamp="2026-01-01T00:00:00",
            ),
        ]

        consensus = await agent.build_consensus([{"title": article_title}])

        assert consensus[article_title] == pytest.approx(0.84)
        assert consensus[f"{article_title}_confidence"] == 0.5

    asyncio.run(scenario())
