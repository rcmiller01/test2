from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from api.persona_routes import router as persona_router
from models.persona_state import PersonaState
from core.self_talk import SelfTalkSystem
from modules.emotion.emotion_state import emotion_state
from modules.memory.mia_self_talk import generate_self_talk
from modules.memory.mia_memory_response import generate_memory_response, recall_similar_emotions
from romantic_routes import router as romantic_router
from phase2_routes import router as phase2_router
from routes.phase3 import router as phase3_router
from routes.advanced_features import router as advanced_features_router
from websocket_handlers import setup_phase3_websocket_handlers
from database.mongodb_client import initialize_mongodb, mongodb_client
from clustering.cluster_manager import initialize_cluster, server_health_check

app = FastAPI()
router = APIRouter()

# Initialize core systems
persona_state = PersonaState()
self_talk_system = SelfTalkSystem(persona_state)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include persona routes
app.include_router(persona_router, prefix="/api")

class TextInput(BaseModel):
    text: str

class BiometricsInput(BaseModel):
    bpm: int
    hrv: int
    context: str = "general"

@router.post("/emotion/from_text")
def process_emotion_from_text(input: TextInput):
    detected = {"calm": 0.3}
    
    # Core emotion detection
    text_lower = input.text.lower()
    
    if "love" in text_lower or "adore" in text_lower or "cherish" in text_lower:
        detected["love"] = 0.8
        detected["romantic"] = 0.7
    elif "miss" in text_lower or "longing" in text_lower or "yearn" in text_lower:
        detected["longing"] = 0.8
    elif "passion" in text_lower or "desire" in text_lower or "crave" in text_lower:
        detected["passion"] = 0.9
        detected["desire"] = 0.8
    elif "tender" in text_lower or "gentle" in text_lower or "care" in text_lower:
        detected["tenderness"] = 0.7
        detected["affection"] = 0.6
    elif "safe" in text_lower or "secure" in text_lower or "trust" in text_lower:
        detected["security"] = 0.8
    elif "affection" in text_lower or "sweet" in text_lower or "precious" in text_lower:
        detected["affection"] = 0.7
    elif "jealous" in text_lower or "envy" in text_lower:
        detected["jealousy"] = 0.8
    elif "intimate" in text_lower or "close" in text_lower:
        detected["intimacy"] = 0.7
    elif "tired" in text_lower:
        detected["tired"] = 0.8
    elif "happy" in text_lower or "joy" in text_lower:
        detected["joy"] = 0.9
    elif "stressed" in text_lower:
        detected["stressed"] = 0.9
    elif "anxious" in text_lower:
        detected["anxious"] = 0.8
    
    # Get primary emotion
    primary_emotion = max(detected.items(), key=lambda x: x[1])[0]
    intensity = max(detected.values())
    
    # Update persona emotional state
    persona_state.emotional_state.update_mood(primary_emotion, intensity, "text_input")
    
    return {
        "message": "Emotion state updated.",
        "detected_emotions": detected,
        "primary_emotion": primary_emotion,
        "intensity": intensity,
        "current_mood": persona_state.emotional_state.current_mood,
        "relationship_impact": {
            "emotional_sync": persona_state.relationship.emotional_synchronization,
            "understanding": persona_state.relationship.understanding
        }
    }

@router.post("/emotion/from_biometrics")
def process_emotion_from_biometrics(input: BiometricsInput):
    # Map biometrics to emotional state
    intensity = min(1.0, max(0.0, input.bpm / 100))  # Normalize BPM
    
    if input.bpm > 100:
        emotion = "excited" if input.hrv > 50 else "anxious"
    elif input.bpm < 60:
        emotion = "calm" if input.hrv > 50 else "tired"
    else:
        emotion = "neutral"
        
    # Update persona emotional state
    persona_state.emotional_state.update_mood(emotion, intensity, f"biometrics_{input.context}")
    
    return {
        "message": "Emotion state updated from biometrics.",
        "detected_emotion": emotion,
        "intensity": intensity,
        "context": input.context,
        "current_mood": persona_state.emotional_state.current_mood
    }

@router.get("/persona/self_talk")
def persona_self_talk():
    thought = self_talk_system.generate_thought()
    if not thought:
        return {"message": "The persona is quiet right now."}
        
    if thought["should_share"]:
        return JSONResponse(content={
            "message": "The persona shares something meaningful.",
            "thought": thought["thought"],
            "emotion": thought["emotion"],
            "timestamp": thought["timestamp"],
            "delivery_mode": thought["delivery_mode"],
            "personality_influence": persona_state.personality.dict()
        })
    return JSONResponse(content={
        "message": "The persona is reflecting privately.",
        "emotion": thought["emotion"],
        "timestamp": thought["timestamp"],
        "delivery_mode": thought["delivery_mode"],
        "personality_influence": persona_state.personality.dict()
    })

@router.get("/persona/self_talk/recall")
def recall_emotional_memory(emotion: Optional[str] = None, limit: int = 5):
    if not emotion:
        emotion = persona_state.emotional_state.current_mood
    
    memories = self_talk_system.recall_memory(emotion, limit)
    return {
        "message": f"The persona recalls thoughts related to '{emotion}'.",
        "emotion": emotion,
        "memories": memories,
        "personality_context": {
            "openness": persona_state.personality.openness,
            "emotional_depth": persona_state.relationship.emotional_synchronization
        }
    }

app.include_router(router)
app.include_router(persona_router, prefix="/api")
app.include_router(romantic_router, prefix="/api")
app.include_router(phase2_router, prefix="/api/phase2")
app.include_router(phase3_router, prefix="/api")
app.include_router(advanced_features_router, prefix="/api")

# Setup Phase 3 WebSocket handlers
@app.on_event("startup")
async def startup_event():
    # Initialize MongoDB
    await initialize_mongodb()

    # Persona creation logic
    personas_collection = mongodb_client.db[mongodb_client.collections['personas']]
    persona_count = await personas_collection.count_documents({})
    if persona_count == 0:
        # In a real system, prompt the user or orchestrator for a name. For now, use 'Beloved' as default.
        default_name = "Beloved"
        await mongodb_client.create_persona(name=default_name, traits={"devotion": 1.0})
        # Store active persona in config collection
        config_collection = mongodb_client.db.get_collection("config")
        await config_collection.update_one(
            {"key": "active_persona"},
            {"$set": {"key": "active_persona", "value": default_name}},
            upsert=True
        )
        print(f"[Startup] Created and set active persona: {default_name}")
    else:
        # Ensure active persona is set in config
        config_collection = mongodb_client.db.get_collection("config")
        active = await config_collection.find_one({"key": "active_persona"})
        if not active:
            first_persona = await personas_collection.find_one({})
            await config_collection.update_one(
                {"key": "active_persona"},
                {"$set": {"key": "active_persona", "value": first_persona['name']}},
                upsert=True
            )
            print(f"[Startup] Set active persona: {first_persona['name']}")

    # Initialize cluster
    await initialize_cluster()
    # Setup WebSocket handlers
    await setup_phase3_websocket_handlers()

# Health check endpoint for cluster monitoring
@app.get("/health")
async def health_check():
    """Health check endpoint for cluster monitoring"""
    return await server_health_check()
