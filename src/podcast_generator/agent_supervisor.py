"""AI Agent Supervisor Pattern Implementation - Educational Version.

🎓 LEARNING OBJECTIVES:
This module demonstrates several key AI Agent Patterns:
1. Hierarchical Coordination Pattern (Supervisor-Worker)
2. Specialized Agent Pattern (Domain-specific agents)
3. Observer Pattern (Task monitoring and notifications)
4. Task Queue Management Pattern
5. Agent Lifecycle Management Pattern

🏗️ ARCHITECTURE OVERVIEW:
The Supervisor Agent acts as a central coordinator that:
- Manages a pool of specialized worker agents
- Distributes tasks based on agent capabilities
- Monitors task execution and agent health
- Implements observer pattern for real-time notifications
- Handles failures and provides system resilience

🤖 AGENT TYPES:
- ContentFetcherAgent: Retrieves articles from various sources
- QualityAssessorAgent: Performs A2A collaborative quality assessment
- ContentProcessorAgent: Handles AI summarization and script generation
- AudioGeneratorAgent: Manages text-to-speech audio production

📚 EDUCATIONAL VALUE:
This implementation serves as a practical example of how enterprise-grade
multi-agent systems coordinate complex workflows while maintaining
scalability, reliability, and observability.
"""
import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Status of agent tasks."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentType(Enum):
    """Enumeration of available agent types.
    
    🎓 PATTERN: Specialized Agent Pattern
    Each enum value represents a different domain of expertise,
    demonstrating how complex systems can be broken down into
    specialized, focused components.
    
    🔍 DESIGN PRINCIPLE:
    - Single Responsibility: Each agent type has one clear purpose
    - Separation of Concerns: Different aspects handled by different agents
    - Extensibility: New agent types can be easily added
    """
    CONTENT_FETCHER = "content_fetcher"      # 📰 Handles article retrieval and processing
    QUALITY_ASSESSOR = "quality_assessor"    # 🎯 Manages A2A collaborative assessment
    CONTENT_PROCESSOR = "content_processor"  # 🤖 Performs AI summarization and script generation
    AUDIO_GENERATOR = "audio_generator"      # 🎵 Handles text-to-speech audio production
    TRANSLATOR = "translator"


@dataclass
class Task:
    """Represents a task to be executed by an agent.
    
    🎓 PATTERN: Task Object Pattern
    This class encapsulates all information needed to execute a task,
    demonstrating how to design self-contained work units in distributed systems.
    
    🔍 DESIGN PRINCIPLES:
    - Immutable Identity: task_id uniquely identifies each task
    - State Tracking: status field enables monitoring and debugging
    - Priority Queuing: priority field enables task scheduling
    - Error Handling: error field captures failure information
    - Timestamping: created_at enables performance analysis
    
    📊 LIFECYCLE STATES:
    - pending: Task created but not yet started
    - running: Task currently being executed
    - completed: Task finished successfully
    - failed: Task encountered an error
    """
    task_id: str                                    # 🆔 Unique identifier for the task
    agent_type: AgentType
    task_name: str                                  # 📝 Type of task to be performed
    payload: Dict[str, Any]                         # 📦 Data and parameters for the task
    priority: int = 1                               # ⭐ Priority level (higher = more urgent)
    created_at: datetime = field(default_factory=datetime.now)  # ⏰ Task creation timestamp
    status: str = "pending"                         # 📊 Current execution status
    result: Optional[Any] = None                    # ✅ Task execution result
    error: Optional[str] = None                     # ❌ Error message if task failed
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class AgentCapability:
    """Defines what an agent can do."""
    agent_type: AgentType
    capabilities: List[str]
    max_concurrent_tasks: int = 1
    average_execution_time: float = 30.0  # seconds
    reliability_score: float = 0.95  # 0.0 to 1.0


