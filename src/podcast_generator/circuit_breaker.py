"""Circuit Breaker Pattern Implementation - Educational Version.

🎓 LEARNING OBJECTIVES:
This module demonstrates the Circuit Breaker Resilience Pattern:
1. Failure Detection and Prevention
2. Graceful Degradation Strategies
3. Automatic Recovery Mechanisms
4. System Stability Patterns
5. Health Monitoring and Metrics

🔌 CIRCUIT BREAKER ANALOGY:
Just like electrical circuit breakers protect your home from power surges,
software circuit breakers protect distributed systems from cascade failures.
When a service becomes unhealthy, the circuit breaker "trips" and prevents
further requests, allowing the system to recover gracefully.

📊 CIRCUIT STATES:
┌─────────────┐    failure_threshold    ┌─────────────┐
│   CLOSED    │────────────────────────►│    OPEN     │
│ (Normal)    │                         │ (Failing)   │
└─────────────┘                         └─────────────┘
       ▲                                       │
       │ success                               │ timeout
       │                                       ▼
┌─────────────┐    success_threshold    ┌─────────────┐
│ HALF_OPEN   │◄───────────────────────│  RECOVERY   │
│ (Testing)   │                         │ (Waiting)   │
└─────────────┘                         └─────────────┘

🔍 KEY CONCEPTS:
1. CLOSED: Normal operation, requests pass through
2. OPEN: Failure detected, requests immediately fail
3. HALF_OPEN: Testing recovery, limited requests allowed
4. Failure Threshold: Number of failures before opening
5. Recovery Timeout: Time to wait before testing recovery

🛡️ BENEFITS:
- Prevents cascade failures across services
- Provides fast failure responses
- Enables automatic recovery
- Improves system stability
- Offers fallback mechanisms

📚 EDUCATIONAL VALUE:
This implementation shows how production systems handle failures
gracefully, demonstrating patterns used by Netflix, Amazon, and
other large-scale distributed systems.
"""
import asyncio
import time
from datetime import datetime
from typing import Callable, Any, Optional, Dict
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """States of the circuit breaker."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, blocking requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5          # Number of failures before opening
    recovery_timeout: float = 60.0      # Seconds before trying half-open
    success_threshold: int = 3          # Successes needed to close from half-open
    timeout: float = 30.0               # Request timeout in seconds
    expected_exception: type = Exception  # Exception type to catch


class CircuitBreakerError(Exception):
    """Exception raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """Circuit breaker implementation for resilient AI agent operations."""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.last_success_time: Optional[float] = None
        
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset from OPEN to HALF_OPEN."""
        if self.state != CircuitState.OPEN:
            return False
            
        if self.last_failure_time is None:
            return False
            
        return (time.time() - self.last_failure_time) >= self.config.recovery_timeout
    
    def _record_success(self):
        """Record a successful operation."""
        self.failure_count = 0
        self.last_success_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.success_count = 0
                logger.info("Circuit breaker closed - service recovered")
        
    def _record_failure(self):
        """Record a failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        self.success_count = 0
        
        if self.state == CircuitState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
                logger.warning(f"Circuit breaker opened - {self.failure_count} failures")
        elif self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning("Circuit breaker reopened - test failed")
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        # Check if we should attempt reset
        if self._should_attempt_reset():
            self.state = CircuitState.HALF_OPEN
            logger.info("Circuit breaker half-open - testing service")
        
        # Block requests if circuit is open
        if self.state == CircuitState.OPEN:
            raise CircuitBreakerError("Circuit breaker is OPEN - service unavailable")
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=self.config.timeout
            )
            
            self._record_success()
            return result
            
        except self.config.expected_exception as e:
            self._record_failure()
            raise e
        except asyncio.TimeoutError:
            self._record_failure()
            raise CircuitBreakerError("Operation timed out")
    
    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "last_success_time": self.last_success_time
        }


