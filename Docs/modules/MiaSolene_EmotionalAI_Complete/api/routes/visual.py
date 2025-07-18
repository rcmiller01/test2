from fastapi import APIRouter
from modules.visual.visual_sync import get_visual_state

router = APIRouter()

@router.get("/state")
def visual_state():
    state = get_visual_state()
    return {"visual_state": state}
