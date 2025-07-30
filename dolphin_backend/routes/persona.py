
import re

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..orchestrator import orchestrator

router = APIRouter()

_VALID_ID = re.compile(r'^[\w-]{1,50}$')

@router.get("/api/personas")
async def get_personas():
    return {
        "current_persona": orchestrator.personality_system.current_persona,
        "personas": orchestrator.personality_system.get_personas()
    }

@router.post("/api/personas/create")
async def create_persona(persona_data: Dict[str, Any]):
    persona_id = persona_data.get("id")
    if not persona_id or not _VALID_ID.match(persona_id):
        raise HTTPException(status_code=400, detail="Persona ID required")
    success = orchestrator.personality_system.create_custom_persona(persona_id, persona_data)
    if success:
        return {"success": True, "persona_id": persona_id}
    else:
        raise HTTPException(status_code=400, detail="Failed to create persona")

@router.post("/api/personas/{persona_id}")
async def set_persona(persona_id: str):
    if not _VALID_ID.match(persona_id):
        raise HTTPException(status_code=400, detail="Invalid persona id")
    success = orchestrator.personality_system.set_persona(persona_id)
    if success:
        return {"success": True, "persona": persona_id}
    else:
        raise HTTPException(status_code=404, detail="Persona not found")
