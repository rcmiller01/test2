from fastapi import APIRouter
from modules.emotion.emotion_dispatcher import dispatch_emotion_event

router = APIRouter()

@router.post("/dispatch")
def dispatch_event(event_type: str, value: str, source: str = "system"):
    dispatch_emotion_event(event_type, value, source)
    return {"status": "dispatched", "event": event_type, "value": value}
