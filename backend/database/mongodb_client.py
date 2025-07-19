# mongodb_client.py
# MongoDB client for EmotionalAI data persistence

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import motor.motor_asyncio

logger = logging.getLogger(__name__)

class EmotionalAIMongoDB:
    """MongoDB client for EmotionalAI data persistence"""
    
    def __init__(self, connection_string: str = "mongodb://localhost:27017/", database_name: str = "emotional_ai"):
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.db = None
        self.is_connected = False
        
        # Collection names
        self.collections = {
            'memories': 'memories',
            'threads': 'threads',
            'relationships': 'relationships',
            'biometrics': 'biometrics',
            'avatars': 'avatars',
            'sessions': 'sessions',
            'analytics': 'analytics'
        }
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            # Use motor for async MongoDB operations
            self.client = motor.motor_asyncio.AsyncIOMotorClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000
            )
            
            # Test connection
            await self.client.admin.command('ping')
            
            self.db = self.client[self.database_name]
            self.is_connected = True
            
            # Create indexes for better performance
            await self._create_indexes()
            
            logger.info(f"Connected to MongoDB database: {self.database_name}")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self.is_connected = False
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Memories collection indexes
            memories_collection = self.db[self.collections['memories']]
            await memories_collection.create_index([("user_id", 1)])
            await memories_collection.create_index([("tags", 1)])
            await memories_collection.create_index([("memory_type", 1)])
            await memories_collection.create_index([("created_at", -1)])
            await memories_collection.create_index([("emotional_tags", 1)])
            
            # Threads collection indexes
            threads_collection = self.db[self.collections['threads']]
            await threads_collection.create_index([("user_id", 1)])
            await threads_collection.create_index([("thread_id", 1)])
            await threads_collection.create_index([("created_at", -1)])
            await threads_collection.create_index([("tags", 1)])
            
            # Relationships collection indexes
            relationships_collection = self.db[self.collections['relationships']]
            await relationships_collection.create_index([("user_id", 1)])
            await relationships_collection.create_index([("persona", 1)])
            await relationships_collection.create_index([("created_at", -1)])
            
            # Biometrics collection indexes
            biometrics_collection = self.db[self.collections['biometrics']]
            await biometrics_collection.create_index([("user_id", 1)])
            await biometrics_collection.create_index([("timestamp", -1)])
            
            # Sessions collection indexes
            sessions_collection = self.db[self.collections['sessions']]
            await sessions_collection.create_index([("user_id", 1)])
            await sessions_collection.create_index([("session_id", 1)])
            await sessions_collection.create_index([("created_at", -1)])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    # Memory Management
    async def store_memory(self, memory_data: Dict[str, Any]) -> str:
        """Store a new memory with tagging and metadata"""
        try:
            if not self.is_connected:
                raise Exception("MongoDB not connected")
            
            collection = self.db[self.collections['memories']]
            
            # Prepare memory document
            memory_doc = {
                "user_id": memory_data.get("user_id"),
                "persona": memory_data.get("persona", "mia"),
                "title": memory_data.get("title", "Untitled Memory"),
                "content": memory_data.get("content", ""),
                "memory_type": memory_data.get("memory_type", "general"),
                "emotional_tags": memory_data.get("emotional_tags", []),
                "tags": memory_data.get("tags", []),
                "trust_level": memory_data.get("trust_level", 0.5),
                "importance": memory_data.get("importance", 0.5),
                "context": memory_data.get("context", {}),
                "metadata": {
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                    "version": 1,
                    "source": memory_data.get("source", "user_input")
                },
                "relationships": memory_data.get("relationships", []),
                "biometric_context": memory_data.get("biometric_context", {}),
                "location_context": memory_data.get("location_context", {}),
                "mood_context": memory_data.get("mood_context", {})
            }
            
            result = await collection.insert_one(memory_doc)
            memory_id = str(result.inserted_id)
            
            logger.info(f"Memory stored successfully: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            raise
    
    async def update_memory(self, memory_id: str, update_data: Dict[str, Any]) -> bool:
        """Update an existing memory"""
        try:
            if not self.is_connected:
                raise Exception("MongoDB not connected")
            
            collection = self.db[self.collections['memories']]
            
            # Prepare update document
            update_doc = {
                "$set": {
                    "title": update_data.get("title"),
                    "content": update_data.get("content"),
                    "emotional_tags": update_data.get("emotional_tags"),
                    "tags": update_data.get("tags"),
                    "trust_level": update_data.get("trust_level"),
                    "importance": update_data.get("importance"),
                    "context": update_data.get("context"),
                    "metadata.updated_at": datetime.now(),
                    "metadata.version": update_data.get("version", 1)
                }
            }
            
            result = await collection.update_one(
                {"_id": ObjectId(memory_id)},
                update_doc
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Memory updated successfully: {memory_id}")
            else:
                logger.warning(f"Memory not found for update: {memory_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating memory: {e}")
            raise
    
    async def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific memory by ID"""
        try:
            if not self.is_connected:
                raise Exception("MongoDB not connected")
            
            collection = self.db[self.collections['memories']]
            
            memory_doc = await collection.find_one({"_id": ObjectId(memory_id)})
            
            if memory_doc:
                # Convert ObjectId to string for JSON serialization
                memory_doc["_id"] = str(memory_doc["_id"])
                return memory_doc
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving memory: {e}")
            raise
    
    async def search_memories(self, user_id: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search memories with various filters"""
        try:
            if not self.is_connected:
                raise Exception("MongoDB not connected")
            
            collection = self.db[self.collections['memories']]
            
            # Build search filter
            search_filter = {"user_id": user_id}
            
            if query.get("tags"):
                search_filter["tags"] = {"$in": query["tags"]}
            
            if query.get("emotional_tags"):
                search_filter["emotional_tags"] = {"$in": query["emotional_tags"]}
            
            if query.get("memory_type"):
                search_filter["memory_type"] = query["memory_type"]
            
            if query.get("persona"):
                search_filter["persona"] = query["persona"]
            
            if query.get("date_range"):
                date_range = query["date_range"]
                search_filter["metadata.created_at"] = {
                    "$gte": date_range["start"],
                    "$lte": date_range["end"]
                }
            
            # Execute search
            cursor = collection.find(search_filter).sort("metadata.created_at", -1)
            
            memories = []
            async for memory in cursor:
                memory["_id"] = str(memory["_id"])
                memories.append(memory)
            
            logger.info(f"Found {len(memories)} memories for user {user_id}")
            return memories
            
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            raise
    
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory"""
        try:
            if not self.is_connected:
                raise Exception("MongoDB not connected")
            
            collection = self.db[self.collections['memories']]
            
            result = await collection.delete_one({"_id": ObjectId(memory_id)})
            
            success = result.deleted_count > 0
            if success:
                logger.info(f"Memory deleted successfully: {memory_id}")
            else:
                logger.warning(f"Memory not found for deletion: {memory_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting memory: {e}")
            raise
    
    # Thread Memory Management
    async def store_thread_memory(self, thread_data: Dict[str, Any]) -> str:
        """Store thread memory for development threads"""
        try:
            if not self.is_connected:
                raise Exception("MongoDB not connected")
            
            collection = self.db[self.collections['threads']]
            
            # Prepare thread document
            thread_doc = {
                "user_id": thread_data.get("user_id"),
                "thread_id": thread_data.get("thread_id"),
                "persona": thread_data.get("persona", "mia"),
                "title": thread_data.get("title", "Development Thread"),
                "messages": thread_data.get("messages", []),
                "context": thread_data.get("context", {}),
                "tags": thread_data.get("tags", []),
                "development_phase": thread_data.get("development_phase", "planning"),
                "status": thread_data.get("status", "active"),
                "metadata": {
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                    "message_count": len(thread_data.get("messages", [])),
                    "last_activity": datetime.now()
                },
                "memory_references": thread_data.get("memory_references", []),
                "relationship_context": thread_data.get("relationship_context", {}),
                "biometric_context": thread_data.get("biometric_context", {})
            }
            
            result = await collection.insert_one(thread_doc)
            thread_id = str(result.inserted_id)
            
            logger.info(f"Thread memory stored successfully: {thread_id}")
            return thread_id
            
        except Exception as e:
            logger.error(f"Error storing thread memory: {e}")
            raise
    
    async def update_thread_memory(self, thread_id: str, update_data: Dict[str, Any]) -> bool:
        """Update thread memory"""
        try:
            if not self.is_connected:
                raise Exception("MongoDB not connected")
            
            collection = self.db[self.collections['threads']]
            
            # Prepare update document
            update_doc = {
                "$set": {
                    "messages": update_data.get("messages"),
                    "context": update_data.get("context"),
                    "tags": update_data.get("tags"),
                    "development_phase": update_data.get("development_phase"),
                    "status": update_data.get("status"),
                    "metadata.updated_at": datetime.now(),
                    "metadata.message_count": len(update_data.get("messages", [])),
                    "metadata.last_activity": datetime.now(),
                    "memory_references": update_data.get("memory_references"),
                    "relationship_context": update_data.get("relationship_context"),
                    "biometric_context": update_data.get("biometric_context")
                }
            }
            
            result = await collection.update_one(
                {"_id": ObjectId(thread_id)},
                update_doc
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Thread memory updated successfully: {thread_id}")
            else:
                logger.warning(f"Thread memory not found for update: {thread_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating thread memory: {e}")
            raise
    
    async def get_thread_memory(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve thread memory by ID"""
        try:
            if not self.is_connected:
                raise Exception("MongoDB not connected")
            
            collection = self.db[self.collections['threads']]
            
            thread_doc = await collection.find_one({"_id": ObjectId(thread_id)})
            
            if thread_doc:
                thread_doc["_id"] = str(thread_doc["_id"])
                return thread_doc
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving thread memory: {e}")
            raise
    
    async def get_user_threads(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all threads for a user"""
        try:
            if not self.is_connected:
                raise Exception("MongoDB not connected")
            
            collection = self.db[self.collections['threads']]
            
            cursor = collection.find({"user_id": user_id}).sort("metadata.last_activity", -1)
            
            threads = []
            async for thread in cursor:
                thread["_id"] = str(thread["_id"])
                threads.append(thread)
            
            logger.info(f"Found {len(threads)} threads for user {user_id}")
            return threads
            
        except Exception as e:
            logger.error(f"Error retrieving user threads: {e}")
            raise
    
    # Relationship Data Management
    async def store_relationship_data(self, relationship_data: Dict[str, Any]) -> str:
        """Store relationship data and insights"""
        try:
            if not self.is_connected:
                raise Exception("MongoDB not connected")
            
            collection = self.db[self.collections['relationships']]
            
            relationship_doc = {
                "user_id": relationship_data.get("user_id"),
                "persona": relationship_data.get("persona", "mia"),
                "health_score": relationship_data.get("health_score", 0.5),
                "insights": relationship_data.get("insights", []),
                "recommendations": relationship_data.get("recommendations", []),
                "growth_areas": relationship_data.get("growth_areas", []),
                "milestones": relationship_data.get("milestones", []),
                "conflicts": relationship_data.get("conflicts", []),
                "communication_patterns": relationship_data.get("communication_patterns", {}),
                "emotional_sync": relationship_data.get("emotional_sync", {}),
                "metadata": {
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                    "analysis_count": relationship_data.get("analysis_count", 1)
                }
            }
            
            result = await collection.insert_one(relationship_doc)
            relationship_id = str(result.inserted_id)
            
            logger.info(f"Relationship data stored successfully: {relationship_id}")
            return relationship_id
            
        except Exception as e:
            logger.error(f"Error storing relationship data: {e}")
            raise
    
    # Biometric Data Management
    async def store_biometric_data(self, biometric_data: Dict[str, Any]) -> str:
        """Store biometric data"""
        try:
            if not self.is_connected:
                raise Exception("MongoDB not connected")
            
            collection = self.db[self.collections['biometrics']]
            
            biometric_doc = {
                "user_id": biometric_data.get("user_id"),
                "timestamp": datetime.now(),
                "heart_rate": biometric_data.get("heart_rate"),
                "hrv": biometric_data.get("hrv"),
                "breathing_rate": biometric_data.get("breathing_rate"),
                "stress_level": biometric_data.get("stress_level"),
                "energy_level": biometric_data.get("energy_level"),
                "romantic_sync": biometric_data.get("romantic_sync", {}),
                "context": biometric_data.get("context", "general"),
                "persona": biometric_data.get("persona", "mia"),
                "session_id": biometric_data.get("session_id")
            }
            
            result = await collection.insert_one(biometric_doc)
            biometric_id = str(result.inserted_id)
            
            logger.info(f"Biometric data stored successfully: {biometric_id}")
            return biometric_id
            
        except Exception as e:
            logger.error(f"Error storing biometric data: {e}")
            raise
    
    # Session Management
    async def store_session_data(self, session_data: Dict[str, Any]) -> str:
        """Store session data"""
        try:
            if not self.is_connected:
                raise Exception("MongoDB not connected")
            
            collection = self.db[self.collections['sessions']]
            
            session_doc = {
                "user_id": session_data.get("user_id"),
                "session_id": session_data.get("session_id"),
                "persona": session_data.get("persona", "mia"),
                "start_time": datetime.now(),
                "end_time": None,
                "duration": 0,
                "features_used": session_data.get("features_used", []),
                "interaction_count": session_data.get("interaction_count", 0),
                "mood_changes": session_data.get("mood_changes", []),
                "memory_creations": session_data.get("memory_creations", 0),
                "vr_sessions": session_data.get("vr_sessions", []),
                "haptic_triggers": session_data.get("haptic_triggers", []),
                "voice_interactions": session_data.get("voice_interactions", []),
                "status": "active"
            }
            
            result = await collection.insert_one(session_doc)
            session_id = str(result.inserted_id)
            
            logger.info(f"Session data stored successfully: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error storing session data: {e}")
            raise
    
    async def end_session(self, session_id: str) -> bool:
        """End a session and calculate duration"""
        try:
            if not self.is_connected:
                raise Exception("MongoDB not connected")
            
            collection = self.db[self.collections['sessions']]
            
            # Get session start time
            session_doc = await collection.find_one({"_id": ObjectId(session_id)})
            if not session_doc:
                return False
            
            end_time = datetime.now()
            duration = (end_time - session_doc["start_time"]).total_seconds()
            
            # Update session
            result = await collection.update_one(
                {"_id": ObjectId(session_id)},
                {
                    "$set": {
                        "end_time": end_time,
                        "duration": duration,
                        "status": "completed"
                    }
                }
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Session ended successfully: {session_id}, duration: {duration}s")
            
            return success
            
        except Exception as e:
            logger.error(f"Error ending session: {e}")
            raise
    
    # Analytics and Insights
    async def store_analytics(self, analytics_data: Dict[str, Any]) -> str:
        """Store analytics data"""
        try:
            if not self.is_connected:
                raise Exception("MongoDB not connected")
            
            collection = self.db[self.collections['analytics']]
            
            analytics_doc = {
                "user_id": analytics_data.get("user_id"),
                "timestamp": datetime.now(),
                "event_type": analytics_data.get("event_type"),
                "event_data": analytics_data.get("event_data", {}),
                "persona": analytics_data.get("persona", "mia"),
                "session_id": analytics_data.get("session_id"),
                "performance_metrics": analytics_data.get("performance_metrics", {}),
                "user_behavior": analytics_data.get("user_behavior", {}),
                "feature_usage": analytics_data.get("feature_usage", {})
            }
            
            result = await collection.insert_one(analytics_doc)
            analytics_id = str(result.inserted_id)
            
            logger.info(f"Analytics data stored successfully: {analytics_id}")
            return analytics_id
            
        except Exception as e:
            logger.error(f"Error storing analytics data: {e}")
            raise

# Global MongoDB instance
mongodb_client = EmotionalAIMongoDB()

# Initialize function
async def initialize_mongodb():
    """Initialize MongoDB connection"""
    success = await mongodb_client.connect()
    if success:
        logger.info("MongoDB initialized successfully")
    else:
        logger.error("Failed to initialize MongoDB")
    return success 