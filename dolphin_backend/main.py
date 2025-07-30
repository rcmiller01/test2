from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import os

from .routes import chat, memory, quantization, analytics, persona
from .orchestrator import orchestrator

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('dolphin_backend.log'),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

app = FastAPI(title="Dolphin AI Backend", version="2.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(chat.router)
app.include_router(memory.router)
app.include_router(quantization.router)
app.include_router(analytics.router)
app.include_router(persona.router)

@app.on_event("startup")
async def startup_event():
    await orchestrator.preference_vote_store.initialize()
    await orchestrator.initialize_advanced_features()

if __name__ == "__main__":
    port = int(os.getenv('DOLPHIN_PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
