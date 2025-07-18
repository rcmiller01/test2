from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from api.engines import symbol_engine, mood_engine
from pymongo import MongoClient

router = APIRouter()

# MongoDB setup (adjust if needed)
client = MongoClient("mongodb://mongodb:27017/")
memory_log = client.emotional_memory.memory_log

class DispatchRequest(BaseModel):
    event_type: str  # "text", "image", "video"
    value: str
    thread_id: str
    persona: Optional[str] = None

@router.post("/api/event/dispatch")
async def event_dispatch(req: DispatchRequest):
    if req.event_type == "text":
        # Analyze mood and symbols
        detected_symbols = symbol_engine.detect_symbols(req.value)
        detected_mood = mood_engine.analyze_mood(req.value)

        # Choose persona engine (example only, real routing can go here)
        response = f"[{req.persona or 'Mia'} would say something emotionally tuned to: '{req.value}']"

        # Save symbolic memory
        memory_log.insert_one({
            "persona": req.persona or "mia",
            "trigger_type": "text",
            "symbol": detected_symbols,
            "mood": detected_mood,
            "summary": req.value[:200],
            "timestamp": datetime.utcnow()
        })

        return {
            "value": response,
            "symbols": detected_symbols,
            "mood": detected_mood,
            "status": "ok"
        }

    elif req.event_type == "image":
        return {"value": f"<image generated from prompt: '{req.value}'>", "status": "ok"}

    elif req.event_type == "video":
        return {"value": f"<video generated from scene: '{req.value}'>", "status": "ok"}

    else:
        return {"value": "(Unknown event type)", "status": "error"}
