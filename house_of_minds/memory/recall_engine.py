"""
True Recall - Main Recall Engine

Central orchestrator for the True Recall memory system, coordinating all components
for comprehensive memory storage, retrieval, analysis, and reflection.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, date, timedelta
from pathlib import Path
import json

# Import memory system components
try:
    # Try relative imports first (for package use)
    from .emotion_tagger import EmotionTagger
    from .salience_scoring import SalienceScorer
    from .memory_graph import MemoryGraph
    from .reflection_agent import ReflectionAgent
    from ..storage.memory_store import MemoryStore
except ImportError:
    # Fall back to absolute imports (for direct execution)
    from memory.emotion_tagger import EmotionTagger
    from memory.salience_scoring import SalienceScorer
    from memory.memory_graph import MemoryGraph
    from memory.reflection_agent import ReflectionAgent
    from storage.memory_store import MemoryStore

logger = logging.getLogger(__name__)

class RecallEngine:
    """
    Main orchestrator for the True Recall memory system.
    
    Coordinates emotion analysis, salience scoring, graph relationships,
    memory storage, and reflection generation for comprehensive memory management.
    """
    
    def __init__(self, storage_path: str = "memory_data/memories.json", auto_reflect: bool = True):
        """
        Initialize the recall engine with all components.
        
        Args:
            storage_path: Path for memory storage
            auto_reflect: Whether to automatically generate daily reflections
        """
        self.storage_path = storage_path
        self.auto_reflect = auto_reflect
        
        # Initialize components
        self.emotion_tagger = EmotionTagger()
        self.salience_scorer = SalienceScorer()
        self.memory_graph = MemoryGraph()
        self.reflection_agent = ReflectionAgent()
        self.memory_store = MemoryStore(storage_path)
        
        # Configuration
        self.config = {
            'auto_save': True,
            'enable_graph': True,
            'enable_reflections': auto_reflect,
            'reflection_schedule': 'daily',  # daily, weekly, or manual
            'max_memory_age_days': 365,
            'graph_max_connections': 50,
            'salience_threshold': 0.1
        }
        
        # Runtime state
        self.stats = {
            'total_memories_stored': 0,
            'last_reflection_date': None,
            'processing_errors': 0,
            'system_start_time': datetime.now()
        }
        
        logger.info("🧠 True Recall Engine initialized successfully")
    
    def store_memory(
        self, 
        content: str, 
        actor: str = 'user', 
        event_type: str = 'interaction',
        metadata: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store a new memory with comprehensive analysis.
        
        Args:
            content: The content to remember
            actor: Who/what generated this memory (user, dolphin, system)
            event_type: Type of event (interaction, thought, observation, etc.)
            metadata: Additional metadata
            context: Contextual information for analysis
            
        Returns:
            Dict containing the stored memory with analysis results
        """
        try:
            # Create base memory event
            memory_event = {
                'id': self._generate_memory_id(),
                'content': content,
                'actor': actor,
                'event_type': event_type,
                'timestamp': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            # Add context information
            if context:
                memory_event['context'] = context
            
            # Perform emotion analysis
            emotion_analysis = self.emotion_tagger.analyze_text(content, context)
            memory_event['emotion_analysis'] = emotion_analysis
            
            # Calculate salience score
            historical_events = self._get_recent_events_for_salience(days=7, limit=100)
            salience_analysis = self.salience_scorer.calculate_salience(
                memory_event, 
                historical_events, 
                context
            )
            memory_event['salience_analysis'] = salience_analysis
            
            # Store in persistent storage
            if self.config['auto_save']:
                success = self.memory_store.store_event(memory_event)
                if not success:
                    logger.error("❌ Failed to store memory in persistent storage")
                    return memory_event
            
            # Add to memory graph for relationship discovery
            if self.config['enable_graph']:
                self.memory_graph.add_event(memory_event)
            
            # Update statistics
            self.stats['total_memories_stored'] += 1
            
            # Check for automatic reflection triggers
            if self.config['enable_reflections'] and self.config['reflection_schedule'] == 'daily':
                self._check_daily_reflection_trigger()
            
            logger.debug(f"💾 Stored memory: {memory_event['id']}")
            
            return memory_event
            
        except Exception as e:
            logger.error(f"❌ Error storing memory: {e}")
            self.stats['processing_errors'] += 1
            
            # Return minimal memory event on error
            return {
                'id': self._generate_memory_id(),
                'content': content,
                'actor': actor,
                'event_type': event_type,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def recall_memories(
        self,
        query: Optional[str] = None,
        actor: Optional[str] = None,
        emotion: Optional[str] = None,
        date_range: Optional[Tuple[str, str]] = None,
        min_salience: Optional[float] = None,
        limit: int = 20,
        include_related: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Recall memories based on various criteria.
        
        Args:
            query: Text query to search for
            actor: Filter by actor
            emotion: Filter by emotion
            date_range: Tuple of (start_date, end_date)
            min_salience: Minimum salience score
            limit: Maximum number of results
            include_related: Whether to include related memories
            
        Returns:
            List of matching memories with relevance scores
        """
        try:
            # Basic retrieval from storage
            memories = self.memory_store.get_events(
                actor=actor,
                date_range=date_range,
                emotion_tags=[emotion] if emotion else None,
                min_salience=min_salience,
                limit=limit * 2  # Get more to allow for filtering
            )
            
            # Text search if query provided
            if query:
                query_memories = self.memory_store.search_events_by_content(query, limit * 2)
                # Merge and deduplicate
                memory_ids = {m['id'] for m in memories}
                for mem in query_memories:
                    if mem['id'] not in memory_ids:
                        memories.append(mem)
            
            # Add related memories from graph
            if include_related and self.config['enable_graph']:
                enhanced_memories = []
                for memory in memories:
                    enhanced_memory = memory.copy()
                    
                    # Get related memories
                    related = self.memory_graph.get_related_events(
                        memory['id'], 
                        max_depth=2, 
                        min_weight=0.3, 
                        max_results=5
                    )
                    enhanced_memory['related_memories'] = related
                    
                    enhanced_memories.append(enhanced_memory)
                
                memories = enhanced_memories
            
            # Sort by relevance (salience + recency)
            memories = self._rank_memories_by_relevance(memories, query)
            
            return memories[:limit]
            
        except Exception as e:
            logger.error(f"❌ Error recalling memories: {e}")
            return []
    
    def get_daily_reflection(self, target_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Get or generate a daily reflection for a specific date.
        
        Args:
            target_date: Date to reflect on (defaults to today)
            
        Returns:
            Dict containing the daily reflection
        """
        if target_date is None:
            target_date = date.today()
        
        try:
            # Check if reflection already exists
            existing_reflection = self.memory_store.get_reflection(
                target_date.isoformat(), 
                'daily'
            )
            
            if existing_reflection:
                return existing_reflection
            
            # Generate new reflection
            daily_events = self.memory_store.get_events_for_date(target_date)
            
            reflection = self.reflection_agent.generate_daily_reflection(
                daily_events, 
                target_date
            )
            
            # Store the reflection
            if self.config['auto_save']:
                self.memory_store.store_reflection(reflection)
            
            return reflection
            
        except Exception as e:
            logger.error(f"❌ Error getting daily reflection: {e}")
            return {'error': str(e), 'date': target_date.isoformat()}
    
    def get_weekly_reflection(self, start_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Get or generate a weekly reflection.
        
        Args:
            start_date: Start of the week (defaults to Monday of current week)
            
        Returns:
            Dict containing the weekly reflection
        """
        if start_date is None:
            today = date.today()
            start_date = today - timedelta(days=today.weekday())
        
        try:
            # Check if reflection already exists
            existing_reflection = self.memory_store.get_reflection(
                start_date.isoformat(), 
                'weekly'
            )
            
            if existing_reflection:
                return existing_reflection
            
            # Gather daily reflections for the week
            daily_reflections = []
            for i in range(7):
                day = start_date + timedelta(days=i)
                daily_reflection = self.get_daily_reflection(day)
                if daily_reflection and 'error' not in daily_reflection:
                    daily_reflections.append(daily_reflection)
            
            # Generate weekly reflection
            weekly_reflection = self.reflection_agent.generate_weekly_reflection(
                daily_reflections, 
                start_date
            )
            
            # Store the reflection
            if self.config['auto_save']:
                self.memory_store.store_reflection(weekly_reflection)
            
            return weekly_reflection
            
        except Exception as e:
            logger.error(f"❌ Error getting weekly reflection: {e}")
            return {'error': str(e), 'start_date': start_date.isoformat()}
    
    def analyze_patterns(self, days: int = 30) -> Dict[str, Any]:
        """
        Analyze patterns across recent memories.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict containing pattern analysis
        """
        try:
            # Get recent events
            recent_events = self.memory_store.get_recent_events(days=days, limit=500)
            
            # Use reflection agent for pattern identification
            patterns = self.reflection_agent.identify_patterns(recent_events, days)
            
            # Add graph-based insights
            if self.config['enable_graph']:
                graph_stats = self.memory_graph.get_graph_statistics()
                patterns['graph_insights'] = {
                    'central_memories': self.memory_graph.get_central_events(limit=5),
                    'conversation_threads': len(self.memory_graph.find_conversation_threads()),
                    'semantic_clusters': len(self.memory_graph.find_semantic_clusters()),
                    'graph_statistics': graph_stats
                }
            
            return patterns
            
        except Exception as e:
            logger.error(f"❌ Error analyzing patterns: {e}")
            return {'error': str(e)}
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive memory system statistics."""
        try:
            # Storage statistics
            storage_stats = self.memory_store.get_storage_stats()
            
            # Graph statistics
            graph_stats = {}
            if self.config['enable_graph']:
                graph_stats = self.memory_graph.get_graph_statistics()
            
            # Runtime statistics
            runtime_stats = self.stats.copy()
            uptime = datetime.now() - self.stats['system_start_time']
            runtime_stats['uptime_hours'] = round(uptime.total_seconds() / 3600, 2)
            
            return {
                'storage': storage_stats,
                'graph': graph_stats,
                'runtime': runtime_stats,
                'configuration': self.config,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting statistics: {e}")
            return {'error': str(e)}
    
    def update_configuration(self, config_updates: Dict[str, Any]) -> bool:
        """
        Update system configuration.
        
        Args:
            config_updates: Dict of configuration keys to update
            
        Returns:
            bool: True if successful
        """
        try:
            for key, value in config_updates.items():
                if key in self.config:
                    self.config[key] = value
                    logger.info(f"⚙️ Updated config: {key} = {value}")
                else:
                    logger.warning(f"⚠️ Unknown config key: {key}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating configuration: {e}")
            return False
    
    def backup_memories(self, backup_path: str) -> bool:
        """
        Create a backup of all memories.
        
        Args:
            backup_path: Path for the backup file
            
        Returns:
            bool: True if successful
        """
        try:
            success = self.memory_store.backup_to_file(backup_path)
            if success:
                logger.info(f"💾 Memory backup created at {backup_path}")
            return success
            
        except Exception as e:
            logger.error(f"❌ Error creating backup: {e}")
            return False
    
    def restore_memories(self, backup_path: str) -> bool:
        """
        Restore memories from a backup.
        
        Args:
            backup_path: Path to the backup file
            
        Returns:
            bool: True if successful
        """
        try:
            success = self.memory_store.restore_from_backup(backup_path)
            if success:
                # Rebuild memory graph
                if self.config['enable_graph']:
                    self._rebuild_memory_graph()
                logger.info(f"📥 Memories restored from {backup_path}")
            return success
            
        except Exception as e:
            logger.error(f"❌ Error restoring backup: {e}")
            return False
    
    def cleanup_old_memories(self, days_to_keep: int = 365) -> int:
        """
        Clean up old memories beyond the retention period.
        
        Args:
            days_to_keep: Number of days to keep
            
        Returns:
            int: Number of memories removed
        """
        try:
            removed_count = self.memory_store.cleanup_old_events(days_to_keep)
            
            # Rebuild graph after cleanup
            if removed_count > 0 and self.config['enable_graph']:
                self._rebuild_memory_graph()
            
            logger.info(f"🧹 Cleaned up {removed_count} old memories")
            return removed_count
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up memories: {e}")
            return 0
    
    def close(self):
        """Close the recall engine and cleanup resources."""
        try:
            self.memory_store.close()
            logger.info("🔒 True Recall Engine closed")
        except Exception as e:
            logger.error(f"❌ Error closing recall engine: {e}")
    
    # Private helper methods
    
    def _generate_memory_id(self) -> str:
        """Generate a unique memory ID."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        return f"memory_{timestamp}"
    
    def _get_recent_events_for_salience(self, days: int = 7, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent events for salience calculation context."""
        try:
            return self.memory_store.get_recent_events(days=days, limit=limit)
        except Exception as e:
            logger.error(f"❌ Error getting recent events: {e}")
            return []
    
    def _rank_memories_by_relevance(self, memories: List[Dict[str, Any]], query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Rank memories by relevance considering multiple factors."""
        try:
            for memory in memories:
                relevance_score = 0.0
                
                # Salience score (40% weight)
                salience_data = memory.get('salience_analysis', {})
                salience_score = salience_data.get('salience_score', 0.5)
                relevance_score += salience_score * 0.4
                
                # Recency (30% weight)
                timestamp_str = memory.get('timestamp', memory.get('created_at', ''))
                if timestamp_str:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        hours_ago = (datetime.now() - timestamp.replace(tzinfo=None)).total_seconds() / 3600
                        recency_score = max(0, 1 - (hours_ago / (24 * 7)))  # Decay over a week
                        relevance_score += recency_score * 0.3
                    except:
                        pass
                
                # Emotional intensity (20% weight)
                emotion_data = memory.get('emotion_analysis', {})
                if emotion_data:
                    intensity = emotion_data.get('emotional_intensity', 0)
                    relevance_score += intensity * 0.2
                
                # Query relevance (10% weight)
                if query:
                    content = memory.get('content', '').lower()
                    query_words = query.lower().split()
                    matches = sum(1 for word in query_words if word in content)
                    query_relevance = matches / len(query_words) if query_words else 0
                    relevance_score += query_relevance * 0.1
                
                memory['relevance_score'] = round(relevance_score, 4)
            
            # Sort by relevance score
            memories.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            
            return memories
            
        except Exception as e:
            logger.error(f"❌ Error ranking memories: {e}")
            return memories
    
    def _check_daily_reflection_trigger(self):
        """Check if a daily reflection should be generated."""
        try:
            today = date.today()
            yesterday = today - timedelta(days=1)
            
            # Check if we need to generate yesterday's reflection
            if (self.stats['last_reflection_date'] is None or 
                self.stats['last_reflection_date'] < yesterday.isoformat()):
                
                # Generate reflection for yesterday (if it has events)
                yesterday_events = self.memory_store.get_events_for_date(yesterday)
                if yesterday_events:
                    reflection = self.get_daily_reflection(yesterday)
                    if reflection and 'error' not in reflection:
                        self.stats['last_reflection_date'] = yesterday.isoformat()
                        logger.info(f"📔 Auto-generated daily reflection for {yesterday}")
                
        except Exception as e:
            logger.error(f"❌ Error checking reflection trigger: {e}")
    
    def _rebuild_memory_graph(self):
        """Rebuild the memory graph from stored events."""
        try:
            # Clear existing graph
            self.memory_graph = MemoryGraph()
            
            # Reload all events
            all_events = self.memory_store.get_events(limit=1000)  # Limit for performance
            
            for event in all_events:
                self.memory_graph.add_event(event)
            
            logger.info(f"🕸️ Rebuilt memory graph with {len(all_events)} events")
            
        except Exception as e:
            logger.error(f"❌ Error rebuilding memory graph: {e}")
    
    # Context managers and async support
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    async def store_memory_async(self, *args, **kwargs) -> Dict[str, Any]:
        """Async version of store_memory."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.store_memory, *args, **kwargs)
    
    async def recall_memories_async(self, *args, **kwargs) -> List[Dict[str, Any]]:
        """Async version of recall_memories."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.recall_memories, *args, **kwargs)

# Convenience functions

def create_recall_engine(storage_path: str = "memory_data/memories.json", auto_reflect: bool = True) -> RecallEngine:
    """Create and return a recall engine instance."""
    return RecallEngine(storage_path, auto_reflect)

def quick_memory_store(content: str, actor: str = 'user', storage_path: str = "memory_data/memories.json") -> Dict[str, Any]:
    """Quick function to store a single memory."""
    with RecallEngine(storage_path) as engine:
        return engine.store_memory(content, actor)

def quick_memory_recall(query: str, limit: int = 10, storage_path: str = "memory_data/memories.json") -> List[Dict[str, Any]]:
    """Quick function to recall memories."""
    with RecallEngine(storage_path) as engine:
        return engine.recall_memories(query=query, limit=limit)
