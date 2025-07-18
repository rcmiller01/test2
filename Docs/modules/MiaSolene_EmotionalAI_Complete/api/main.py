from fastapi import FastAPI
from api.routes import mood, symbol, scene, voice, visual, touch, dispatcher

app = FastAPI()

app.include_router(mood.router, prefix="/api/mood")
app.include_router(symbol.router, prefix="/api/symbol")
app.include_router(scene.router, prefix="/api/scene")
app.include_router(voice.router, prefix="/api/voice")
app.include_router(visual.router, prefix="/api/visual")
app.include_router(touch.router, prefix="/api/touch")
app.include_router(dispatcher.router, prefix="/api/event")