class ResilientAgentWrapper:
    """Wrapper that adds circuit breaker resilience to agents."""
    
    def __init__(self, agent, circuit_config: CircuitBreakerConfig = None):
        self.agent = agent
        self.circuit_breaker = CircuitBreaker(
            circuit_config or CircuitBreakerConfig()
        )
        self.fallback_handlers: Dict[str, Callable] = {}
    
    def add_fallback(self, method_name: str, fallback_func: Callable):
        """Add fallback function for a specific method."""
        self.fallback_handlers[method_name] = fallback_func
    
    async def execute_with_resilience(self, method_name: str, *args, **kwargs) -> Any:
        """Execute agent method with circuit breaker and fallback."""
        try:
            method = getattr(self.agent, method_name)
            return await self.circuit_breaker.call(method, *args, **kwargs)
            
        except (CircuitBreakerError, Exception) as e:
            logger.warning(f"Primary method failed: {e}")
            
            # Try fallback if available
            if method_name in self.fallback_handlers:
                logger.info(f"Using fallback for {method_name}")
                fallback = self.fallback_handlers[method_name]
                return await fallback(*args, **kwargs)
            else:
                raise e
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status including circuit breaker state."""
        return {
            "agent_id": getattr(self.agent, 'agent_id', 'unknown'),
            "circuit_breaker": self.circuit_breaker.get_state(),
            "fallbacks_available": list(self.fallback_handlers.keys())
        }


# Resilient versions of key operations
class ResilientOperations:
    """Collection of resilient operations with circuit breakers."""
    
    def __init__(self):
        self.article_fetcher_cb = CircuitBreaker(CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=30.0,
            timeout=60.0
        ))
        
        self.ai_processor_cb = CircuitBreaker(CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=45.0,
            timeout=120.0
        ))
        
        self.tts_generator_cb = CircuitBreaker(CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=60.0,
            timeout=180.0
        ))
    
    async def fetch_articles_resilient(self) -> list:
        """Fetch articles with circuit breaker protection."""
        async def fetch_operation():
            from podcast_generator.article_fetcher import fetch_multiple_sources
            return await fetch_multiple_sources()
        
        try:
            return await self.article_fetcher_cb.call(fetch_operation)
        except CircuitBreakerError:
            # Fallback to cached articles or default content
            logger.warning("Using fallback articles due to circuit breaker")
            return self._get_fallback_articles()
    
    async def process_with_ai_resilient(self, processor, method_name: str, *args, **kwargs):
        """Process with AI using circuit breaker protection."""
        async def ai_operation():
            method = getattr(processor, method_name)
            return method(*args, **kwargs)
        
        try:
            return await self.ai_processor_cb.call(ai_operation)
        except CircuitBreakerError:
            logger.warning(f"AI processing failed, using fallback for {method_name}")
            return self._get_ai_fallback(method_name, *args, **kwargs)
    
    async def generate_audio_resilient(self, file_manager, *args, **kwargs):
        """Generate audio with circuit breaker protection."""
        async def tts_operation():
            return await file_manager.save_mp3_file(*args, **kwargs)
        
        try:
            return await self.tts_generator_cb.call(tts_operation)
        except CircuitBreakerError:
            logger.warning("TTS generation failed, creating text-only output")
            return self._create_text_fallback(*args, **kwargs)
    
    def _get_fallback_articles(self) -> list:
        """Provide fallback articles when fetching fails."""
        return [
            {
                "title": "AI System Maintenance",
                "description": "The AI news system is currently under maintenance. Please check back later for the latest updates.",
                "link": "#",
                "published": datetime.now(),
                "source": "System"
            }
        ]
    
    def _get_ai_fallback(self, method_name: str, *args, **kwargs) -> str:
        """Provide fallback AI responses."""
        if method_name == "summarize_article":
            return "Article summary temporarily unavailable due to system maintenance."
        elif method_name == "generate_podcast_script":
            return "Welcome to the AI Podcast. We're experiencing technical difficulties and will return with regular programming shortly. Thank you for your patience."
        else:
            return "AI processing temporarily unavailable."
    
    def _create_text_fallback(self, text_content: str, *args, **kwargs) -> str:
        """Create text-only fallback when audio generation fails."""
        from podcast_generator.file_utils import FileManager
        file_manager = FileManager()
        
        # Save as text file instead of audio
        text_path = file_manager.get_output_path("fallback_podcast.txt")
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write("PODCAST TRANSCRIPT (Audio generation unavailable)\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write(text_content)
        
        return text_path
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get health status of all circuit breakers."""
        return {
            "article_fetcher": self.article_fetcher_cb.get_state(),
            "ai_processor": self.ai_processor_cb.get_state(),
            "tts_generator": self.tts_generator_cb.get_state(),
            "overall_health": "healthy" if all(
                cb.state == CircuitState.CLOSED 
                for cb in [self.article_fetcher_cb, self.ai_processor_cb, self.tts_generator_cb]
            ) else "degraded"
        }
