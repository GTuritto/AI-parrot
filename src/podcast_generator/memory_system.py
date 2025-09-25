"""
AI-Parrot Memory System

Implements short-term and long-term memory for enhanced podcast generation
with context awareness, learning capabilities, and personalization.

Architecture:
- Short-term Memory: Session-based context (current conversation, recent articles)
- Long-term Memory: Persistent storage (user preferences, historical patterns, knowledge base)
"""

import json
import sqlite3
import hashlib
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import logging


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """Types of memory entries."""
    ARTICLE = "article"
    TOPIC = "topic"
    USER_PREFERENCE = "user_preference"
    GENERATION_CONTEXT = "generation_context"
    FEEDBACK = "feedback"
    PATTERN = "pattern"
    KNOWLEDGE = "knowledge"


@dataclass
class MemoryEntry:
    """Represents a memory entry with metadata."""
    id: str
    memory_type: MemoryType
    content: Dict[str, Any]
    timestamp: datetime
    importance: float  # 0.0 to 1.0
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.last_accessed is None:
            self.last_accessed = self.timestamp


class ShortTermMemory:
    """
    Session-based memory for current context and recent interactions.
    Stores temporary information that's relevant for the current session.
    """
    
    def __init__(self, max_entries: int = 100, ttl_hours: int = 24):
        self.max_entries = max_entries
        self.ttl_hours = ttl_hours
        self.memory: Dict[str, MemoryEntry] = {}
        self.session_id = self._generate_session_id()
        
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        return hashlib.md5(f"{datetime.now().isoformat()}".encode()).hexdigest()[:12]
    
    def store(self, memory_type: MemoryType, content: Dict[str, Any], 
              importance: float = 0.5, tags: List[str] = None) -> str:
        """Store information in short-term memory."""
        entry_id = hashlib.md5(f"{memory_type.value}_{json.dumps(content, sort_keys=True, cls=DateTimeEncoder)}".encode()).hexdigest()[:16]
        
        entry = MemoryEntry(
            id=entry_id,
            memory_type=memory_type,
            content=content,
            timestamp=datetime.now(),
            importance=importance,
            tags=tags or []
        )
        
        self.memory[entry_id] = entry
        self._cleanup_expired()
        self._enforce_size_limit()
        
        logger.debug(f"Stored short-term memory: {memory_type.value} - {entry_id}")
        return entry_id
    
    def retrieve(self, memory_type: Optional[MemoryType] = None, 
                tags: List[str] = None, limit: int = 10) -> List[MemoryEntry]:
        """Retrieve memories by type and/or tags."""
        results = []
        
        for entry in self.memory.values():
            # Filter by type
            if memory_type and entry.memory_type != memory_type:
                continue
                
            # Filter by tags
            if tags and not any(tag in entry.tags for tag in tags):
                continue
                
            # Update access info
            entry.access_count += 1
            entry.last_accessed = datetime.now()
            results.append(entry)
        
        # Sort by importance and recency
        results.sort(key=lambda x: (x.importance, x.timestamp), reverse=True)
        return results[:limit]
    
    def get_recent_articles(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recently processed articles."""
        entries = self.retrieve(MemoryType.ARTICLE, limit=limit)
        return [entry.content for entry in entries]
    
    def get_session_context(self) -> Dict[str, Any]:
        """Get current session context."""
        return {
            "session_id": self.session_id,
            "total_entries": len(self.memory),
            "memory_types": list(set(entry.memory_type.value for entry in self.memory.values())),
            "recent_activity": self._get_recent_activity()
        }
    
    def _get_recent_activity(self) -> List[Dict[str, Any]]:
        """Get recent memory activity."""
        recent = sorted(self.memory.values(), key=lambda x: x.timestamp, reverse=True)[:5]
        return [
            {
                "type": entry.memory_type.value,
                "timestamp": entry.timestamp.isoformat(),
                "importance": entry.importance
            }
            for entry in recent
        ]
    
    def _cleanup_expired(self):
        """Remove expired entries."""
        cutoff = datetime.now() - timedelta(hours=self.ttl_hours)
        expired = [entry_id for entry_id, entry in self.memory.items() 
                  if entry.timestamp < cutoff]
        
        for entry_id in expired:
            del self.memory[entry_id]
            
        if expired:
            logger.debug(f"Cleaned up {len(expired)} expired short-term memories")
    
    def _enforce_size_limit(self):
        """Enforce maximum number of entries."""
        if len(self.memory) <= self.max_entries:
            return
            
        # Sort by importance and recency, keep the most important
        entries = sorted(self.memory.values(), 
                        key=lambda x: (x.importance, x.timestamp), reverse=True)
        
        to_keep = entries[:self.max_entries]
        self.memory = {entry.id: entry for entry in to_keep}
        
        logger.debug(f"Enforced size limit, kept {len(to_keep)} entries")


class LongTermMemory:
    """
    Persistent memory for long-term learning and knowledge retention.
    Stores information across sessions with SQLite backend.
    """
    
    def __init__(self, db_path: str = "memory/long_term_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    memory_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    importance REAL NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TEXT,
                    tags TEXT,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_graph (
                    id TEXT PRIMARY KEY,
                    subject TEXT NOT NULL,
                    predicate TEXT NOT NULL,
                    object TEXT NOT NULL,
                    confidence REAL DEFAULT 1.0,
                    timestamp TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_patterns (
                    id TEXT PRIMARY KEY,
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,
                    frequency INTEGER DEFAULT 1,
                    last_seen TEXT NOT NULL,
                    confidence REAL DEFAULT 1.0
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance)")
            
    def store(self, memory_type: MemoryType, content: Dict[str, Any], 
              importance: float = 0.5, tags: List[str] = None, 
              metadata: Dict[str, Any] = None) -> str:
        """Store information in long-term memory."""
        entry_id = hashlib.md5(f"{memory_type.value}_{json.dumps(content, sort_keys=True, cls=DateTimeEncoder)}".encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO memories 
                (id, memory_type, content, timestamp, importance, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                entry_id,
                memory_type.value,
                json.dumps(content, cls=DateTimeEncoder),
                datetime.now().isoformat(),
                importance,
                json.dumps(tags or [], cls=DateTimeEncoder),
                json.dumps(metadata or {}, cls=DateTimeEncoder)
            ))
            
        logger.debug(f"Stored long-term memory: {memory_type.value} - {entry_id}")
        return entry_id
    
    def retrieve(self, memory_type: Optional[MemoryType] = None, 
                tags: List[str] = None, limit: int = 10, 
                min_importance: float = 0.0) -> List[MemoryEntry]:
        """Retrieve memories from long-term storage."""
        query = """
            SELECT id, memory_type, content, timestamp, importance, 
                   access_count, last_accessed, tags, metadata
            FROM memories 
            WHERE importance >= ?
        """
        params = [min_importance]
        
        if memory_type:
            query += " AND memory_type = ?"
            params.append(memory_type.value)
            
        query += " ORDER BY importance DESC, timestamp DESC LIMIT ?"
        params.append(limit)
        
        results = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            
            for row in cursor.fetchall():
                entry = MemoryEntry(
                    id=row[0],
                    memory_type=MemoryType(row[1]),
                    content=json.loads(row[2]),
                    timestamp=datetime.fromisoformat(row[3]),
                    importance=row[4],
                    access_count=row[5],
                    last_accessed=datetime.fromisoformat(row[6]) if row[6] else None,
                    tags=json.loads(row[7])
                )
                
                # Filter by tags if specified
                if tags and not any(tag in entry.tags for tag in tags):
                    continue
                    
                # Update access count
                self._update_access(entry.id)
                results.append(entry)
                
        return results
    
    def store_knowledge(self, subject: str, predicate: str, object_val: str, 
                       confidence: float = 1.0) -> str:
        """Store knowledge triple in knowledge graph."""
        triple_id = hashlib.md5(f"{subject}_{predicate}_{object_val}".encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO knowledge_graph 
                (id, subject, predicate, object, confidence, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (triple_id, subject, predicate, object_val, confidence, datetime.now().isoformat()))
            
        return triple_id
    
    def query_knowledge(self, subject: str = None, predicate: str = None, 
                       object_val: str = None) -> List[Tuple[str, str, str, float]]:
        """Query knowledge graph."""
        query = "SELECT subject, predicate, object, confidence FROM knowledge_graph WHERE 1=1"
        params = []
        
        if subject:
            query += " AND subject = ?"
            params.append(subject)
        if predicate:
            query += " AND predicate = ?"
            params.append(predicate)
        if object_val:
            query += " AND object = ?"
            params.append(object_val)
            
        query += " ORDER BY confidence DESC"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchall()
    
    def learn_pattern(self, pattern_type: str, pattern_data: Dict[str, Any]):
        """Learn and store user patterns."""
        pattern_id = hashlib.md5(f"{pattern_type}_{json.dumps(pattern_data, sort_keys=True, cls=DateTimeEncoder)}".encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            # Check if pattern exists
            cursor = conn.execute("SELECT frequency FROM user_patterns WHERE id = ?", (pattern_id,))
            existing = cursor.fetchone()
            
            if existing:
                # Update frequency
                conn.execute("""
                    UPDATE user_patterns 
                    SET frequency = frequency + 1, last_seen = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), pattern_id))
            else:
                # Insert new pattern
                conn.execute("""
                    INSERT INTO user_patterns 
                    (id, pattern_type, pattern_data, last_seen)
                    VALUES (?, ?, ?, ?)
                """, (pattern_id, pattern_type, json.dumps(pattern_data, cls=DateTimeEncoder), datetime.now().isoformat()))
    
    def get_patterns(self, pattern_type: str = None, min_frequency: int = 1) -> List[Dict[str, Any]]:
        """Get learned patterns."""
        query = "SELECT pattern_type, pattern_data, frequency, confidence FROM user_patterns WHERE frequency >= ?"
        params = [min_frequency]
        
        if pattern_type:
            query += " AND pattern_type = ?"
            params.append(pattern_type)
            
        query += " ORDER BY frequency DESC, confidence DESC"
        
        results = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            for row in cursor.fetchall():
                results.append({
                    "type": row[0],
                    "data": json.loads(row[1]),
                    "frequency": row[2],
                    "confidence": row[3]
                })
                
        return results
    
    def _update_access(self, entry_id: str):
        """Update access count and timestamp."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE memories 
                SET access_count = access_count + 1, last_accessed = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), entry_id))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics."""
        with sqlite3.connect(self.db_path) as conn:
            # Memory counts by type
            cursor = conn.execute("""
                SELECT memory_type, COUNT(*), AVG(importance), AVG(access_count)
                FROM memories 
                GROUP BY memory_type
            """)
            memory_stats = {row[0]: {"count": row[1], "avg_importance": row[2], "avg_access": row[3]} 
                           for row in cursor.fetchall()}
            
            # Knowledge graph stats
            cursor = conn.execute("SELECT COUNT(*) FROM knowledge_graph")
            knowledge_count = cursor.fetchone()[0]
            
            # Pattern stats
            cursor = conn.execute("SELECT COUNT(*), AVG(frequency) FROM user_patterns")
            pattern_stats = cursor.fetchone()
            
            return {
                "memory_entries": memory_stats,
                "knowledge_triples": knowledge_count,
                "patterns": {"count": pattern_stats[0], "avg_frequency": pattern_stats[1]},
                "total_memories": sum(stats["count"] for stats in memory_stats.values())
            }


