from typing import Optional, Dict, Any
from pydantic import BaseModel, validator

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    persona: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    handler: str
    reasoning: str
    metadata: Dict[str, Any]
    timestamp: str
    session_id: str
    persona_used: str
    judgment: Optional[Dict[str, Any]] = None

class PreferenceVoteSchema(BaseModel):
    prompt: str
    response_a: str
    response_b: str
    winner: str

    @validator('winner')
    def validate_winner(cls, v):
        if v not in ('a', 'b'):
            raise ValueError("winner must be 'a' or 'b'")
        return v

class TaskRoute(BaseModel):
    task_type: str
    confidence: float
    reasoning: str
    handler: str

class PreferenceVoteRequest(BaseModel):
    prompt: str
    response_a: str
    response_b: str
    winner: str
