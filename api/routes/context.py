from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# In-memory thread context (replace with DB in prod)
thread_contexts = {}

class ContextRequest(BaseModel):
    thread_id: str
    mode: str  # "companion" or "dev"
    persona: str = None  # e.g. "mia", "solene", "doc"

@router.post("/api/context/set")
async def set_context(req: ContextRequest):
    thread_contexts[req.thread_id] = {
        "mode": req.mode,
        "persona": req.persona
    }
    return {"status": "ok", "context": thread_contexts[req.thread_id]}

@router.get("/api/context/{thread_id}")
async def get_context(thread_id: str):
    context = thread_contexts.get(thread_id, {"mode": "companion", "persona": None})
    return {"thread_id": thread_id, "context": context}
