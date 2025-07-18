from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.routes import memory

app = FastAPI()

# Mount memory API
app.include_router(memory.router, prefix="/api")

# Serve the memory browser HTML
app.mount("/memory-browser", StaticFiles(directory="static", html=True), name="memory-browser")
