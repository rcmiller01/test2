from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..orchestrator import orchestrator

router = APIRouter()

@router.get('/api/personas')
async def get_personas():
    return {
        'current_persona': orchestrator.personality_system.current_persona,
        'personas': orchestrator.personality_system.get_personas()
    }

@router.post('/api/personas/{persona_id}')
async def set_persona(persona_id: str):
    success = orchestrator.personality_system.set_persona(persona_id)
    if not success:
        raise HTTPException(status_code=404, detail='Persona not found')
    return {'success': True, 'persona': persona_id}

@router.post('/api/personas/create')
async def create_persona(persona_data: Dict[str, Any]):
    persona_id = persona_data.get('id')
    if not persona_id:
        raise HTTPException(status_code=400, detail='Persona ID required')
    success = orchestrator.personality_system.create_custom_persona(persona_id, persona_data)
    if not success:
        raise HTTPException(status_code=400, detail='Failed to create persona')
    return {'success': True, 'persona_id': persona_id}

@router.get('/api/personas/manifestos')
async def list_persona_manifestos():
    if not orchestrator.persona_instruction_manager:
        raise HTTPException(status_code=503, detail='Persona instruction manager not available')
    return orchestrator.persona_instruction_manager.list_manifestos()

@router.get('/api/personas/manifesto/{persona_id}')
async def get_persona_manifesto(persona_id: str):
    if not orchestrator.persona_instruction_manager:
        raise HTTPException(status_code=503, detail='Persona instruction manager not available')
    manifesto = orchestrator.persona_instruction_manager.get_manifesto(persona_id)
    if not manifesto:
        raise HTTPException(status_code=404, detail='Persona manifesto not found')
    return manifesto.to_dict()

@router.post('/api/personas/activate/{persona_id}')
async def activate_persona_manifesto(persona_id: str):
    if not orchestrator.persona_instruction_manager:
        raise HTTPException(status_code=503, detail='Persona instruction manager not available')
    success = orchestrator.persona_instruction_manager.activate_persona(persona_id)
    if not success:
        raise HTTPException(status_code=404, detail='Persona manifesto not found')
    return {'status': 'activated', 'persona_id': persona_id}
