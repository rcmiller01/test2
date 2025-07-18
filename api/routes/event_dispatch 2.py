from fastapi import APIRouter, Request
from pydantic import BaseModel
from api.routes.context import thread_contexts
from api.engines.doc_engine import generate_doc_response

router = APIRouter()

class DispatchRequest(BaseModel):
    event_type: str  # "text", "image", "video"
    value: str
    thread_id: str
    persona: str = None

@router.post("/api/event/dispatch")
async def event_dispatch(req: DispatchRequest):
    context = thread_contexts.get(req.thread_id, {"mode": "companion", "persona": None})
    mode = context.get("mode")
    persona = context.get("persona")

    if req.event_type == "text":
        if mode == "dev":
            reply = generate_doc_response(req.value)
            return {"value": reply, "status": "ok"}
        else:
            # Placeholder: Companion engine logic would go here
            return {"value": f"[{persona or 'Mia+Solene+Lyra'} would respond to: '{req.value}']", "status": "ok"}

    elif req.event_type == "image":
        return {"value": f"<image from: '{req.value}'>", "status": "ok"}
    elif req.event_type == "video":
        return {"value": f"<video from: '{req.value}'>", "status": "ok"}
    else:
        return {"value": "(Unknown event type)", "status": "error"}