class SpecializedAgent:
    """Base class for specialized agents.
    
    🎓 PATTERN: Specialized Agent Pattern + Template Method Pattern
    This abstract base class defines the common interface and behavior
    for all specialized agents while allowing each agent to implement
    its own specific task handling logic.
    
    🔍 KEY DESIGN PATTERNS:
    1. Template Method: execute_task() defines the algorithm structure
    2. Strategy Pattern: _handle_task() allows different implementations
    3. State Management: Tracks agent status and task history
    4. Error Handling: Comprehensive exception management
    
    🏗️ AGENT LIFECYCLE:
    1. Initialization: Agent created with unique ID and type
    2. Task Assignment: Tasks added to agent's queue
    3. Task Execution: Agent processes tasks using template method
    4. State Updates: Agent status updated throughout lifecycle
    5. Completion: Results stored and agent marked as available
    
    📊 MONITORING CAPABILITIES:
    - Real-time status tracking (busy/available)
    - Task history maintenance
    - Health status monitoring
    - Performance metrics collection
    """
    
    def __init__(self, agent_type: AgentType, agent_id: str = None):
        """Initialize a specialized agent.
        
        Args:
            agent_type: The type/specialization of this agent
            agent_id: Optional custom ID (auto-generated if not provided)
        """
        # 🆔 Generate unique agent identifier
        self.agent_id = agent_id or f"{agent_type.value}-{uuid.uuid4().hex[:8]}"
        
        # 🎭 Store agent specialization type
        self.agent_type = agent_type
        
        # 📋 Task management data structures
        self.current_tasks: Dict[str, Task] = {}    # Currently executing tasks
        self.completed_tasks: List[Task] = []       # Historical task record
        
        # 🔄 Agent state management
        self.is_busy = False                        # Current availability status
        self.health_status = "healthy"              # Health monitoring status
        
    async def execute_task(self, task: Task) -> Task:
        """Execute a task assigned to this agent.
        
        🎓 PATTERN: Template Method Pattern
        This method defines the standard algorithm for task execution
        while allowing specialized agents to implement their own
        specific task handling logic via the _handle_task() method.
        
        🔄 EXECUTION FLOW:
        1. Pre-execution: Update task status and agent state
        2. Execution: Delegate to specialized handler
        3. Success: Store results and update status
        4. Failure: Capture error information
        5. Cleanup: Reset agent state and record task history
        
        📊 MONITORING INTEGRATION:
        - Logs task start/completion for observability
        - Updates task timestamps for performance analysis
        - Maintains agent busy state for load balancing
        - Records task history for system analytics
        
        Args:
            task: The task to be executed
            
        Returns:
            Task: The completed task with results or error information
        """
        logger.info(f"🚀 Agent {self.agent_id} starting task {task.task_id}")
        
        # 📊 PHASE 1: Pre-execution setup
        task.status = TaskStatus.IN_PROGRESS.value
        task.started_at = datetime.now().isoformat()
        self.current_tasks[task.task_id] = task
        self.is_busy = True  # 🔒 Mark agent as busy
        
        try:
            # 🎯 PHASE 2: Task execution (Strategy Pattern)
            # Delegate to specialized implementation
            result = await self._handle_task(task)
            
            # ✅ PHASE 3: Success handling
            task.result = result
            task.status = TaskStatus.COMPLETED.value
            task.completed_at = datetime.now().isoformat()
            
            logger.info(f"✅ Agent {self.agent_id} completed task {task.task_id}")
            
        except Exception as e:
            # ❌ PHASE 4: Error handling
            task.error = str(e)
            task.status = TaskStatus.FAILED.value
            task.completed_at = datetime.now().isoformat()
            
            logger.error(f"❌ Agent {self.agent_id} failed task {task.task_id}: {e}")
        
        finally:
            # 🧹 PHASE 5: Cleanup and state management
            self.current_tasks.pop(task.task_id, None)  # Remove from active tasks
            self.completed_tasks.append(task)           # Add to history
            self.is_busy = False                        # 🔓 Mark agent as available
            
        return task
    
    async def _handle_task(self, task: Task) -> Any:
        """Override this method in specialized agents."""
        raise NotImplementedError("Specialized agents must implement _handle_task")
    
    def _handle_unknown_task(self, task: Task) -> Any:
        """Handle unknown task types."""
        raise ValueError(f"Unknown task '{task.task_name}' for agent type {self.agent_type.value}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "is_busy": self.is_busy,
            "health_status": self.health_status,
            "current_tasks": len(self.current_tasks),
            "completed_tasks": len(self.completed_tasks)
        }


# Specialized Agent Implementations
class ContentFetcherAgent(SpecializedAgent):
    """Specialized agent for content fetching."""
    
    def __init__(self):
        super().__init__(AgentType.CONTENT_FETCHER)
        
    async def _handle_task(self, task: Task) -> Any:
        """Handle content fetching tasks."""
        if task.task_name == "fetch_articles":
            from podcast_generator.article_fetcher import fetch_multiple_sources
            articles = await fetch_multiple_sources()
            return {"articles": articles, "count": len(articles)}
        
        return self._handle_unknown_task(task)


