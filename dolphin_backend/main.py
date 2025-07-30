from fastapi import FastAPI
import os
from fastapi.middleware.cors import CORSMiddleware

from .orchestrator import orchestrator
from .routes import chat, memory, quantization, analytics, persona

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