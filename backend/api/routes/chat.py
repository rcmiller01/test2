from fastapi import APIRouter, Request
from pydantic import BaseModel
from backend.engine.unified_dispatch import unified_dispatch

router = APIRouter()

class ChatPayload(BaseModel):
    input: str
    emotion: str = "neutral"
    persona: str = "auto"
    override: bool = False

@router.post("/chat/dispatch")
async def chat_dispatch(payload: ChatPayload):
    result = unified_dispatch(payload.dict())
    return {"persona": result["persona"], "response": result["response"]}