class MemoryManager:
    """
    Unified interface for both short-term and long-term memory systems.
    Provides intelligent memory management and context-aware retrieval.
    """
    
    def __init__(self, db_path: str = "memory/long_term_memory.db"):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory(db_path)
        
    def store_article(self, article: Dict[str, Any], importance: float = 0.7):
        """Store article in both short and long-term memory."""
        tags = ["article", "ai_news"]
        if "title" in article:
            tags.append(article["title"].lower().replace(" ", "_"))
            
        # Store in short-term for immediate access
        self.short_term.store(MemoryType.ARTICLE, article, importance, tags)
        
        # Store in long-term for persistence
        self.long_term.store(MemoryType.ARTICLE, article, importance, tags)
        
        # Learn patterns from article
        self._learn_article_patterns(article)
    
    def store_generation_context(self, context: Dict[str, Any]):
        """Store podcast generation context."""
        self.short_term.store(MemoryType.GENERATION_CONTEXT, context, 0.8, ["generation", "context"])
        
        # Learn generation patterns
        self.long_term.learn_pattern("generation", {
            "language": context.get("language"),
            "voice": context.get("voice"),
            "timestamp": datetime.now().isoformat()
        })
    
    def get_relevant_context(self, current_articles: List[Dict[str, Any]], 
                           limit: int = 5) -> Dict[str, Any]:
        """Get relevant context for current generation."""
        # Get recent articles from short-term memory
        recent_articles = self.short_term.get_recent_articles(limit)
        
        # Get related knowledge from long-term memory
        knowledge_context = self._get_knowledge_context(current_articles)
        
        # Get user patterns
        patterns = self.long_term.get_patterns(min_frequency=2)
        
        return {
            "recent_articles": recent_articles,
            "knowledge_context": knowledge_context,
            "user_patterns": patterns,
            "session_context": self.short_term.get_session_context()
        }
    
    def _learn_article_patterns(self, article: Dict[str, Any]):
        """Learn patterns from article content."""
        if "title" in article:
            # Extract topics/keywords
            title_words = article["title"].lower().split()
            for word in title_words:
                if len(word) > 3:  # Filter short words
                    self.long_term.store_knowledge(word, "appears_in", "article_title")
        
        if "summary" in article:
            # Learn about content patterns
            summary_length = len(article["summary"])
            self.long_term.learn_pattern("article_length", {"length_category": self._categorize_length(summary_length)})
    
    def _get_knowledge_context(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get relevant knowledge context for articles."""
        context = []
        
        for article in articles:
            if "title" in article:
                title_words = article["title"].lower().split()
                for word in title_words:
                    if len(word) > 3:
                        related = self.long_term.query_knowledge(subject=word)
                        if related:
                            context.extend([{"subject": r[0], "predicate": r[1], "object": r[2]} for r in related[:3]])
        
        return context[:10]  # Limit context size
    
    def _categorize_length(self, length: int) -> str:
        """Categorize content length."""
        if length < 100:
            return "short"
        elif length < 500:
            return "medium"
        else:
            return "long"
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get comprehensive memory summary."""
        return {
            "short_term": self.short_term.get_session_context(),
            "long_term": self.long_term.get_statistics(),
            "total_active_memories": len(self.short_term.memory)
        }
    
    def clear_session(self):
        """Clear current session (short-term memory)."""
        self.short_term = ShortTermMemory()
        logger.info("Cleared short-term memory session")
