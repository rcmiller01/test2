from fastapi import APIRouter, Query
from tts_service import speak

router = APIRouter()

@router.get("/mia/speak")
def mia_speak(text: str = Query(...), emotion: str = Query("default")):
    try:
        speak(text, emotion)
        return {"message": "Mia has spoken.", "text": text, "emotion": emotion}
    except Exception as e:
        return {"error": str(e)}