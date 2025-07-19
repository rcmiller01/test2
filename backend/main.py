from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from modules.emotion.emotion_state import emotion_state
from modules.memory.mia_self_talk import generate_self_talk
from modules.memory.mia_memory_response import generate_memory_response, recall_similar_emotions
from romantic_routes import router as romantic_router
from phase2_routes import router as phase2_router
from routes.phase3 import router as phase3_router
from routes.advanced_features import router as advanced_features_router
from websocket_handlers import setup_phase3_websocket_handlers
from database.mongodb_client import initialize_mongodb
from clustering.cluster_manager import initialize_cluster, server_health_check

app = FastAPI()
router = APIRouter()

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
    
    emotion_state.update_from_text(detected)
    return {
        "message": "Emotion state updated.",
        "detected_emotions": detected,
        "current_emotion_state": emotion_state.to_dict(),
        "primary_mood": emotion_state.current_emotion(),
        "romantic_context": emotion_state.get_romantic_context()
    }

@router.post("/emotion/from_biometrics")
def process_emotion_from_biometrics(input: BiometricsInput):
    emotion_state.update_from_biometrics(
        bpm=input.bpm,
        hrv=input.hrv,
        context=input.context
    )
    return {
        "message": "Emotion state updated from biometrics.",
        "current_emotion_state": emotion_state.to_dict(),
        "primary_mood": emotion_state.current_emotion(),
        "romantic_context": emotion_state.get_romantic_context()
    }

@router.get("/mia/self_talk")
def mia_self_talk():
    thought = generate_self_talk()
    if not thought:
        return {"message": "Mia is quiet right now."}
    memory_line = generate_memory_response() if thought["should_share"] else None
    if thought["should_share"]:
        return JSONResponse(content={
            "message": "Mia shares something meaningful.",
            "thought": thought["thought"],
            "emotion": thought["emotion"],
            "timestamp": thought["timestamp"],
            "delivery_mode": thought["delivery_mode"],
            "memory": memory_line
        })
    return JSONResponse(content={
        "message": "Mia is reflecting privately.",
        "emotion": thought["emotion"],
        "timestamp": thought["timestamp"],
        "delivery_mode": thought["delivery_mode"]
    })

@router.get("/mia/self_talk/recall")
def recall_emotional_memory(emotion: str = None, limit: int = 5):
    if not emotion:
        emotion = emotion_state.current_emotion()
    history = recall_similar_emotions(emotion, limit=limit)
    return {
        "message": f"Mia recalls past thoughts related to '{emotion}'.",
        "emotion": emotion,
        "memories": history
    }

app.include_router(router)
app.include_router(romantic_router, prefix="/api")
app.include_router(phase2_router, prefix="/api/phase2")
app.include_router(phase3_router, prefix="/api")
app.include_router(advanced_features_router, prefix="/api")

# Setup Phase 3 WebSocket handlers
@app.on_event("startup")
async def startup_event():
    # Initialize MongoDB
    await initialize_mongodb()
    
    # Initialize cluster
    await initialize_cluster()
    
    # Setup WebSocket handlers
    await setup_phase3_websocket_handlers()

# Health check endpoint for cluster monitoring
@app.get("/health")
async def health_check():
    """Health check endpoint for cluster monitoring"""
    return await server_health_check()