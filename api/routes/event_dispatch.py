from fastapi import APIRouter, Request
from pydantic import BaseModel
from api.routes.context import thread_contexts
from api.engines.doc_engine import generate_doc_response
from api.engines.symbol_engine import interpret_symbols
from api.engines.mood_engine import respond_with_emotion

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
            # Companion logic begins here
            symbol_hint = interpret_symbols(req.value, persona)
            emotional_response = respond_with_emotion(req.value, persona)
            reply = f"{emotional_response} {symbol_hint}".strip()
            return {"value": reply or "[No response generated]", "status": "ok"}

    elif req.event_type == "image":
        return {"value": f"<image from: '{req.value}'>", "status": "ok"}
    elif req.event_type == "video":
        return {"value": f"<video from: '{req.value}'>", "status": "ok"}
    else:
        return {"value": "(Unknown event type)", "status": "error"}
