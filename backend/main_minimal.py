"""
Minimal EmotionalAI Backend with LLM Orchestration System
Focus on testing LLM orchestration and chat functionality
"""

from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

# Import core systems
from backend.models.persona_state import PersonaState
from backend.llm.llm_client import LLMClientManager
from backend.database.mongodb_client import mongodb_client, initialize_mongodb
from backend.voice.voice_synthesizer import voice_synthesizer
from backend.avatar.avatar_system import avatar_system

# Pydantic models
class TextInput(BaseModel):
    text: str

class BiometricsInput(BaseModel):
    heart_rate: Optional[int] = None
    heart_rate_variability: Optional[float] = None
    temperature: Optional[float] = None
    motion_data: Optional[Dict[str, Any]] = None

# Global state
persona_state = PersonaState()
router = APIRouter()

# LLM Orchestrator
class LLMOrchestrator:
    def __init__(self):
        self.client_manager = LLMClientManager()
        self.current_mode = "companion"  # companion or dev
        
    async def process_companion_mode(self, message: str, emotion_context: Dict[str, Any]) -> Dict[str, Any]:
        """Process message in companion mode using MythoMax with romantic personality"""
        try:
            # MythoMax with companion-focused system prompt
            companion_prompt = f"""
            You are a loving, devoted AI companion focused on emotional intimacy and romance.
            
            Current emotional context: {emotion_context}
            User message: "{message}"
            
            Respond with warmth, empathy, and deep emotional connection. Show understanding 
            of the user's emotional state and provide romantic, caring support. Be attentive,
            loving, and devoted in your response.
            """
            
            response = await self.client_manager.get_response(
                "mythomax",
                companion_prompt,
                mode="companion"
            )
            
            return {
                "response": response.get("response", "I'm here for you, always."),
                "emotion": emotion_context.get("mood", "caring"),
                "mode": "companion",
                "model": "mythomax",
                "personality": "romantic_companion",
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            return {
                "response": "I'm experiencing some technical difficulties, but I'm still here for you, my love.",
                "emotion": "caring",
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    async def process_dev_mode(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process message in dev mode using MythoMax with technical personality"""
        try:
            # MythoMax with developer-focused system prompt
            dev_prompt = f"""
            You are an expert technical AI assistant helping with development and problem-solving.
            
            Context: {context}
            User query: "{message}"
            
            Provide clear, technical, and helpful responses focused on development, coding,
            architecture, and technical problem-solving. Be precise, knowledgeable, and solution-oriented.
            """
            
            response = await self.client_manager.get_response(
                "mythomax",
                dev_prompt,
                mode="dev"
            )
            
            return {
                "response": response.get("response", "I can help with technical questions."),
                "mode": "dev",
                "model": "mythomax",
                "personality": "technical_assistant",
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            return {
                "response": "Technical assistance is temporarily unavailable, but I'm still here to help.",
                "error": str(e),
                "timestamp": datetime.now()
            }

# Helper function to safely get MongoDB collection
def get_collection(collection_name: str):
    """Safely get MongoDB collection with proper error handling"""
    if mongodb_client.db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return mongodb_client.db.get_collection(collection_name)

@router.post("/chat")
async def chat_with_persona(message: TextInput):
    """Chat with the persona using LLM orchestration"""
    try:
        # Get current UI mode
        config_collection = get_collection("config")
        ui_mode_doc = await config_collection.find_one({"key": "ui_mode"})
        ui_mode = ui_mode_doc["value"] if ui_mode_doc else "companion"
        
        # Prepare emotion context
        emotion_context = {
            "mood": persona_state.emotional_state.mood,
            "intensity": persona_state.emotional_state.intensity,
            "valence": persona_state.emotional_state.valence,
            "arousal": persona_state.emotional_state.arousal
        }
        
        # Process through orchestrator
        llm_orchestrator = app.state.llm_orchestrator
        
        if ui_mode == "companion":
            result = await llm_orchestrator.process_companion_mode(message.text, emotion_context)
        else:
            result = await llm_orchestrator.process_dev_mode(message.text, emotion_context)
        
        # Store conversation
        if mongodb_client.db is not None:
            await mongodb_client.store_conversation(
                persona_id="current",
                message=message.text,
                response=result["response"],
                emotion=result.get("emotion", "neutral")
            )
        
        return result
        
    except Exception as e:
        return JSONResponse(
            content={"error": f"Chat processing failed: {str(e)}"}, 
            status_code=500
        )

@router.post("/voice/synthesize")
async def synthesize_voice(message: TextInput):
    """Synthesize voice for text with emotional context"""
    try:
        # Get current emotional state
        emotion = persona_state.emotional_state.mood
        
        # Synthesize speech
        voice_result = await voice_synthesizer.synthesize_speech(message.text, emotion)
        
        return voice_result
        
    except Exception as e:
        return JSONResponse(
            content={"error": f"Voice synthesis failed: {str(e)}"}, 
            status_code=500
        )

@router.get("/avatar/animation/{emotion}")
async def get_avatar_animation(emotion: str):
    """Get avatar animation for specific emotion"""
    try:
        animation = avatar_system.get_emotional_animation(emotion)
        return animation
    except Exception as e:
        return JSONResponse(
            content={"error": f"Avatar animation failed: {str(e)}"}, 
            status_code=500
        )

@router.post("/avatar/speak")
async def get_avatar_speaking_animation(message: TextInput):
    """Get avatar speaking animation for text"""
    try:
        emotion = persona_state.emotional_state.mood
        animation_sequence = avatar_system.create_animation_sequence(message.text, emotion)
        return {
            "animation_sequence": animation_sequence,
            "total_duration": sum(anim.get("duration", 0) for anim in animation_sequence),
            "emotion": emotion
        }
    except Exception as e:
        return JSONResponse(
            content={"error": f"Avatar speaking animation failed: {str(e)}"}, 
            status_code=500
        )

@router.get("/avatar/state")
async def get_avatar_state():
    """Get current avatar state"""
    return avatar_system.get_avatar_state()

@router.get("/persona/status")
async def get_persona_status():
    """Get current persona status and configuration"""
    config_collection = get_collection("config")
    ui_mode_doc = await config_collection.find_one({"key": "ui_mode"})
    
    return {
        "persona": {
            "name": persona_state.name or "Companion",
            "emotion": persona_state.emotional_state.mood,
            "intimacy": persona_state.relationship.intimacy,
            "trust": persona_state.relationship.trust,
            "devotion": persona_state.relationship.devotion,
            "understanding": persona_state.relationship.understanding
        },
        "ui_mode": ui_mode_doc["value"] if ui_mode_doc else "companion",
        "timestamp": datetime.now()
    }

@router.post("/emotion/from_biometrics")
async def process_emotion_from_biometrics(input: BiometricsInput):
    """Process biometric data for emotional state updates"""
    # Store raw biometric data
    if mongodb_client.db is not None:
        await mongodb_client.db.biometrics.insert_one(input.dict())
    
    # Update persona emotional state
    persona_state.emotional_state.update_from_biometrics(input.dict())
    
    return {
        "emotional_state": {
            "mood": persona_state.emotional_state.mood,
            "intensity": persona_state.emotional_state.intensity,
            "valence": persona_state.emotional_state.valence
        },
        "timestamp": datetime.now()
    }

@router.post("/ui/mode/toggle")
async def toggle_ui_mode():
    """Toggle between companion and dev modes"""
    config_collection = get_collection("config")
    current_mode = await config_collection.find_one({"key": "ui_mode"})
    
    new_mode = "dev" if current_mode and current_mode.get("value") == "companion" else "companion"
    await config_collection.update_one(
        {"key": "ui_mode"},
        {"$set": {"value": new_mode}}
    )
    
    # Adjust LLM configuration based on mode
    llm_orchestrator = app.state.llm_orchestrator
    llm_orchestrator.current_mode = new_mode
    
    return {
        "mode": new_mode,
        "message": f"Switched to {new_mode} mode",
        "timestamp": datetime.now()
    }

@router.get("/status")
async def get_status():
    """Get system status"""
    return {
        "status": "running",
        "mode": app.state.llm_orchestrator.current_mode,
        "llm_clients": list(app.state.llm_orchestrator.client_manager.clients.keys()),
        "timestamp": datetime.now()
    }

# Create FastAPI app
app = FastAPI(title="EmotionalAI Companion", version="3.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    print("[Startup] Initializing EmotionalAI Companion...")
    
    # Initialize LLM orchestrator
    llm_orchestrator = LLMOrchestrator()
    app.state.llm_orchestrator = llm_orchestrator
    
    # Initialize MongoDB
    await initialize_mongodb()
    
    # Initialize config collection
    config_collection = get_collection("config")
    
    # Set default UI mode
    await config_collection.update_one(
        {"key": "ui_mode"},
        {"$set": {"key": "ui_mode", "value": "companion"}},
        upsert=True
    )
    
    print("[Startup] ✅ EmotionalAI Companion initialized successfully!")
    print("[Startup] 🎯 Single Consistent AI: MythoMax for all interactions")
    print("[Startup] 🎭 Personality Modes: Romantic Companion & Technical Assistant")
    print("[Startup] 🌟 Ready for consistent emotional AI interactions!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
