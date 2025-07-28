"""
Memory Handler - Vector database and memory management

This module provides memory management capabilities including vector storage,
semantic search, and conversation history management.
"""

import logging
import asyncio
import json
import os
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import hashlib
import pickle
from dataclasses import dataclass, asdict
import aiofiles

logger = logging.getLogger(__name__)

@dataclass
class MemoryEntry:
    """Represents a single memory entry."""
    id: str
    content: str
    embedding: Optional[List[float]]
    metadata: Dict[str, Any]
    timestamp: datetime
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    tags: List[str] = None
    importance: float = 0.5  # 0.0 to 1.0
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.last_accessed is None:
            self.last_accessed = self.timestamp

class MemoryHandler:
    """
    Handles memory storage, retrieval, and management for the House of Minds system.
    
    Provides vector search, semantic similarity, conversation history management,
    and intelligent memory consolidation.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the memory handler."""
        self.config = config
        self.storage_path = config.get('storage_path', './data/memory')
        self.max_memory_entries = config.get('max_memory_entries', 10000)
        self.embedding_dim = config.get('embedding_dim', 384)  # For lightweight embeddings
        
        # Memory management settings
        self.importance_threshold = config.get('importance_threshold', 0.3)
        self.decay_rate = config.get('decay_rate', 0.1)
        self.consolidation_interval = config.get('consolidation_interval', 24)  # hours
        
        # Vector search settings
        self.similarity_threshold = config.get('similarity_threshold', 0.7)
        self.max_search_results = config.get('max_search_results', 10)
        
        # Storage
        self.memories: Dict[str, MemoryEntry] = {}
        self.conversation_history: List[Dict[str, Any]] = []
        self.tags_index: Dict[str, List[str]] = {}  # tag -> memory_ids
        
        # Ensure storage directory exists
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Load existing memories
        asyncio.create_task(self._load_memories())
        
        logger.info("🧠 Memory Handler initialized")
    
    async def store_memory(self, content: str, metadata: Dict[str, Any] = None,
                          tags: List[str] = None, importance: float = 0.5) -> str:
        """
        Store a new memory entry.
        
        Args:
            content: The content to store
            metadata: Additional metadata
            tags: Tags for categorization
            importance: Importance score (0.0 to 1.0)
            
        Returns:
            The memory ID
        """
        try:
            # Generate unique ID
            memory_id = self._generate_memory_id(content)
            
            # Create memory entry
            memory = MemoryEntry(
                id=memory_id,
                content=content,
                embedding=await self._generate_embedding(content),
                metadata=metadata or {},
                timestamp=datetime.now(),
                tags=tags or [],
                importance=max(0.0, min(1.0, importance))
            )
            
            # Store memory
            self.memories[memory_id] = memory
            
            # Update tags index
            for tag in memory.tags:
                if tag not in self.tags_index:
                    self.tags_index[tag] = []
                self.tags_index[tag].append(memory_id)
            
            # Save to disk
            await self._save_memory(memory)
            
            logger.info(f"💾 Stored memory: {memory_id[:8]}...")
            return memory_id
            
        except Exception as e:
            logger.error(f"❌ Failed to store memory: {e}")
            raise
    
    async def search_memories(self, query: str, 
                            tags: List[str] = None,
                            min_importance: float = 0.0,
                            max_results: int = None) -> List[Dict[str, Any]]:
        """
        Search for memories using semantic similarity.
        
        Args:
            query: Search query
            tags: Filter by tags
            min_importance: Minimum importance threshold
            max_results: Maximum number of results
            
        Returns:
            List of matching memories with similarity scores
        """
        try:
            if not self.memories:
                return []
            
            max_results = max_results or self.max_search_results
            
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)
            
            # Find similar memories
            similarities = []
            for memory_id, memory in self.memories.items():
                # Filter by tags if specified
                if tags and not any(tag in memory.tags for tag in tags):
                    continue
                
                # Filter by importance
                if memory.importance < min_importance:
                    continue
                
                # Calculate similarity
                if memory.embedding:
                    similarity = self._calculate_similarity(query_embedding, memory.embedding)
                    if similarity >= self.similarity_threshold:
                        similarities.append((memory_id, similarity))
            
            # Sort by similarity and limit results
            similarities.sort(key=lambda x: x[1], reverse=True)
            similarities = similarities[:max_results]
            
            # Build results
            results = []
            for memory_id, similarity in similarities:
                memory = self.memories[memory_id]
                
                # Update access tracking
                memory.access_count += 1
                memory.last_accessed = datetime.now()
                
                results.append({
                    'id': memory_id,
                    'content': memory.content,
                    'metadata': memory.metadata,
                    'tags': memory.tags,
                    'importance': memory.importance,
                    'similarity': similarity,
                    'timestamp': memory.timestamp.isoformat(),
                    'access_count': memory.access_count
                })
            
            logger.info(f"🔍 Found {len(results)} memories for query")
            return results
            
        except Exception as e:
            logger.error(f"❌ Memory search failed: {e}")
            return []
    
    async def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific memory by ID."""
        if memory_id not in self.memories:
            return None
        
        memory = self.memories[memory_id]
        memory.access_count += 1
        memory.last_accessed = datetime.now()
        
        return {
            'id': memory_id,
            'content': memory.content,
            'metadata': memory.metadata,
            'tags': memory.tags,
            'importance': memory.importance,
            'timestamp': memory.timestamp.isoformat(),
            'access_count': memory.access_count,
            'last_accessed': memory.last_accessed.isoformat()
        }
    
    async def update_memory(self, memory_id: str, 
                          content: str = None,
                          metadata: Dict[str, Any] = None,
                          tags: List[str] = None,
                          importance: float = None) -> bool:
        """Update an existing memory."""
        if memory_id not in self.memories:
            return False
        
        try:
            memory = self.memories[memory_id]
            
            # Update fields if provided
            if content is not None:
                memory.content = content
                memory.embedding = await self._generate_embedding(content)
            
            if metadata is not None:
                memory.metadata.update(metadata)
            
            if tags is not None:
                # Remove from old tags index
                for tag in memory.tags:
                    if tag in self.tags_index and memory_id in self.tags_index[tag]:
                        self.tags_index[tag].remove(memory_id)
                
                # Update tags
                memory.tags = tags
                
                # Add to new tags index
                for tag in tags:
                    if tag not in self.tags_index:
                        self.tags_index[tag] = []
                    if memory_id not in self.tags_index[tag]:
                        self.tags_index[tag].append(memory_id)
            
            if importance is not None:
                memory.importance = max(0.0, min(1.0, importance))
            
            # Save updated memory
            await self._save_memory(memory)
            
            logger.info(f"📝 Updated memory: {memory_id[:8]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update memory {memory_id}: {e}")
            return False
    
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory."""
        if memory_id not in self.memories:
            return False
        
        try:
            memory = self.memories[memory_id]
            
            # Remove from tags index
            for tag in memory.tags:
                if tag in self.tags_index and memory_id in self.tags_index[tag]:
                    self.tags_index[tag].remove(memory_id)
                    if not self.tags_index[tag]:  # Remove empty tag
                        del self.tags_index[tag]
            
            # Remove from memories
            del self.memories[memory_id]
            
            # Remove file
            memory_file = os.path.join(self.storage_path, f"{memory_id}.json")
            if os.path.exists(memory_file):
                os.remove(memory_file)
            
            logger.info(f"🗑️ Deleted memory: {memory_id[:8]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete memory {memory_id}: {e}")
            return False
    
    async def store_conversation(self, user_input: str, ai_response: str,
                               context: Dict[str, Any] = None) -> str:
        """Store a conversation exchange."""
        conversation_entry = {
            'id': self._generate_conversation_id(user_input, ai_response),
            'user_input': user_input,
            'ai_response': ai_response,
            'context': context or {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.conversation_history.append(conversation_entry)
        
        # Auto-store important conversations as memories
        if self._should_store_as_memory(user_input, ai_response):
            await self.store_memory(
                content=f"User: {user_input}\nAI: {ai_response}",
                metadata={'type': 'conversation', 'context': context},
                tags=['conversation'],
                importance=0.6
            )
        
        # Limit conversation history size
        if len(self.conversation_history) > 1000:
            self.conversation_history = self.conversation_history[-1000:]
        
        return conversation_entry['id']
    
    async def get_conversation_context(self, num_exchanges: int = 5) -> List[Dict[str, Any]]:
        """Get recent conversation context."""
        return self.conversation_history[-num_exchanges:] if self.conversation_history else []
    
    async def consolidate_memories(self):
        """Consolidate and clean up memories."""
        try:
            logger.info("🧹 Starting memory consolidation...")
            
            current_time = datetime.now()
            consolidated_count = 0
            deleted_count = 0
            
            memories_to_delete = []
            
            for memory_id, memory in self.memories.items():
                # Calculate memory decay based on age and access
                age_days = (current_time - memory.timestamp).days
                recency_score = 1.0 / (1.0 + age_days * self.decay_rate)
                access_score = min(1.0, memory.access_count / 10.0)
                
                # Calculate current importance
                current_importance = memory.importance * (recency_score + access_score) / 2.0
                
                if current_importance < self.importance_threshold:
                    memories_to_delete.append(memory_id)
                else:
                    # Update importance
                    memory.importance = current_importance
                    consolidated_count += 1
            
            # Delete low-importance memories
            for memory_id in memories_to_delete:
                await self.delete_memory(memory_id)
                deleted_count += 1
            
            logger.info(f"✅ Memory consolidation complete: {consolidated_count} kept, {deleted_count} deleted")
            
        except Exception as e:
            logger.error(f"❌ Memory consolidation failed: {e}")
    
    def _generate_memory_id(self, content: str) -> str:
        """Generate a unique ID for a memory."""
        timestamp = datetime.now().isoformat()
        content_hash = hashlib.md5(f"{content}{timestamp}".encode()).hexdigest()
        return f"mem_{content_hash[:16]}"
    
    def _generate_conversation_id(self, user_input: str, ai_response: str) -> str:
        """Generate a unique ID for a conversation."""
        timestamp = datetime.now().isoformat()
        content_hash = hashlib.md5(f"{user_input}{ai_response}{timestamp}".encode()).hexdigest()
        return f"conv_{content_hash[:16]}"
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate a simple embedding for text.
        
        Note: This is a placeholder implementation. In production,
        you would use a proper embedding model like sentence-transformers.
        """
        # Simple hash-based embedding (for demonstration)
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hash to float values
        embedding = []
        for i in range(0, len(text_hash), 2):
            hex_pair = text_hash[i:i+2]
            float_val = int(hex_pair, 16) / 255.0  # Normalize to 0-1
            embedding.append(float_val)
        
        # Pad or truncate to desired dimension
        while len(embedding) < self.embedding_dim:
            embedding.extend(embedding[:self.embedding_dim - len(embedding)])
        
        return embedding[:self.embedding_dim]
    
    def _calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        if len(embedding1) != len(embedding2):
            return 0.0
        
        # Cosine similarity
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        norm1 = sum(a * a for a in embedding1) ** 0.5
        norm2 = sum(b * b for b in embedding2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _should_store_as_memory(self, user_input: str, ai_response: str) -> bool:
        """Determine if a conversation should be stored as a memory."""
        # Store if it contains important keywords or is long enough
        important_keywords = [
            'remember', 'important', 'note', 'save', 'store', 'don\'t forget',
            'plan', 'goal', 'deadline', 'appointment', 'meeting'
        ]
        
        combined_text = f"{user_input} {ai_response}".lower()
        
        # Store if contains important keywords or is substantial
        return (
            any(keyword in combined_text for keyword in important_keywords) or
            len(combined_text) > 200
        )
    
    async def _save_memory(self, memory: MemoryEntry):
        """Save a memory to disk."""
        try:
            memory_file = os.path.join(self.storage_path, f"{memory.id}.json")
            memory_data = {
                'id': memory.id,
                'content': memory.content,
                'embedding': memory.embedding,
                'metadata': memory.metadata,
                'timestamp': memory.timestamp.isoformat(),
                'access_count': memory.access_count,
                'last_accessed': memory.last_accessed.isoformat() if memory.last_accessed else None,
                'tags': memory.tags,
                'importance': memory.importance
            }
            
            async with aiofiles.open(memory_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(memory_data, indent=2, ensure_ascii=False))
                
        except Exception as e:
            logger.error(f"❌ Failed to save memory {memory.id}: {e}")
    
    async def _load_memories(self):
        """Load memories from disk."""
        try:
            if not os.path.exists(self.storage_path):
                return
            
            loaded_count = 0
            
            for filename in os.listdir(self.storage_path):
                if filename.endswith('.json') and filename.startswith('mem_'):
                    try:
                        memory_file = os.path.join(self.storage_path, filename)
                        
                        async with aiofiles.open(memory_file, 'r', encoding='utf-8') as f:
                            content = await f.read()
                            memory_data = json.loads(content)
                        
                        # Reconstruct memory entry
                        memory = MemoryEntry(
                            id=memory_data['id'],
                            content=memory_data['content'],
                            embedding=memory_data.get('embedding'),
                            metadata=memory_data.get('metadata', {}),
                            timestamp=datetime.fromisoformat(memory_data['timestamp']),
                            access_count=memory_data.get('access_count', 0),
                            last_accessed=datetime.fromisoformat(memory_data['last_accessed']) if memory_data.get('last_accessed') else None,
                            tags=memory_data.get('tags', []),
                            importance=memory_data.get('importance', 0.5)
                        )
                        
                        self.memories[memory.id] = memory
                        
                        # Update tags index
                        for tag in memory.tags:
                            if tag not in self.tags_index:
                                self.tags_index[tag] = []
                            self.tags_index[tag].append(memory.id)
                        
                        loaded_count += 1
                        
                    except Exception as e:
                        logger.warning(f"Failed to load memory from {filename}: {e}")
            
            logger.info(f"📚 Loaded {loaded_count} memories from disk")
            
        except Exception as e:
            logger.error(f"❌ Failed to load memories: {e}")
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        if not self.memories:
            return {'total_memories': 0}
        
        total_memories = len(self.memories)
        avg_importance = sum(m.importance for m in self.memories.values()) / total_memories
        total_access_count = sum(m.access_count for m in self.memories.values())
        
        # Tag statistics
        tag_counts = {}
        for memory in self.memories.values():
            for tag in memory.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        return {
            'total_memories': total_memories,
            'average_importance': round(avg_importance, 3),
            'total_access_count': total_access_count,
            'conversation_history_length': len(self.conversation_history),
            'tag_distribution': tag_counts,
            'storage_path': self.storage_path,
            'memory_usage': f"{total_memories}/{self.max_memory_entries}"
        }
    
    async def export_memories(self, export_path: str, 
                            tags: List[str] = None,
                            min_importance: float = 0.0) -> bool:
        """Export memories to a file."""
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'filter_tags': tags,
                'min_importance': min_importance,
                'memories': []
            }
            
            for memory in self.memories.values():
                # Apply filters
                if tags and not any(tag in memory.tags for tag in tags):
                    continue
                if memory.importance < min_importance:
                    continue
                
                memory_data = {
                    'id': memory.id,
                    'content': memory.content,
                    'metadata': memory.metadata,
                    'timestamp': memory.timestamp.isoformat(),
                    'tags': memory.tags,
                    'importance': memory.importance,
                    'access_count': memory.access_count
                }
                export_data['memories'].append(memory_data)
            
            async with aiofiles.open(export_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(export_data, indent=2, ensure_ascii=False))
            
            logger.info(f"📤 Exported {len(export_data['memories'])} memories to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to export memories: {e}")
            return False
