from fastapi import FastAPI
from backend.api.routes import chat  # import the chat router
from fastapi.staticfiles import StaticFiles

# Import all route modules
from api.routes import (
    memory,
    context,
    mood,
    touch,
    visual,
    scene,
    voice,
    event_dispatch
)

app = FastAPI()

# Route includes
app.include_router(memory.router, prefix="/api")
app.include_router(context.router, prefix="/api")
app.include_router(mood.router, prefix="/api")
app.include_router(touch.router, prefix="/api")
app.include_router(visual.router, prefix="/api")
app.include_router(scene.router, prefix="/api")
app.include_router(voice.router, prefix="/api")
app.include_router(event_dispatch.router, prefix="/api")
app.include_router(chat.router, prefix="/api", tags=["chat"])


# Serve the memory browser HTML
app.mount("/memory-browser", StaticFiles(directory="static", html=True), name="memory-browser")
