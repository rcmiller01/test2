from fastapi import APIRouter, Request, HTTPException
from ..models import ChatRequest, ChatResponse
from ..orchestrator import orchestrator
import aiohttp
from datetime import datetime

router = APIRouter()

@router.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: Request, chat: ChatRequest):
    token = req.headers.get("persona-token")
    result = await orchestrator.process_chat_request(chat, persona_token=token)
    return result

@router.get("/api/status")
async def status_endpoint():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{orchestrator.ollama_url}/api/tags") as response:
                ollama_status = response.status == 200
    except Exception:
        ollama_status = False
    analytics = orchestrator.analytics_logger.get_real_time_stats()
    memory_summary = orchestrator.memory_system.get_memory_summary()
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "backend_status": {
            "services": {
                "ollama": ollama_status,
                "openrouter_configured": bool(orchestrator.openrouter_key),
                "n8n": False
            },
            "analytics": analytics,
            "memory": memory_summary,
            "personality": {
                "current_persona": orchestrator.personality_system.current_persona,
                "available_personas": list(orchestrator.personality_system.personas.keys())
            }
        }
    }

@router.get("/api/handlers")
async def handlers_endpoint():
    return {
        "handlers": [
            {
                "name": "DOLPHIN",
                "description": "Local conversation and general tasks",
                "icon": "🐬",
                "status": "available"
            },
            {
                "name": "OPENROUTER",
                "description": "Cloud AI for complex coding tasks",
                "icon": "☁️",
                "status": "available" if orchestrator.openrouter_key else "unavailable"
            },
            {
                "name": "N8N",
                "description": "Workflow automation and utilities",
                "icon": "🔧",
                "status": "development"
            },
            {
                "name": "KIMI_K2",
                "description": "Analytics and fallback processing",
                "icon": "📊",
                "status": "available"
            }
        ]
    }
