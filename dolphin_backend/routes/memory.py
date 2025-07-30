from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional, List
from ..orchestrator import orchestrator

router = APIRouter()

@router.get('/api/memory/session/{session_id}')
async def get_session_memory(session_id: str):
    context = orchestrator.memory_system.get_session_context(session_id)
    return {'session_id': session_id, 'context': context}

@router.get('/api/memory/longterm')
async def get_longterm_memory():
    return orchestrator.memory_system.long_term_memory

@router.post('/api/memory/longterm/goal')
async def add_goal(goal_data: Dict[str, Any]):
    goal_text = goal_data.get('text')
    priority = goal_data.get('priority', 'medium')
    if not goal_text:
        raise HTTPException(status_code=400, detail='Goal text required')
    goal_id = orchestrator.memory_system.add_goal(goal_text, priority)
    return {'success': True, 'goal_id': goal_id}

@router.post('/api/memory/flush')
async def flush_memory():
    success = orchestrator.memory_system.flush_short_term()
    return {'success': success}

@router.delete('/api/memory/session/{session_id}')
async def close_session(session_id: str):
    orchestrator.memory_system.close_session(session_id)
    return {'success': True, 'session_id': session_id}

# Private memory
@router.post('/api/private-memory/unlock')
async def unlock_private_memory(password: str = 'default_dev_password'):
    if not orchestrator.private_memory_manager:
        raise HTTPException(status_code=503, detail='Private memory manager not available')
    success = orchestrator.private_memory_manager.unlock_private_memories(password)
    if success:
        return {'status': 'unlocked', 'message': 'Private memories are now accessible'}
    raise HTTPException(status_code=401, detail='Invalid password')

@router.post('/api/private-memory/lock')
async def lock_private_memory():
    if not orchestrator.private_memory_manager:
        raise HTTPException(status_code=503, detail='Private memory manager not available')
    orchestrator.private_memory_manager.lock_private_memories()
    return {'status': 'locked', 'message': 'Private memories are now locked'}

@router.get('/api/private-memory/status')
async def get_private_memory_status():
    if not orchestrator.private_memory_manager:
        raise HTTPException(status_code=503, detail='Private memory manager not available')
    return orchestrator.private_memory_manager.get_status()

@router.get('/api/private-memory/preview')
async def get_private_memory_preview():
    if not orchestrator.private_memory_manager:
        raise HTTPException(status_code=503, detail='Private memory manager not available')
    return orchestrator.private_memory_manager.get_private_memory_preview()

@router.post('/api/private-memory/add')
async def add_private_memory(request: Dict[str, Any]):
    if not orchestrator.private_memory_manager:
        raise HTTPException(status_code=503, detail='Private memory manager not available')
    if not orchestrator.private_memory_manager.is_unlocked:
        raise HTTPException(status_code=403, detail='Private memories are locked')
    entry_id = orchestrator.private_memory_manager.add_private_memory(
        content=request.get('content', ''),
        tags=request.get('tags', []),
        category=request.get('category', 'private'),
        session_id=request.get('session_id', 'default'),
        access_level=request.get('access_level', 'private'),
        metadata=request.get('metadata', {})
    )
    return {'entry_id': entry_id, 'status': 'added'}

@router.get('/api/private-memory/{entry_id}')
async def get_private_memory(entry_id: str):
    if not orchestrator.private_memory_manager:
        raise HTTPException(status_code=503, detail='Private memory manager not available')
    if not orchestrator.private_memory_manager.is_unlocked:
        raise HTTPException(status_code=403, detail='Private memories are locked')
    memory = orchestrator.private_memory_manager.get_private_memory(entry_id)
    if not memory:
        raise HTTPException(status_code=404, detail='Private memory not found')
    return memory

@router.get('/api/private-memory/search')
async def search_private_memories(query: Optional[str] = None, category: Optional[str] = None, limit: int = 10):
    if not orchestrator.private_memory_manager:
        raise HTTPException(status_code=503, detail='Private memory manager not available')
    if not orchestrator.private_memory_manager.is_unlocked:
        raise HTTPException(status_code=403, detail='Private memories are locked')
    results = orchestrator.private_memory_manager.search_private_memories(query=query, category=category, limit=limit)
    return {'results': results, 'count': len(results)}
