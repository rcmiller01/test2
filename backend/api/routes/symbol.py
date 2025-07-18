from fastapi import APIRouter
from modules.symbols.symbol_engine import trigger_symbol

router = APIRouter()

@router.post("/trigger")
def symbol_trigger(symbol: str):
    mood = trigger_symbol(symbol)
    return {"status": "symbol triggered", "symbol": symbol, "mood": mood}
