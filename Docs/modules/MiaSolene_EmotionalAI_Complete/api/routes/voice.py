from fastapi import APIRouter
from modules.voice.voice_output import speak

router = APIRouter()

@router.post("/speak")
def voice_speak(text: str):
    speak(text)
    return {"status": "speaking", "text": text}
