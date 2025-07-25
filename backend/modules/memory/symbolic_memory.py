"""
Symbolic Memory System
Enhanced memory with symbol-based associations and emotional context
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import json
import sqlite3
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)

class SymbolType(Enum):
    """Types of symbolic associations"""
    METAPHOR = "metaphor"
    EMOTION = "emotion"
    CONCEPT = "concept"
    MEMORY = "memory"
    RELATIONSHIP = "relationship"
    EXPERIENCE = "experience"

@dataclass
class SymbolicMemory:
    """Individual symbolic memory entry"""
    id: str
    symbol: str
    symbol_type: SymbolType
    content: str
    emotional_weight: float  # -1.0 to 1.0
    association_strength: float  # 0.0 to 1.0
    context: Dict[str, Any]
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0

@dataclass
class MemoryCluster:
    """Cluster of related memories"""
    id: str
    name: str
    central_theme: str
    memories: List[str]  # Memory IDs
    emotional_tone: float
    importance: float
    created_at: datetime
    last_updated: datetime

class SymbolicMemorySystem:
    """Enhanced memory system with symbolic associations"""
    
    def __init__(self, db_path: str = "data/symbolic_memory.db"):
        self.db_path = db_path
        self.connection = None
        self.symbols_cache = {}
        # symbol -> {frequency, avg_emotion, last_used, decay_score}
        self.clusters_cache = {}
        self.emotional_weights = {}
        
    async def initialize(self):
        """Initialize the symbolic memory system"""
        try:
            # Create database connection
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            
            # Create tables
            await self._create_tables()
            
            # Load cached data
            await self._load_caches()
            
            logger.info("✅ Symbolic Memory System initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize symbolic memory: {e}")
            raise e
    
    async def _create_tables(self):
        """Create database tables for symbolic memory"""
        cursor = self.connection.cursor()
        
        # Symbolic memories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS symbolic_memories (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                symbol_type TEXT NOT NULL,
                content TEXT NOT NULL,
                emotional_weight REAL NOT NULL,
                association_strength REAL NOT NULL,
                context TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                last_accessed TIMESTAMP NOT NULL,
                access_count INTEGER DEFAULT 0
            )
        """)
        
        # Memory clusters table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_clusters (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                central_theme TEXT NOT NULL,
                memories TEXT NOT NULL,
                emotional_tone REAL NOT NULL,
                importance REAL NOT NULL,
                created_at TIMESTAMP NOT NULL,
                last_updated TIMESTAMP NOT NULL
            )
        """)
        
        # Symbol associations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS symbol_associations (
                id TEXT PRIMARY KEY,
                symbol_a TEXT NOT NULL,
                symbol_b TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                strength REAL NOT NULL,
                created_at TIMESTAMP NOT NULL
            )
        """)
        
        # Emotional context table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emotional_contexts (
                id TEXT PRIMARY KEY,
                memory_id TEXT NOT NULL,
                emotion TEXT NOT NULL,
                intensity REAL NOT NULL,
                trigger_words TEXT,
                context_data TEXT,
                created_at TIMESTAMP NOT NULL,
                FOREIGN KEY (memory_id) REFERENCES symbolic_memories (id)
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_symbol ON symbolic_memories(symbol)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_emotional_weight ON symbolic_memories(emotional_weight)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_association_strength ON symbolic_memories(association_strength)")
        
        self.connection.commit()
        logger.info("📊 Symbolic memory database tables created")
    
    async def _load_caches(self):
        """Load frequently accessed data into memory"""
        cursor = self.connection.cursor()
        
        # Load symbol frequencies
        cursor.execute("""
            SELECT symbol, COUNT(*) as frequency, AVG(emotional_weight) as avg_emotion,
                   MAX(last_accessed) as last_used
            FROM symbolic_memories
            GROUP BY symbol
        """)
        
        for row in cursor.fetchall():
            last_used = row['last_used']
            last_dt = datetime.fromisoformat(last_used) if last_used else datetime.now()
            self.symbols_cache[row['symbol']] = {
                'frequency': row['frequency'],
                'avg_emotion': row['avg_emotion'],
                'last_used': last_dt,
                'decay_score': 0.0
            }
        
        logger.info(f"📚 Loaded {len(self.symbols_cache)} symbols into cache")
    
    async def store_memory(self, 
                          content: str, 
                          symbols: List[str],
                          emotional_context: Dict[str, float],
                          user_context: Dict[str, Any] = None) -> str:
        """
        Store a new memory with symbolic associations
        
        Args:
            content: The actual memory content
            symbols: List of associated symbols
            emotional_context: Emotions and their intensities
            user_context: Additional context information
            
        Returns:
            Memory ID
        """
        try:
            memory_id = self._generate_memory_id(content)
            now = datetime.now()
            
            # Calculate overall emotional weight
            emotional_weight = sum(emotional_context.values()) / len(emotional_context) if emotional_context else 0.0
            
            cursor = self.connection.cursor()
            
            # Store individual symbolic memories for each symbol
            for symbol in symbols:
                symbol_type = self._classify_symbol(symbol, content)
                association_strength = self._calculate_association_strength(symbol, content, emotional_context)
                
                symbolic_memory = SymbolicMemory(
                    id=f"{memory_id}_{symbol}",
                    symbol=symbol,
                    symbol_type=symbol_type,
                    content=content,
                    emotional_weight=emotional_weight,
                    association_strength=association_strength,
                    context=user_context or {},
                    created_at=now,
                    last_accessed=now
                )
                
                cursor.execute("""
                    INSERT OR REPLACE INTO symbolic_memories 
                    (id, symbol, symbol_type, content, emotional_weight, 
                     association_strength, context, created_at, last_accessed, access_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    symbolic_memory.id,
                    symbolic_memory.symbol,
                    symbolic_memory.symbol_type.value,
                    symbolic_memory.content,
                    symbolic_memory.emotional_weight,
                    symbolic_memory.association_strength,
                    json.dumps(symbolic_memory.context),
                    symbolic_memory.created_at,
                    symbolic_memory.last_accessed,
                    symbolic_memory.access_count
                ))

                # Track symbol usage
                if symbol not in self.symbols_cache:
                    self.symbols_cache[symbol] = {
                        'frequency': 0,
                        'avg_emotion': emotional_weight,
                        'last_used': now,
                        'decay_score': 0.0
                    }
                self.symbols_cache[symbol]['last_used'] = now
            
            # Store emotional contexts
            for emotion, intensity in emotional_context.items():
                cursor.execute("""
                    INSERT INTO emotional_contexts 
                    (id, memory_id, emotion, intensity, trigger_words, context_data, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"{memory_id}_{emotion}",
                    memory_id,
                    emotion,
                    intensity,
                    json.dumps(symbols),
                    json.dumps(user_context or {}),
                    now
                ))
            
            self.connection.commit()
            
            # Update caches
            await self._update_symbol_cache(symbols, emotional_weight)
            
            # Check for clustering opportunities
            await self._update_memory_clusters(memory_id, symbols, emotional_weight)
            
            logger.info(f"💾 Stored symbolic memory: {memory_id} with {len(symbols)} symbols")
            return memory_id
            
        except Exception as e:
            logger.error(f"❌ Failed to store symbolic memory: {e}")
            raise e
    
    async def recall_by_symbol(self, 
                              symbol: str, 
                              limit: int = 10,
                              min_strength: float = 0.1) -> List[SymbolicMemory]:
        """
        Recall memories associated with a specific symbol
        
        Args:
            symbol: Symbol to search for
            limit: Maximum number of memories to return
            min_strength: Minimum association strength threshold
            
        Returns:
            List of relevant symbolic memories
        """
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT * FROM symbolic_memories 
                WHERE symbol = ? AND association_strength >= ?
                ORDER BY association_strength DESC, last_accessed DESC
                LIMIT ?
            """, (symbol, min_strength, limit))
            
            memories = []
            for row in cursor.fetchall():
                memory = SymbolicMemory(
                    id=row['id'],
                    symbol=row['symbol'],
                    symbol_type=SymbolType(row['symbol_type']),
                    content=row['content'],
                    emotional_weight=row['emotional_weight'],
                    association_strength=row['association_strength'],
                    context=json.loads(row['context']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    last_accessed=datetime.fromisoformat(row['last_accessed']),
                    access_count=row['access_count']
                )
                memories.append(memory)
                
                # Update access tracking
                await self._update_access_tracking(memory.id)
            
            logger.info(f"🔍 Recalled {len(memories)} memories for symbol: {symbol}")
            return memories
            
        except Exception as e:
            logger.error(f"❌ Failed to recall memories by symbol: {e}")
            return []
    
    async def recall_by_emotion(self, 
                               emotion: str, 
                               intensity_threshold: float = 0.5,
                               limit: int = 10) -> List[SymbolicMemory]:
        """Recall memories by emotional context"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT sm.* FROM symbolic_memories sm
                JOIN emotional_contexts ec ON sm.id LIKE ec.memory_id || '%'
                WHERE ec.emotion = ? AND ec.intensity >= ?
                ORDER BY ec.intensity DESC, sm.last_accessed DESC
                LIMIT ?
            """, (emotion, intensity_threshold, limit))
            
            memories = []
            for row in cursor.fetchall():
                memory = SymbolicMemory(
                    id=row['id'],
                    symbol=row['symbol'],
                    symbol_type=SymbolType(row['symbol_type']),
                    content=row['content'],
                    emotional_weight=row['emotional_weight'],
                    association_strength=row['association_strength'],
                    context=json.loads(row['context']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    last_accessed=datetime.fromisoformat(row['last_accessed']),
                    access_count=row['access_count']
                )
                memories.append(memory)
            
            logger.info(f"💭 Recalled {len(memories)} memories for emotion: {emotion}")
            return memories
            
        except Exception as e:
            logger.error(f"❌ Failed to recall memories by emotion: {e}")
            return []
    
    async def find_symbolic_connections(self, symbols: List[str]) -> Dict[str, List[str]]:
        """Find connections between symbols"""
        try:
            cursor = self.connection.cursor()
            connections = {}
            
            for symbol in symbols:
                cursor.execute("""
                    SELECT DISTINCT sm2.symbol, AVG(sm2.association_strength) as avg_strength
                    FROM symbolic_memories sm1
                    JOIN symbolic_memories sm2 ON sm1.content = sm2.content
                    WHERE sm1.symbol = ? AND sm2.symbol != ?
                    GROUP BY sm2.symbol
                    ORDER BY avg_strength DESC
                    LIMIT 5
                """, (symbol, symbol))
                
                related_symbols = [row['symbol'] for row in cursor.fetchall()]
                connections[symbol] = related_symbols
            
            return connections
            
        except Exception as e:
            logger.error(f"❌ Failed to find symbolic connections: {e}")
            return {}
    
    def _generate_memory_id(self, content: str) -> str:
        """Generate unique memory ID"""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"mem_{timestamp}_{content_hash}"
    
    def _classify_symbol(self, symbol: str, content: str) -> SymbolType:
        """Classify the type of symbol based on content and context"""
        symbol_lower = symbol.lower()
        content_lower = content.lower()
        
        # Emotion words
        emotion_words = ['happy', 'sad', 'love', 'fear', 'anger', 'joy', 'hope', 'trust']
        if any(word in symbol_lower for word in emotion_words):
            return SymbolType.EMOTION
        
        # Relationship words
        relationship_words = ['friend', 'partner', 'family', 'companion', 'together']
        if any(word in symbol_lower for word in relationship_words):
            return SymbolType.RELATIONSHIP
        
        # Experience words
        experience_words = ['journey', 'adventure', 'discovery', 'learning', 'growth']
        if any(word in symbol_lower for word in experience_words):
            return SymbolType.EXPERIENCE
        
        # Abstract concepts
        concept_words = ['freedom', 'peace', 'wisdom', 'truth', 'beauty', 'meaning']
        if any(word in symbol_lower for word in concept_words):
            return SymbolType.CONCEPT
        
        # Default to metaphor
        return SymbolType.METAPHOR
    
    def _calculate_association_strength(self, symbol: str, content: str, emotional_context: Dict[str, float]) -> float:
        """Calculate how strongly a symbol is associated with the content"""
        strength = 0.0
        
        # Base strength from symbol frequency in content
        symbol_count = content.lower().count(symbol.lower())
        content_length = len(content.split())
        if content_length > 0:
            strength += min(symbol_count / content_length * 10, 0.5)
        
        # Emotional relevance boost
        if emotional_context:
            avg_emotion = sum(emotional_context.values()) / len(emotional_context)
            strength += abs(avg_emotion) * 0.3
        
        # Symbol cache boost (frequently used symbols)
        if symbol in self.symbols_cache:
            frequency_boost = min(self.symbols_cache[symbol]['frequency'] / 100, 0.2)
            strength += frequency_boost
        
        return min(strength, 1.0)
    
    async def _update_symbol_cache(self, symbols: List[str], emotional_weight: float):
        """Update symbol frequency cache"""
        now = datetime.now()
        for symbol in symbols:
            if symbol in self.symbols_cache:
                self.symbols_cache[symbol]['frequency'] += 1
                # Update average emotion
                old_avg = self.symbols_cache[symbol]['avg_emotion']
                freq = self.symbols_cache[symbol]['frequency']
                new_avg = (old_avg * (freq - 1) + emotional_weight) / freq
                self.symbols_cache[symbol]['avg_emotion'] = new_avg
            else:
                self.symbols_cache[symbol] = {
                    'frequency': 1,
                    'avg_emotion': emotional_weight,
                    'last_used': now,
                    'decay_score': 0.0
                }
            self.symbols_cache[symbol]['last_used'] = now
            self.symbols_cache[symbol]['decay_score'] = 0.0
    
    async def _update_access_tracking(self, memory_id: str):
        """Update memory access tracking"""
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE symbolic_memories
            SET access_count = access_count + 1, last_accessed = ?
            WHERE id = ?
        """, (datetime.now(), memory_id))
        self.connection.commit()

        # Update symbol usage cache
        symbol = memory_id.split("_")[-1]
        if symbol in self.symbols_cache:
            self.symbols_cache[symbol]['last_used'] = datetime.now()
            self.symbols_cache[symbol]['decay_score'] = 0.0
    
    async def _update_memory_clusters(self, memory_id: str, symbols: List[str], emotional_weight: float):
        """Update or create memory clusters based on symbolic associations"""
        # This would implement clustering logic based on symbol overlap
        # For now, we'll keep it simple and focus on the core functionality
        pass
    
    async def get_memory_statistics(self) -> Dict[str, Any]:
        """Get statistics about the memory system"""
        try:
            cursor = self.connection.cursor()
            
            # Total memories
            cursor.execute("SELECT COUNT(*) as total FROM symbolic_memories")
            total_memories = cursor.fetchone()['total']
            
            # Unique symbols
            cursor.execute("SELECT COUNT(DISTINCT symbol) as unique_symbols FROM symbolic_memories")
            unique_symbols = cursor.fetchone()['unique_symbols']
            
            # Average emotional weight
            cursor.execute("SELECT AVG(emotional_weight) as avg_emotion FROM symbolic_memories")
            avg_emotion = cursor.fetchone()['avg_emotion'] or 0.0
            
            # Most frequent symbols
            cursor.execute("""
                SELECT symbol, COUNT(*) as frequency 
                FROM symbolic_memories 
                GROUP BY symbol 
                ORDER BY frequency DESC 
                LIMIT 10
            """)
            top_symbols = [{'symbol': row['symbol'], 'frequency': row['frequency']} 
                          for row in cursor.fetchall()]
            
            return {
                'total_memories': total_memories,
                'unique_symbols': unique_symbols,
                'average_emotional_weight': avg_emotion,
                'top_symbols': top_symbols,
                'cache_size': len(self.symbols_cache)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get memory statistics: {e}")
            return {}

# Global instance
symbolic_memory_system = SymbolicMemorySystem()
