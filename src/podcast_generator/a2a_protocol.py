"""Agent-to-Agent (A2A) Communication Protocol - Educational Implementation.

🎓 LEARNING OBJECTIVES:
This module demonstrates advanced AI Agent Patterns:
1. Agent-to-Agent Communication Pattern
2. Collaborative Intelligence Pattern
3. Consensus Building Algorithm
4. Peer Discovery and Network Formation
5. Quality Assessment Aggregation

🤝 COLLABORATIVE INTELLIGENCE CONCEPT:
Instead of relying on a single AI assessment, multiple agents collaborate
to reach consensus on content quality. This mimics how human teams
make better decisions through diverse perspectives and peer review.

🌐 NETWORK ARCHITECTURE:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Agent A   │◄──►│   Agent B   │◄──►│   Agent C   │
└─────────────┘    └─────────────┘    └─────────────┘
       ▲                   ▲                   ▲
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────┐
│           Consensus Building Engine                 │
│  • Aggregates individual assessments               │
│  • Weights opinions by agent confidence            │
│  • Resolves conflicts through averaging            │
│  • Produces final collaborative score              │
└─────────────────────────────────────────────────────┘

🔍 KEY ALGORITHMS:
1. Peer Discovery: Automatic detection of other agents
2. Quality Scoring: Individual agent assessment (0.0-1.0)
3. Confidence Weighting: Agents express certainty in their scores
4. Consensus Building: Weighted average of all agent opinions
5. Network Resilience: Graceful handling of agent failures

📚 EDUCATIONAL VALUE:
This implementation shows how distributed AI systems can achieve
better results through collaboration rather than competition,
demonstrating principles used in modern AI research and production systems.
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
from aiohttp import web


class MessageType(Enum):
    """Types of A2A messages."""
    QUALITY_REQUEST = "quality_request"
    QUALITY_RESPONSE = "quality_response"
    CONSENSUS_REQUEST = "consensus_request"
    CONSENSUS_RESPONSE = "consensus_response"
    AGENT_DISCOVERY = "agent_discovery"
    HEARTBEAT = "heartbeat"


@dataclass
class A2AMessage:
    """Standard A2A message format."""
    message_id: str
    sender_id: str
    receiver_id: str  # "*" for broadcast
    message_type: MessageType
    timestamp: str
    payload: Dict[str, Any]
    ttl: int = 300  # Time to live in seconds


@dataclass
class ArticleQualityScore:
    """Article quality assessment from an agent."""
    article_id: str
    agent_id: str
    relevance_score: float  # 0.0 to 1.0
    quality_score: float    # 0.0 to 1.0
    confidence: float       # 0.0 to 1.0
    reasoning: str
    timestamp: str


@dataclass
class AgentInfo:
    """Information about an A2A agent."""
    agent_id: str
    agent_type: str
    capabilities: List[str]
    endpoint: str
    last_seen: str
    status: str = "active"


class A2AQualityAgent:
    """A2A Agent for collaborative article quality assessment."""
    
    def __init__(
        self, 
        agent_id: str = None,
        listen_port: int = 8080,
        known_agents: List[str] = None
    ):
        """Initialize the A2A Quality Agent.
        
        Args:
            agent_id: Unique identifier for this agent.
            listen_port: Port to listen for A2A messages.
            known_agents: List of known agent endpoints.
        """
        self.agent_id = agent_id or f"podcast-agent-{uuid.uuid4().hex[:8]}"
        self.listen_port = listen_port
        self.known_agents = known_agents or []
        self.discovered_agents: Dict[str, AgentInfo] = {}
        self.quality_scores: Dict[str, List[ArticleQualityScore]] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.server = None
        
    async def start(self):
        """Start the A2A agent."""
        self.session = aiohttp.ClientSession()
        await self.start_server()
        await self.discover_agents()
        print(f"A2A Quality Agent {self.agent_id} started on port {self.listen_port}")
        
    async def stop(self):
        """Stop the A2A agent."""
        if self.server:
            await self.server.cleanup()
        if self.session:
            await self.session.close()
            
    async def start_server(self):
        """Start HTTP server to receive A2A messages."""
        app = web.Application()
        app.router.add_post('/a2a/message', self.handle_message)
        app.router.add_get('/a2a/status', self.handle_status)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.listen_port)
        await site.start()
        self.server = runner
        
    async def handle_message(self, request):
        """Handle incoming A2A messages."""
        try:
            data = await request.json()
            message = A2AMessage(**data)
            
            # Check TTL
            msg_time = datetime.fromisoformat(message.timestamp)
            if datetime.now() - msg_time > timedelta(seconds=message.ttl):
                return web.Response(status=410, text="Message expired")
                
            # Route message based on type
            if message.message_type == MessageType.QUALITY_REQUEST:
                await self.handle_quality_request(message)
            elif message.message_type == MessageType.QUALITY_RESPONSE:
                await self.handle_quality_response(message)
            elif message.message_type == MessageType.CONSENSUS_REQUEST:
                await self.handle_consensus_request(message)
            elif message.message_type == MessageType.AGENT_DISCOVERY:
                await self.handle_agent_discovery(message)
                
            return web.Response(status=200, text="Message processed")
            
        except Exception as e:
            print(f"Error handling A2A message: {e}")
            return web.Response(status=400, text=str(e))
            
    async def handle_status(self, request):
        """Handle status requests."""
        status = {
            "agent_id": self.agent_id,
            "agent_type": "podcast_quality_assessor",
            "capabilities": ["article_quality_assessment", "consensus_building"],
            "status": "active",
            "discovered_agents": len(self.discovered_agents),
            "processed_articles": len(self.quality_scores)
        }
        return web.json_response(status)
        
    async def discover_agents(self):
        """Discover other A2A agents."""
        discovery_message = A2AMessage(
            message_id=str(uuid.uuid4()),
            sender_id=self.agent_id,
            receiver_id="*",
            message_type=MessageType.AGENT_DISCOVERY,
            timestamp=datetime.now().isoformat(),
            payload={
                "agent_type": "podcast_quality_assessor",
                "capabilities": ["article_quality_assessment", "consensus_building"],
                "endpoint": f"http://localhost:{self.listen_port}"
            }
        )
        
        # Broadcast to known agents
        for agent_endpoint in self.known_agents:
            await self.send_message(discovery_message, agent_endpoint)
            
    async def send_message(self, message: A2AMessage, endpoint: str):
        """Send A2A message to another agent."""
        if not self.session:
            return False
            
        try:
            # Convert message to dict and handle enum serialization
            message_dict = asdict(message)
            message_dict['message_type'] = message.message_type.value
            
            async with self.session.post(
                f"{endpoint}/a2a/message",
                json=message_dict,
                headers={"Content-Type": "application/json"}
            ) as response:
                return response.status == 200
        except Exception as e:
            print(f"Error sending message to {endpoint}: {e}")
            return False
            
    async def assess_articles_collaboratively(
        self, 
        articles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Assess article quality collaboratively with other agents.
        
        Args:
            articles: List of articles to assess.
            
        Returns:
            Articles with collaborative quality scores.
        """
        print(f"Starting collaborative assessment of {len(articles)} articles...")
        
        # Step 1: Assess articles locally
        local_scores = []
        for article in articles:
            score = await self.assess_article_quality(article)
            local_scores.append(score)
            
        # Step 2: Request assessments from other agents
        if self.discovered_agents:
            await self.request_peer_assessments(articles)
            
            # Wait for responses (with timeout)
            await asyncio.sleep(5)  # Give agents time to respond
            
        # Step 3: Build consensus
        consensus_scores = await self.build_consensus(articles)
        
        # Step 4: Apply consensus scores to articles
        enhanced_articles = []
        for i, article in enumerate(articles):
            article_copy = article.copy()
            article_copy['a2a_quality_score'] = consensus_scores.get(
                article.get('title', ''), 
                local_scores[i].quality_score if i < len(local_scores) else 0.5
            )
            article_copy['a2a_consensus_confidence'] = consensus_scores.get(
                f"{article.get('title', '')}_confidence", 
                0.5
            )
            enhanced_articles.append(article_copy)
            
        print(f"Collaborative assessment complete. Enhanced {len(enhanced_articles)} articles.")
        return enhanced_articles
        
    async def assess_article_quality(self, article: Dict[str, Any]) -> ArticleQualityScore:
        """Assess quality of a single article using local AI."""
        # Simple heuristic-based assessment (can be enhanced with AI models)
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        
        # Relevance scoring based on keywords
        ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'llm', 'gpt', 'claude']
        relevance_score = sum(1 for keyword in ai_keywords if keyword in title or keyword in description)
        relevance_score = min(relevance_score / len(ai_keywords), 1.0)
        
        # Quality scoring based on content length and source
        quality_score = 0.5  # Base score
        if len(description) > 100:
            quality_score += 0.2
        if article.get('source') in ['MIT Tech Review', 'TechCrunch']:
            quality_score += 0.2
        quality_score = min(quality_score, 1.0)
        
        return ArticleQualityScore(
            article_id=article.get('title', ''),
            agent_id=self.agent_id,
            relevance_score=relevance_score,
            quality_score=quality_score,
            confidence=0.7,  # Medium confidence for heuristic assessment
            reasoning=f"Relevance: {relevance_score:.2f}, Quality: {quality_score:.2f}",
            timestamp=datetime.now().isoformat()
        )
        
    async def request_peer_assessments(self, articles: List[Dict[str, Any]]):
        """Request quality assessments from peer agents."""
        request_message = A2AMessage(
            message_id=str(uuid.uuid4()),
            sender_id=self.agent_id,
            receiver_id="*",
            message_type=MessageType.QUALITY_REQUEST,
            timestamp=datetime.now().isoformat(),
            payload={
                "articles": [
                    {
                        "title": article.get('title', ''),
                        "description": article.get('description', ''),
                        "source": article.get('source', '')
                    }
                    for article in articles[:5]  # Limit to 5 articles for efficiency
                ]
            }
        )
        
        # Send to all discovered agents
        for agent_info in self.discovered_agents.values():
            await self.send_message(request_message, agent_info.endpoint)
            
    async def build_consensus(self, articles: List[Dict[str, Any]]) -> Dict[str, float]:
        """Build consensus from multiple agent assessments."""
        consensus_scores = {}
        
        for article in articles:
            article_title = article.get('title', '')
            scores = self.quality_scores.get(article_title, [])
            
            if scores:
                # Weighted average based on confidence
                total_weight = sum(score.confidence for score in scores)
                if total_weight > 0:
                    weighted_quality = sum(
                        score.quality_score * score.confidence 
                        for score in scores
                    ) / total_weight
                    
                    weighted_relevance = sum(
                        score.relevance_score * score.confidence 
                        for score in scores
                    ) / total_weight
                    
                    # Combined score
                    consensus_scores[article_title] = (weighted_quality + weighted_relevance) / 2
                    consensus_scores[f"{article_title}_confidence"] = min(total_weight / len(scores), 1.0)
                    
        return consensus_scores
        
    async def handle_quality_request(self, message: A2AMessage):
        """Handle quality assessment requests from other agents."""
        articles = message.payload.get('articles', [])
        
        # Assess each article
        assessments = []
        for article in articles:
            score = await self.assess_article_quality(article)
            assessments.append(asdict(score))
            
        # Send response
        response_message = A2AMessage(
            message_id=str(uuid.uuid4()),
            sender_id=self.agent_id,
            receiver_id=message.sender_id,
            message_type=MessageType.QUALITY_RESPONSE,
            timestamp=datetime.now().isoformat(),
            payload={"assessments": assessments}
        )
        
        # Find sender's endpoint
        sender_info = self.discovered_agents.get(message.sender_id)
        if sender_info:
            await self.send_message(response_message, sender_info.endpoint)
            
    async def handle_quality_response(self, message: A2AMessage):
        """Handle quality assessment responses from other agents."""
        assessments = message.payload.get('assessments', [])
        
        for assessment_data in assessments:
            score = ArticleQualityScore(**assessment_data)
            
            if score.article_id not in self.quality_scores:
                self.quality_scores[score.article_id] = []
            self.quality_scores[score.article_id].append(score)
            
    async def handle_consensus_request(self, message: A2AMessage):
        """Handle consensus building requests."""
        # Implementation for consensus protocols
        pass
        
    async def handle_agent_discovery(self, message: A2AMessage):
        """Handle agent discovery messages."""
        agent_info = AgentInfo(
            agent_id=message.sender_id,
            agent_type=message.payload.get('agent_type', 'unknown'),
            capabilities=message.payload.get('capabilities', []),
            endpoint=message.payload.get('endpoint', ''),
            last_seen=datetime.now().isoformat()
        )
        
        self.discovered_agents[message.sender_id] = agent_info
        print(f"Discovered agent: {agent_info.agent_id} ({agent_info.agent_type})")


# Integration function for the podcast workflow
async def enhance_articles_with_a2a(
    articles: List[Dict[str, Any]], 
    agent_config: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
    """Enhance articles using A2A collaborative quality assessment.
    
    Args:
        articles: List of articles to enhance.
        agent_config: Configuration for the A2A agent.
        
    Returns:
        Enhanced articles with A2A quality scores.
    """
    if not agent_config:
        agent_config = {
            "listen_port": 8080,
            "known_agents": [
                "http://localhost:8081",
                "http://localhost:8082"
            ]
        }
        
    try:
        agent = A2AQualityAgent(**agent_config)
        await agent.start()
        
        # Perform collaborative assessment
        enhanced_articles = await agent.assess_articles_collaboratively(articles)
        
        await agent.stop()
        return enhanced_articles
        
    except Exception as e:
        print(f"A2A enhancement failed: {e}")
        print("Falling back to original articles...")
        return articles
