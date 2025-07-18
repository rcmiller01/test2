from fastapi import APIRouter
from modules.visual.visual_state import get_visual_state

router = APIRouter()

@router.get("/api/visual-state")
async def visual_state():
    return get_visual_state()