class QualityAssessorAgent(SpecializedAgent):
    """Specialized agent for quality assessment."""
    
    def __init__(self):
        super().__init__(AgentType.QUALITY_ASSESSOR)
        
    async def _handle_task(self, task: Task) -> Any:
        """Handle quality assessment tasks."""
        if task.task_name == "assess_quality":
            from podcast_generator.a2a_protocol import enhance_articles_with_a2a
            articles = task.payload.get("articles", [])
            a2a_config = task.payload.get("a2a_config", {})
            enhanced_articles = await enhance_articles_with_a2a(articles, a2a_config)
            return {"enhanced_articles": enhanced_articles}
        
        return self._handle_unknown_task(task)


class ContentProcessorAgent(SpecializedAgent):
    """Specialized agent for content processing."""
    
    def __init__(self):
        super().__init__(AgentType.CONTENT_PROCESSOR)
        self._processor = None  # Lazy initialization
        
    def _get_processor(self):
        """Get or create AI processor instance."""
        if self._processor is None:
            from podcast_generator.ai_processor import AIProcessor
            self._processor = AIProcessor()
        return self._processor
        
    async def _handle_task(self, task: Task) -> Any:
        """Handle content processing tasks."""
        processor = self._get_processor()
        
        if task.task_name == "summarize_articles":
            articles = task.payload.get("articles", [])
            summaries = []
            for article in articles:
                summary = processor.summarize_article(article)
                article_summary = article.copy()
                article_summary["summary"] = summary
                summaries.append(article_summary)
            return {"summaries": summaries}
            
        elif task.task_name == "generate_script":
            summaries = task.payload.get("summaries", [])
            voice_name = task.payload.get("voice_name", "Aria")
            script = processor.generate_podcast_script(summaries, voice_name)
            return {"script": script}
        
        return self._handle_unknown_task(task)


class AudioGeneratorAgent(SpecializedAgent):
    """Specialized agent for audio generation."""
    
    def __init__(self):
        super().__init__(AgentType.AUDIO_GENERATOR)
        self._file_manager = None  # Lazy initialization
        
    def _get_file_manager(self):
        """Get or create file manager instance."""
        if self._file_manager is None:
            from podcast_generator.file_utils import FileManager
            self._file_manager = FileManager()
        return self._file_manager
        
    async def _handle_task(self, task: Task) -> Any:
        """Handle audio generation tasks."""
        if task.task_name == "generate_audio":
            file_manager = self._get_file_manager()
            
            script = task.payload.get("script", "")
            voice_name = task.payload.get("voice_name", "Aria")
            language = task.payload.get("language", "en")
            
            mp3_path = await file_manager.save_mp3_file(
                text_content=script,
                voice_name=voice_name,
                language=language,
                add_intro_outro=True
            )
            
            return {"audio_path": mp3_path}
        
        return self._handle_unknown_task(task)


