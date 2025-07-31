from fastapi import FastAPI
import os
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn

from .mcp_bridge import route_to_mcp

logger = logging.getLogger(__name__)

from .orchestrator import orchestrator, route_to_mcp
from .routes import chat, memory, quantization, analytics, persona

app = FastAPI(title="Dolphin AI Backend", version="2.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Internal MCP bridge route for testing
# ---------------------------------------------------------------------------

@app.post("/api/internal/test-mcp")
async def test_mcp_bridge():
    task = {
        "intent_type": "reminder",
        "payload": {
            "message": "Run reflection pass",
            "datetime": "2025-08-01T08:00:00Z",
        },
        "source": "dolphin",
        "request_id": "test_123",
    }
    return await route_to_mcp(task)

# Register routers

app.include_router(chat.router)
app.include_router(memory.router)
app.include_router(quantization.router)
app.include_router(analytics.router)
app.include_router(persona.router)


@app.post("/api/internal/test-mcp")
async def test_mcp_bridge():
    task = {
        "intent_type": "reminder",
        "payload": {
            "message": "Run reflection pass",
            "datetime": "2025-08-01T08:00:00Z"
        },
        "source": "dolphin",
        "request_id": "test_123"
    }
    response = await route_to_mcp(task)
    return response


@app.on_event("startup")
async def startup_event():
    await orchestrator.preference_vote_store.initialize()
    await orchestrator.initialize_advanced_features()

if __name__ == "__main__":
    port = int(os.getenv('DOLPHIN_PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
