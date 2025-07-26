"""
FastAPI Backend for Unified AI Companion
Integrates all enhancement functions and psychological modules
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import time
import logging

# Import our enhancement functions
from ..utils.message_timing import infer_conversation_tempo
from ..goodbye_manager import choose_goodbye_template
from ..memory.symbol_memory import symbol_decay_score
from ..ritual_hooks import trigger_ritual_if_ready
from ..utils.event_logger import log_emotional_event

# Import core modules
from ..core.unified_companion import UnifiedCompanion

app = FastAPI(
    title="Unified AI Companion API",
    description="Enhanced AI companion with emotional intelligence and personality evolution",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for requests
class ConversationRequest(BaseModel):
    message: str
    user_id: str = "default_user"
    mood: Optional[str] = "neutral"
    context: Optional[Dict[str, Any]] = {}

class ConversationAnalysisRequest(BaseModel):
    message: str
    mood: str = "neutral"
    silence_duration: float = 0.0
    message_complexity: int = 50

class GoodbyeRequest(BaseModel):
    mood: str = "neutral"
    bond_score: float = 0.5
    conversation_depth: float = 0.5

class SymbolDecayRequest(BaseModel):
    symbol: str
    last_used_timestamp: float
    usage_frequency: int

class RitualCheckRequest(BaseModel):
    depth_score: float
    last_ritual: float
    conversation_length: float = 300.0

class EventLogRequest(BaseModel):
    event_type: str
    intensity: float
    tag: str
    context: Optional[Dict[str, Any]] = {}
    source_module: str = "api"

# Initialize companion (we'll need memory and emotion components)
# For now, using mock objects
class MockMemory:
    async def get_companion_memory(self):
        return {}

class MockEmotionDetector:
    def detect_emotion(self, text):
        return {"emotion": "neutral", "intensity": 0.5}

class MockCreativeDiscovery:
    def discover_creative_potential(self, text):
        return {"creative_score": 0.5}

# Initialize companion
memory = MockMemory()
emotion_detector = MockEmotionDetector()
creative_discovery = MockCreativeDiscovery()

# Global companion instance
companion_instances: Dict[str, UnifiedCompanion] = {}

async def get_companion(user_id: str) -> UnifiedCompanion:
    """Get or create companion instance for user"""
    if user_id not in companion_instances:
        companion = UnifiedCompanion(memory, emotion_detector, creative_discovery)
        await companion.initialize(f"Companion-{user_id}", {"user_id": user_id})
        companion_instances[user_id] = companion
    return companion_instances[user_id]

# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Unified AI Companion API is running",
        "enhancement_functions": [
            "infer_conversation_tempo",
            "choose_goodbye_template", 
            "symbol_decay_score",
            "trigger_ritual_if_ready",
            "log_emotional_event"
        ]
    }

@app.post("/analyze/tempo")
async def analyze_conversation_tempo(request: ConversationAnalysisRequest):
    """Analyze conversation tempo based on mood and context"""
    try:
        tempo_multiplier = infer_conversation_tempo(
            mood=request.mood,
            recent_silence=request.silence_duration,
            message_complexity=request.message_complexity
        )
        
        log_emotional_event(
            event_type="tempo_analysis",
            intensity=0.3,
            tag=f"Tempo analysis for {request.mood} mood",
            context={"tempo_multiplier": tempo_multiplier},
            source_module="api"
        )
        
        return {
            "tempo_multiplier": tempo_multiplier,
            "mood": request.mood,
            "silence_duration": request.silence_duration,
            "interpretation": "faster" if tempo_multiplier < 1.0 else "slower" if tempo_multiplier > 1.0 else "normal"
        }
    except Exception as e:
        logger.error(f"Error analyzing tempo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/goodbye")
async def generate_goodbye(request: GoodbyeRequest):
    """Generate contextual goodbye message"""
    try:
        goodbye_message = choose_goodbye_template(
            mood=request.mood,
            bond_score=request.bond_score,
            conversation_depth=request.conversation_depth
        )
        
        log_emotional_event(
            event_type="goodbye_generated",
            intensity=request.bond_score,
            tag=f"Goodbye generated for {request.mood} mood",
            context={
                "bond_score": request.bond_score,
                "conversation_depth": request.conversation_depth
            },
            source_module="api"
        )
        
        return {
            "goodbye_message": goodbye_message,
            "mood": request.mood,
            "bond_score": request.bond_score,
            "conversation_depth": request.conversation_depth
        }
    except Exception as e:
        logger.error(f"Error generating goodbye: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/symbol_decay")
async def analyze_symbol_decay(request: SymbolDecayRequest):
    """Analyze symbol decay score"""
    try:
        decay_score = symbol_decay_score(
            symbol=request.symbol,
            last_used=request.last_used_timestamp,
            usage_frequency=request.usage_frequency
        )
        
        # Interpret decay score
        if decay_score < 0.3:
            status = "active"
        elif decay_score > 0.7:
            status = "dormant"
        else:
            status = "resurrection_ready"
        
        return {
            "symbol": request.symbol,
            "decay_score": decay_score,
            "status": status,
            "last_used": request.last_used_timestamp,
            "usage_frequency": request.usage_frequency
        }
    except Exception as e:
        logger.error(f"Error analyzing symbol decay: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check/ritual")
async def check_ritual_readiness(request: RitualCheckRequest):
    """Check if ritual conditions are met"""
    try:
        ritual_suggestion = trigger_ritual_if_ready(
            depth_score=request.depth_score,
            last_ritual=request.last_ritual,
            conversation_length=request.conversation_length
        )
        
        if ritual_suggestion:
            log_emotional_event(
                event_type="ritual_triggered",
                intensity=request.depth_score,
                tag="Ritual conditions met",
                context={"ritual_suggestion": ritual_suggestion},
                source_module="api"
            )
        
        return {
            "ritual_ready": ritual_suggestion is not None,
            "ritual_suggestion": ritual_suggestion,
            "depth_score": request.depth_score,
            "last_ritual": request.last_ritual
        }
    except Exception as e:
        logger.error(f"Error checking ritual readiness: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/log/event")
async def log_event(request: EventLogRequest):
    """Log an emotional event"""
    try:
        log_emotional_event(
            event_type=request.event_type,
            intensity=request.intensity,
            tag=request.tag,
            context=request.context,
            source_module=request.source_module
        )
        
        return {
            "status": "logged",
            "event_type": request.event_type,
            "intensity": request.intensity,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error logging event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/conversation")
async def handle_conversation(request: ConversationRequest):
    """Main conversation endpoint with integrated enhancement functions"""
    try:
        companion = await get_companion(request.user_id)
        
        # Analyze conversation tempo
        context = request.context or {}
        tempo = infer_conversation_tempo(
            mood=request.mood or "neutral",
            recent_silence=context.get("silence_duration", 0.0),
            message_complexity=len(request.message)
        )
        
        # Check for ritual readiness
        ritual = trigger_ritual_if_ready(
            depth_score=context.get("depth_score", 0.5),
            last_ritual=context.get("last_ritual", 0),
            conversation_length=context.get("conversation_length", 300)
        )
        
        # Log conversation event
        log_emotional_event(
            event_type="conversation_turn",
            intensity=context.get("emotional_intensity", 0.5),
            tag=f"Conversation with {request.user_id}",
            context={
                "tempo_multiplier": tempo,
                "ritual_suggested": ritual is not None,
                "message_length": len(request.message)
            },
            source_module="conversation_api"
        )
        
        # Generate response (simplified for now)
        response = {
            "companion_response": f"I understand you're feeling {request.mood}. Your message resonates with me.",
            "tempo_multiplier": tempo,
            "ritual_suggestion": ritual,
            "mood": request.mood,
            "user_id": request.user_id,
            "timestamp": time.time()
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error in conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/session/end")
async def end_session(user_id: str, mood: str = "neutral", context: Optional[Dict[str, Any]] = None):
    """End conversation session with contextual goodbye"""
    try:
        companion = await get_companion(user_id)
        
        # Generate contextual goodbye
        goodbye = await companion.end_session(user_id, context or {})
        
        return {
            "goodbye_message": goodbye,
            "user_id": user_id,
            "session_ended_at": time.time()
        }
        
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)