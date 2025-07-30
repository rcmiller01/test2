from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from ..orchestrator import orchestrator

router = APIRouter()

@router.get("/api/memory/session/{session_id}")
async def get_session_memory(session_id: str):
    context = orchestrator.memory_system.get_session_context(session_id)
    return {"session_id": session_id, "context": context}

@router.get("/api/memory/longterm")
async def get_longterm_memory():
    return orchestrator.memory_system.long_term_memory

@router.post("/api/memory/longterm/goal")
async def add_goal(goal_data: Dict[str, Any]):
    goal_text = goal_data.get("text")
    priority = goal_data.get("priority", "medium")
    if not goal_text:
        raise HTTPException(status_code=400, detail="Goal text required")
    goal_id = orchestrator.memory_system.add_goal(goal_text, priority)
    return {"success": True, "goal_id": goal_id}

@router.post("/api/memory/flush")
async def flush_memory():
    success = orchestrator.memory_system.flush_short_term()
    return {"success": success}

@router.delete("/api/memory/session/{session_id}")
async def close_session(session_id: str):
    orchestrator.memory_system.close_session(session_id)
    return {"success": True, "session_id": session_id}
