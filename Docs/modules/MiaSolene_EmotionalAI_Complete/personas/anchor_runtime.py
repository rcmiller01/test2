
import json
from fastapi import APIRouter, HTTPException

router = APIRouter()

def load_anchor_data(persona: str):
    try:
        with open(f"{persona}_emotional_anchors.json", "r") as f:
            anchors = json.load(f)
        with open(f"{persona}_anchor_responses.json", "r") as f:
            responses = json.load(f)
        return anchors, responses
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Anchor files not found.")

@router.get("/anchors/{persona}")
def get_anchor_info(persona: str):
    anchors, responses = load_anchor_data(persona)
    return {
        "anchors": anchors,
        "responses": responses
    }

@router.post("/anchors/{persona}/trigger")
def trigger_anchor(persona: str, symbol: str):
    _, responses = load_anchor_data(persona)
    if symbol in responses:
        return {"response": responses[symbol]}
    else:
        raise HTTPException(status_code=404, detail="Anchor symbol not recognized.")
