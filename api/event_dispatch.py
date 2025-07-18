from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()

class DispatchRequest(BaseModel):
    event_type: str  # "text", "image", "video"
    value: str
    thread_id: str
    persona: str = None

@router.post("/api/event/dispatch")
async def event_dispatch(req: DispatchRequest):
    if req.event_type == "text":
        # TODO: Connect to symbolic + mood engine
        return {"value": f"[Mia/Solene would say something based on: '{req.value}']", "status": "ok"}
    elif req.event_type == "image":
        # TODO: Call image generation engine (ComfyUI/Invoke/etc.)
        return {"value": f"<image generated from prompt: '{req.value}'>", "status": "ok"}
    elif req.event_type == "video":
        # TODO: Call video generator (AnimateDiff/etc.)
        return {"value": f"<video generated from scene: '{req.value}'>", "status": "ok"}
    else:
        return {"value": "(Unknown event type)", "status": "error"}
