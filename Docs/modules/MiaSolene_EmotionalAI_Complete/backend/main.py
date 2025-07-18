from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from emotion_state import emotion_state
from mia_self_talk import generate_self_talk
from mia_memory_response import generate_memory_response, recall_similar_emotions

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
    if "love" in input.text.lower():
        detected["romantic"] = 0.7
    elif "tired" in input.text.lower():
        detected["tired"] = 0.8
    elif "happy" in input.text.lower():
        detected["joy"] = 0.9
    elif "stressed" in input.text.lower():
        detected["stressed"] = 0.9
    elif "anxious" in input.text.lower():
        detected["anxious"] = 0.8
    emotion_state.update_from_text(detected)
    return {
        "message": "Emotion state updated.",
        "detected_emotions": detected,
        "current_emotion_state": emotion_state.to_dict(),
        "primary_mood": emotion_state.current_emotion()
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
        "primary_mood": emotion_state.current_emotion()
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