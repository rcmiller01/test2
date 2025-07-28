"""
True Recall - Memory Store

Persistent storage backend using TinyDB for lightweight, file-based storage
of memory events, reflections, and metadata.
"""

import logging
import json
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import os

from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

logger = logging.getLogger(__name__)

class MemoryStore:
    """
    Persistent storage manager for True Recall memory events using TinyDB.
    
    Provides efficient storage and retrieval of memory events, daily reflections,
    and system metadata with built-in caching and JSON serialization.
    """
    
    def __init__(self, storage_path: str = "memory_data/memories.json"):
        """Initialize the memory store."""
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize TinyDB with caching
        self.db = TinyDB(
            str(self.storage_path),
            storage=CachingMiddleware(JSONStorage),
            sort_keys=True,
            indent=2
        )
        
        # Create tables
        self.events_table = self.db.table('events')
        self.reflections_table = self.db.table('reflections')
        self.metadata_table = self.db.table('metadata')
        
        # Create indexes for common queries
        self._initialize_metadata()
        
        logger.info(f"📁 Memory Store initialized at {self.storage_path}")
    
    def _initialize_metadata(self):
        """Initialize store metadata."""
        Query = self.db.query_class
        metadata = self.metadata_table.get(Query.type == 'store_info')
        
        if not metadata:
            self.metadata_table.insert({
                'type': 'store_info',
                'created_at': datetime.now().isoformat(),
                'version': '1.0.0',
                'total_events': 0,
                'last_backup': None
            })
        
        logger.info("📋 Store metadata initialized")
    
    def store_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Store a memory event.
        
        Args:
            event_data: Event data dictionary
            
        Returns:
            bool: True if successfully stored
        """
        try:
            # Ensure required fields
            if 'id' not in event_data:
                event_data['id'] = self._generate_event_id()
            
            if 'created_at' not in event_data:
                event_data['created_at'] = datetime.now().isoformat()
            
            # Store the event
            self.events_table.insert(event_data)
            
            # Update metadata
            self._update_event_count()
            
            logger.debug(f"📥 Stored event {event_data['id']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store event: {e}")
            return False
    
    def get_events(
        self,
        actor: Optional[str] = None,
        event_type: Optional[str] = None,
        date_range: Optional[tuple] = None,
        emotion_tags: Optional[List[str]] = None,
        min_salience: Optional[float] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve events based on various criteria.
        
        Args:
            actor: Filter by actor (user, dolphin, system)
            event_type: Filter by event type
            date_range: Tuple of (start_date, end_date) as datetime or ISO strings
            emotion_tags: List of emotions to filter by
            min_salience: Minimum salience score
            limit: Maximum number of events to return
            
        Returns:
            List of matching events
        """
        try:
            Event = Query()
            conditions = []
            
            # Build query conditions
            if actor:
                conditions.append(Event.actor == actor)
            
            if event_type:
                conditions.append(Event.event_type == event_type)
            
            if date_range:
                start_date, end_date = self._normalize_date_range(date_range)
                conditions.append(Event.timestamp >= start_date)
                conditions.append(Event.timestamp <= end_date)
            
            if emotion_tags:
                for emotion in emotion_tags:
                    conditions.append(Event.emotion_tags.any([emotion]))
            
            if min_salience is not None:
                conditions.append(Event.salience >= min_salience)
            
            # Execute query
            if conditions:
                query = conditions[0]
                for condition in conditions[1:]:
                    query = query & condition
                events = self.events_table.search(query)
            else:
                events = self.events_table.all()
            
            # Sort by timestamp (newest first)
            events.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Apply limit
            if limit:
                events = events[:limit]
            
            return events
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve events: {e}")
            return []
    
    def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific event by ID."""
        try:
            Event = Query()
            event = self.events_table.get(Event.id == event_id)
            return event
        except Exception as e:
            logger.error(f"❌ Failed to get event {event_id}: {e}")
            return None
    
    def update_event(self, event_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing event."""
        try:
            Event = Query()
            updates['updated_at'] = datetime.now().isoformat()
            
            result = self.events_table.update(updates, Event.id == event_id)
            return len(result) > 0
            
        except Exception as e:
            logger.error(f"❌ Failed to update event {event_id}: {e}")
            return False
    
    def store_reflection(self, reflection_data: Dict[str, Any]) -> bool:
        """Store a daily or weekly reflection."""
        try:
            if 'id' not in reflection_data:
                reflection_data['id'] = self._generate_reflection_id(reflection_data)
            
            if 'created_at' not in reflection_data:
                reflection_data['created_at'] = datetime.now().isoformat()
            
            # Check if reflection exists and update or insert
            Reflection = Query()
            existing = self.reflections_table.get(
                (Reflection.date == reflection_data.get('date')) &
                (Reflection.type == reflection_data.get('type', 'daily'))
            )
            
            if existing:
                reflection_data['updated_at'] = datetime.now().isoformat()
                self.reflections_table.update(reflection_data, 
                    (Reflection.date == reflection_data.get('date')) &
                    (Reflection.type == reflection_data.get('type', 'daily'))
                )
            else:
                self.reflections_table.insert(reflection_data)
            
            logger.info(f"📔 Stored reflection for {reflection_data.get('date')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store reflection: {e}")
            return False
    
    def get_reflection(self, date_str: str, reflection_type: str = 'daily') -> Optional[Dict[str, Any]]:
        """Get a reflection for a specific date."""
        try:
            Reflection = Query()
            reflection = self.reflections_table.get(
                (Reflection.date == date_str) &
                (Reflection.type == reflection_type)
            )
            return reflection
        except Exception as e:
            logger.error(f"❌ Failed to get reflection for {date_str}: {e}")
            return None
    
    def get_events_for_date(self, target_date: Union[str, date, datetime]) -> List[Dict[str, Any]]:
        """Get all events for a specific date."""
        if isinstance(target_date, (date, datetime)):
            date_str = target_date.strftime('%Y-%m-%d')
        else:
            date_str = target_date
        
        next_date = (datetime.strptime(date_str, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
        
        return self.get_events(date_range=(date_str, next_date))
    
    def get_recent_events(self, days: int = 7, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent events from the last N days."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        return self.get_events(
            date_range=(start_date.isoformat(), end_date.isoformat()),
            limit=limit
        )
    
    def search_events_by_content(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search events by content text."""
        try:
            Event = Query()
            events = self.events_table.search(Event.content.search(query, flags=0))
            
            # Sort by timestamp (newest first)
            events.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return events[:limit] if limit else events
            
        except Exception as e:
            logger.error(f"❌ Failed to search events: {e}")
            return []
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        try:
            total_events = len(self.events_table)
            total_reflections = len(self.reflections_table)
            
            # Get date range of events
            events = self.events_table.all()
            if events:
                timestamps = [e.get('timestamp', '') for e in events if e.get('timestamp')]
                timestamps.sort()
                oldest_event = timestamps[0] if timestamps else None
                newest_event = timestamps[-1] if timestamps else None
            else:
                oldest_event = newest_event = None
            
            # File size
            file_size = self.storage_path.stat().st_size if self.storage_path.exists() else 0
            
            return {
                'total_events': total_events,
                'total_reflections': total_reflections,
                'oldest_event': oldest_event,
                'newest_event': newest_event,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'storage_path': str(self.storage_path)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get storage stats: {e}")
            return {}
    
    def cleanup_old_events(self, days_to_keep: int = 90) -> int:
        """Remove events older than specified days."""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
            
            Event = Query()
            removed = self.events_table.remove(Event.timestamp < cutoff_date)
            
            logger.info(f"🧹 Cleaned up {len(removed)} old events")
            return len(removed)
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup events: {e}")
            return 0
    
    def backup_to_file(self, backup_path: str) -> bool:
        """Create a backup of the database."""
        try:
            backup_file = Path(backup_path)
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Create backup data
            backup_data = {
                'backup_created': datetime.now().isoformat(),
                'events': self.events_table.all(),
                'reflections': self.reflections_table.all(),
                'metadata': self.metadata_table.all()
            }
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Database backed up to {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to backup database: {e}")
            return False
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """Restore database from backup."""
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Clear current data
            self.events_table.truncate()
            self.reflections_table.truncate()
            self.metadata_table.truncate()
            
            # Restore data
            if 'events' in backup_data:
                self.events_table.insert_multiple(backup_data['events'])
            
            if 'reflections' in backup_data:
                self.reflections_table.insert_multiple(backup_data['reflections'])
            
            if 'metadata' in backup_data:
                self.metadata_table.insert_multiple(backup_data['metadata'])
            
            logger.info(f"📥 Database restored from {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to restore database: {e}")
            return False
    
    def _generate_event_id(self) -> str:
        """Generate a unique event ID."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        return f"event_{timestamp}"
    
    def _generate_reflection_id(self, reflection_data: Dict[str, Any]) -> str:
        """Generate a reflection ID."""
        date_str = reflection_data.get('date', datetime.now().strftime('%Y-%m-%d'))
        reflection_type = reflection_data.get('type', 'daily')
        return f"reflection_{reflection_type}_{date_str}"
    
    def _normalize_date_range(self, date_range: tuple) -> tuple:
        """Normalize date range to ISO strings."""
        start, end = date_range
        
        if isinstance(start, datetime):
            start = start.isoformat()
        elif isinstance(start, date):
            start = start.isoformat()
        
        if isinstance(end, datetime):
            end = end.isoformat()
        elif isinstance(end, date):
            end = end.isoformat()
        
        return start, end
    
    def _update_event_count(self):
        """Update the total event count in metadata."""
        try:
            Query = self.db.query_class
            total_events = len(self.events_table)
            
            self.metadata_table.update(
                {'total_events': total_events, 'last_updated': datetime.now().isoformat()},
                Query.type == 'store_info'
            )
        except Exception as e:
            logger.error(f"❌ Failed to update event count: {e}")
    
    def close(self):
        """Close the database connection."""
        try:
            self.db.close()
            logger.info("🔒 Memory store closed")
        except Exception as e:
            logger.error(f"❌ Failed to close memory store: {e}")

# Convenience function
def create_memory_store(storage_path: str = "memory_data/memories.json") -> MemoryStore:
    """Create and return a memory store instance."""
    return MemoryStore(storage_path)
