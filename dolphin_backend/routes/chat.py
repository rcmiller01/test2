from fastapi import APIRouter, Request, HTTPException
from datetime import datetime
import aiohttp
from ..orchestrator import orchestrator, ChatRequest, ChatResponse
from handler_registry import handler_registry, HandlerState

router = APIRouter()

@router.post('/api/chat', response_model=ChatResponse)
async def chat_endpoint(req: Request, chat: ChatRequest):
    token = req.headers.get('persona-token')
    return await orchestrator.process_chat_request(chat, persona_token=token)

@router.get('/api/status')
async def status_endpoint():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{orchestrator.ollama_url}/api/tags") as resp:
                ollama_status = resp.status == 200
    except Exception:
        ollama_status = False
    analytics = orchestrator.analytics_logger.get_real_time_stats()
    memory_summary = orchestrator.memory_system.get_memory_summary()
    return {
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'backend_status': {
            'services': {
                'ollama': ollama_status,
                'openrouter_configured': bool(orchestrator.openrouter_key)
            },
            'memory': memory_summary,
            'analytics': analytics
        }
    }

@router.get('/api/handlers')
async def handlers_endpoint():
    return {
        'handlers': [
            {
                'name': 'DOLPHIN',
                'description': 'Local conversation and general tasks',
                'icon': '🐬',
                'status': 'available'
            },
            {
                'name': 'OPENROUTER',
                'description': 'Cloud AI for complex coding tasks',
                'icon': '☁️',
                'status': 'available' if orchestrator.openrouter_key else 'unavailable'
            },
            {
                'name': 'N8N',
                'description': 'Workflow automation and utilities',
                'icon': '🔧',
                'status': 'development'
            },
            {
                'name': 'KIMI_K2',
                'description': 'Analytics and fallback processing',
                'icon': '📊',
                'status': 'available'
            }
        ]
    }

@router.post('/api/update-handler-status')
async def update_handler_status(handler: str, status: str):
    try:
        handler_registry.update(handler, HandlerState(status))
        return {'handler': handler, 'status': status}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/api/fallback-alert')
async def fallback_alert():
    return {'status': 'alerted'}
