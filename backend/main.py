from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
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

# LLM Orchestration
class LLMOrchestrator:
    def __init__(self):
        self.primary_llm = "mythomax"  # Conductor
        self.support_llms = {
            "openchat": {"active": True, "weight": 0.3},
            "qwen2": {"active": True, "weight": 0.3},
            "kimik2": {"active": False, "weight": 0.8}  # Dev mode only
        }
        
    async def process_input(self, text: str, mode: str):
        if mode == "dev":
            return await self.process_dev_input(text)
            
        # Get context from support LLMs
        contexts = await self.gather_llm_contexts(text)
        
        # Let MythoMax orchestrate final response
        return await self.mythomax_process(text, contexts)
        
    async def gather_llm_contexts(self, text: str):
        contexts = {}
        for llm, config in self.support_llms.items():
            if config["active"]:
                context = await self.get_llm_context(llm, text)
                contexts[llm] = {
                    "insight": context,
                    "weight": config["weight"]
                }
        return contexts

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
    # Standard vitals
    heart_rate: Optional[int]
    heart_rate_variability: Optional[int]
    respiratory_rate: Optional[int]
    blood_pressure: Optional[Dict[str, float]]
    
    # Movement/Position data
    acceleration: Optional[Dict[str, float]]
    gyroscope: Optional[Dict[str, float]]
    
    # Environmental
    ambient_light: Optional[float]
    ambient_noise: Optional[float]
    
    # Device-specific
    device_type: str  # "smartwatch", "phone", "fitness_tracker"
    timestamp: datetime = datetime.now()

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
async def process_emotion_from_biometrics(input: BiometricsInput):
    # Store raw biometric data
    await mongodb_client.db.biometrics.insert_one(input.dict())
    
    # Process vitals for emotional state
    emotional_state = {"base_emotion": "neutral", "intensity": 0.5}
    
    if input.heart_rate:
        hr_intensity = min(1.0, max(0.0, input.heart_rate / 100))
        if input.heart_rate_variability:
            if input.heart_rate > 100:
                emotional_state["base_emotion"] = "excited" if input.heart_rate_variability > 50 else "anxious"
            elif input.heart_rate < 60:
                emotional_state["base_emotion"] = "calm" if input.heart_rate_variability > 50 else "tired"
            emotional_state["intensity"] = hr_intensity
    
    # Environmental factors
    if input.ambient_light is not None and input.ambient_noise is not None:
        if input.ambient_light < 10 and input.ambient_noise < 30:
            emotional_state["environment"] = "intimate"
        elif input.ambient_light > 1000 or input.ambient_noise > 70:
            emotional_state["environment"] = "stimulated"
    
    # Movement analysis
    if input.acceleration and input.gyroscope:
        movement = analyze_movement(input.acceleration, input.gyroscope)
        emotional_state["movement"] = movement
    
    # Update persona state
    persona_state.emotional_state.update_mood(
        emotional_state["base_emotion"],
        emotional_state["intensity"],
        f"biometrics_{input.device_type}"
    )
    
    return {
        "message": "Biometric data processed and stored.",
        "emotional_state": emotional_state,
        "timestamp": input.timestamp,
        "device_type": input.device_type,
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

    # Initialize config collection
    config_collection = mongodb_client.db.get_collection("config")
    
    # Set default UI mode
    await config_collection.update_one(
        {"key": "ui_mode"},
        {"$set": {"key": "ui_mode", "value": "companion"}},
        upsert=True
    )
    
    # Initialize LLM orchestrator
    llm_orchestrator = LLMOrchestrator()
    app.state.llm_orchestrator = llm_orchestrator

    # Persona creation logic
    personas_collection = mongodb_client.db[mongodb_client.collections['personas']]
    persona_count = await personas_collection.count_documents({})
    if persona_count == 0:
        # Create initial persona with empty name
        await mongodb_client.create_persona(
            name="",  # Empty name triggers name selection dialog
            traits={
                "devotion": 0.9,
                "openness": 0.8,
                "adaptability": 0.7
            }
        )
        # Store active persona in config collection
        await config_collection.update_one(
            {"key": "active_persona"},
            {"$set": {"key": "active_persona", "value": ""}},
            upsert=True
        )
        print("[Startup] Created initial persona with pending name selection")
    else:
        # Ensure active persona is set in config
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

# Mode toggle endpoint
@router.post("/ui/mode/toggle")
async def toggle_ui_mode():
    config_collection = mongodb_client.db.get_collection("config")
    current_mode = await config_collection.find_one({"key": "ui_mode"})
    
    new_mode = "dev" if current_mode["value"] == "companion" else "companion"
    await config_collection.update_one(
        {"key": "ui_mode"},
        {"$set": {"value": new_mode}}
    )
    
    # Adjust LLM configuration based on mode
    llm_orchestrator = app.state.llm_orchestrator
    if new_mode == "dev":
        llm_orchestrator.support_llms["kimik2"]["active"] = True
    else:
        llm_orchestrator.support_llms["kimik2"]["active"] = False
        
    return {
        "message": f"UI Mode switched to {new_mode}",
        "active_llms": [llm for llm, config in llm_orchestrator.support_llms.items() if config["active"]]
    }

# Health check endpoint for cluster monitoring
@app.get("/health")
async def health_check():
    """Health check endpoint for cluster monitoring"""
    return await server_health_check()
