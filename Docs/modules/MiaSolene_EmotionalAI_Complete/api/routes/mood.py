from fastapi import APIRouter
from modules.emotion.mood_engine import update_mood

router = APIRouter()

@router.post("/update")
def mood_update(trigger: str, intensity: int = 1):
    update_mood(trigger, intensity)
    return {"status": "updated", "mood": trigger}