class AgentSupervisor:
    """Supervisor agent that coordinates specialized worker agents."""
    
    def __init__(self):
        self.supervisor_id = f"supervisor-{uuid.uuid4().hex[:8]}"
        self.agents: Dict[AgentType, SpecializedAgent] = {}
        self.task_queue: List[Task] = []
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: List[Task] = []
        self.observers: List[Callable] = []
        
        # Initialize specialized agents
        self._initialize_agents()
        
    def _initialize_agents(self):
        """Initialize all specialized agents."""
        self.agents[AgentType.CONTENT_FETCHER] = ContentFetcherAgent()
        self.agents[AgentType.QUALITY_ASSESSOR] = QualityAssessorAgent()
        self.agents[AgentType.CONTENT_PROCESSOR] = ContentProcessorAgent()
        self.agents[AgentType.AUDIO_GENERATOR] = AudioGeneratorAgent()
        
        logger.info(f"Supervisor {self.supervisor_id} initialized with {len(self.agents)} agents")
    
    def add_observer(self, observer: Callable):
        """Add observer for task events (Observer Pattern)."""
        self.observers.append(observer)
    
    def _notify_observers(self, event: str, task: Task):
        """Notify all observers of task events."""
        for observer in self.observers:
            try:
                observer(event, task)
            except Exception as e:
                logger.error(f"Observer notification failed: {e}")
    
    async def submit_task(self, agent_type: AgentType, task_name: str, payload: Dict[str, Any], priority: int = 1) -> str:
        """Submit a task to be executed by a specialized agent."""
        task = Task(
            task_id=str(uuid.uuid4()),
            agent_type=agent_type,
            task_name=task_name,
            payload=payload,
            priority=priority
        )
        
        # Add to queue (sorted by priority)
        self.task_queue.append(task)
        self.task_queue.sort(key=lambda t: t.priority)
        
        logger.info(f"Task {task.task_id} submitted to queue for {agent_type.value}")
        self._notify_observers("task_submitted", task)
        
        return task.task_id
    
    async def execute_task(self, task_id: str) -> Task:
        """Execute a specific task."""
        # Find task in queue
        task = None
        for i, t in enumerate(self.task_queue):
            if t.task_id == task_id:
                task = self.task_queue.pop(i)
                break
        
        if not task:
            raise ValueError(f"Task {task_id} not found in queue")
        
        # Get appropriate agent
        agent = self.agents.get(task.agent_type)
        if not agent:
            raise ValueError(f"No agent available for type {task.agent_type}")
        
        # Execute task
        self.active_tasks[task_id] = task
        self._notify_observers("task_started", task)
        
        try:
            completed_task = await agent.execute_task(task)
            self.completed_tasks.append(completed_task)
            self._notify_observers("task_completed", completed_task)
            return completed_task
        finally:
            self.active_tasks.pop(task_id, None)
    
    async def execute_workflow(self, language: str = "en", voice_name: str = "Aria", enable_a2a: bool = True) -> Dict[str, Any]:
        """Execute the complete podcast generation workflow using specialized agents."""
        logger.info(f"Starting workflow execution with supervisor {self.supervisor_id}")
        
        try:
            # Step 1: Fetch articles
            fetch_task_id = await self.submit_task(
                AgentType.CONTENT_FETCHER,
                "fetch_articles",
                {},
                priority=1
            )
            fetch_result = await self.execute_task(fetch_task_id)
            articles = fetch_result.result["articles"]
            
            # Step 2: Quality assessment (if enabled)
            if enable_a2a:
                assess_task_id = await self.submit_task(
                    AgentType.QUALITY_ASSESSOR,
                    "assess_quality",
                    {
                        "articles": articles,
                        "a2a_config": {"listen_port": 8080, "known_agents": []}
                    },
                    priority=1
                )
                assess_result = await self.execute_task(assess_task_id)
                articles = assess_result.result["enhanced_articles"]
            
            # Step 3: Summarize articles
            summarize_task_id = await self.submit_task(
                AgentType.CONTENT_PROCESSOR,
                "summarize_articles",
                {"articles": articles[:7]},  # Limit to 7 articles
                priority=1
            )
            summarize_result = await self.execute_task(summarize_task_id)
            summaries = summarize_result.result["summaries"]
            
            # Step 4: Generate script
            script_task_id = await self.submit_task(
                AgentType.CONTENT_PROCESSOR,
                "generate_script",
                {"summaries": summaries, "language": language, "voice_name": voice_name},
                priority=1
            )
            script_result = await self.execute_task(script_task_id)
            script = script_result.result["script"]
            
            # Step 5: Generate audio
            audio_task_id = await self.submit_task(
                AgentType.AUDIO_GENERATOR,
                "generate_audio",
                {
                    "script": script,
                    "voice_name": voice_name,
                    "language": language
                },
                priority=1
            )
            audio_result = await self.execute_task(audio_task_id)
            audio_path = audio_result.result["audio_path"]
            
            logger.info(f"Workflow completed successfully. Audio saved to: {audio_path}")
            
            return {
                "success": True,
                "audio_path": audio_path,
                "articles_processed": len(articles),
                "summaries_generated": len(summaries),
                "script_length": len(script),
                "tasks_completed": len(self.completed_tasks)
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "tasks_completed": len(self.completed_tasks)
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        agent_statuses = {
            agent_type.value: agent.get_status() 
            for agent_type, agent in self.agents.items()
        }
        
        return {
            "supervisor_id": self.supervisor_id,
            "agents": agent_statuses,
            "queue_size": len(self.task_queue),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "system_health": "healthy" if all(
                agent.health_status == "healthy" 
                for agent in self.agents.values()
            ) else "degraded"
        }


# Observer function for task monitoring
def task_monitor_observer(event: str, task: Task):
    """Observer function to monitor task events."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    logger.info(f"[{timestamp}] {event.upper()}: {task.task_name} ({task.task_id[:8]})")
