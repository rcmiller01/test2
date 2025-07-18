from fastapi import APIRouter
from modules.memory.scene_memory import recall_scene

router = APIRouter()

@router.post("/replay")
def replay_scene(symbol: str = None, mood: str = None, persona: str = None):
    scene = recall_scene(symbol=symbol, mood=mood, persona=persona)
    return scene or {"status": "no scene found"}
