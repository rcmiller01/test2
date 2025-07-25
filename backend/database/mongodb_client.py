# mongodb_client.py
# MongoDB client for EmotionalAI data persistence

import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
from models.persona_state import PersonaState

class MongoDBClient:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.collections = {
            'personas': 'personas',
            'conversations': 'conversations',
            'biometrics': 'biometrics',
            'config': 'config',
            'memories': 'memories'
        }
        
    async def initialize(self):
        """Initialize MongoDB connection"""
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        self.client = AsyncIOMotorClient(mongodb_url)
        self.db = self.client.emotionalai
        
        # Ensure collections exist
        for collection_name in self.collections.values():
            if collection_name not in await self.db.list_collection_names():
                await self.db.create_collection(collection_name)
    
    async def create_persona(self, name: str = "", traits: Dict[str, float] = None) -> str:
        """Create a new persona"""
        if traits is None:
            traits = {"devotion": 0.9}
            
        persona_data = {
            "name": name,
            "traits": traits,
            "created_at": datetime.now(),
            "active": True
        }
        
        result = await self.db[self.collections['personas']].insert_one(persona_data)
        return str(result.inserted_id)
    
    async def get_active_persona(self) -> Optional[Dict]:
        """Get the currently active persona"""
        return await self.db[self.collections['personas']].find_one({"active": True})
    
    async def update_persona_name(self, persona_id: str, name: str) -> bool:
        """Update persona name"""
        result = await self.db[self.collections['personas']].update_one(
            {"_id": persona_id},
            {"$set": {"name": name, "updated_at": datetime.now()}}
        )
        return result.modified_count > 0
    
    async def activate_llm(self, llm_name: str) -> bool:
        """Activate a specific LLM"""
        # Store active LLM in config
        result = await self.db[self.collections['config']].update_one(
            {"key": "active_llm"},
            {"$set": {"key": "active_llm", "value": llm_name, "updated_at": datetime.now()}},
            upsert=True
        )
        return result.upserted_id is not None or result.modified_count > 0
    
    async def get_active_llm(self) -> str:
        """Get currently active LLM"""
        config = await self.db[self.collections['config']].find_one({"key": "active_llm"})
        return config["value"] if config else "mythomax"
    
    async def store_conversation(self, persona_id: str, message: str, response: str, emotion: str) -> str:
        """Store conversation in database"""
        conversation_data = {
            "persona_id": persona_id,
            "user_message": message,
            "ai_response": response,
            "emotion": emotion,
            "timestamp": datetime.now()
        }
        
        result = await self.db[self.collections['conversations']].insert_one(conversation_data)
        return str(result.inserted_id)
    
    async def store_biometrics(self, persona_id: str, biometric_data: Dict[str, Any]) -> str:
        """Store biometric data"""
        data = {
            "persona_id": persona_id,
            "data": biometric_data,
            "timestamp": datetime.now()
        }
        
        result = await self.db[self.collections['biometrics']].insert_one(data)
        return str(result.inserted_id)

# Global instance
mongodb_client = MongoDBClient()

async def initialize_mongodb():
    """Initialize MongoDB connection"""
    await mongodb_client.initialize()