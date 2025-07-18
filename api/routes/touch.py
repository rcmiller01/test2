from fastapi import APIRouter
from modules.touch.touch_context import resolve_touch

router = APIRouter()

@router.post("/context")
def touch_context(region: str, pressure: str = "medium"):
    result = resolve_touch(region, pressure)
    return {"touch_result": result}
