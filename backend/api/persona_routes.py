"""
Persona API routes for the EmotionalAI system.
Handles persona customization, chat, emotional analysis, and relationship progression.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from models.llm_processor import LLMProcessor
from models.persona_state import PersonaState
import json
import os

router = APIRouter()
llm_processor = LLMProcessor()
persona_state = PersonaState()

# Models
class PersonaCustomization(BaseModel):
    name: str
    hair_color: str
    eye_color: str
    voice_type: str

class ChatMessage(BaseModel):
    message: str
    mood: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    mood: str
    llm_model: str

class RelationshipStatus(BaseModel):
    devotion: float
    trust: float
    intimacy: float
    understanding: float
    emotional_sync: float
    milestones: Dict

# Load config
CONFIG_PATH = "config/persona_config.json"
PERSONA_CONFIG = {}

def load_config():
    """Load persona configuration from JSON file."""
    global PERSONA_CONFIG
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            PERSONA_CONFIG = json.load(f)
    else:
        PERSONA_CONFIG = {
            "name": "",
            "devotion_level": 0.9,
            "characteristics": {
                "personality": "warm_affectionate",
                "style": "romantic_casual",
                "hair_color": "",
                "eye_color": ""
            }
        }

def save_config():
    """Save current persona configuration to JSON file."""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(PERSONA_CONFIG, f, indent=2)

# Load initial config
load_config()

@router.post("/persona/customize")
async def customize_persona(customization: PersonaCustomization):
    """Update persona customization settings."""
    PERSONA_CONFIG["name"] = customization.name
    PERSONA_CONFIG["characteristics"]["hair_color"] = customization.hair_color
    PERSONA_CONFIG["characteristics"]["eye_color"] = customization.eye_color
    PERSONA_CONFIG["voice_type"] = customization.voice_type
    
    save_config()
    return {"status": "success", "config": PERSONA_CONFIG}

@router.post("/chat")
async def chat(message: ChatMessage):
    """Process chat message and return persona response."""
    try:
        # Analyze incoming message emotion if not provided
        if not message.mood:
            emotion_analysis = await llm_processor.analyze_emotion(message.message)
            message.mood = emotion_analysis["mood"]

        # Generate response
        response = await llm_processor.generate_response(message.message, {
            "mood": message.mood,
            "intensity": 0.8  # Default intensity if not available
        })

        return ChatResponse(
            response=response["response"],
            mood=response["mood"],
            llm_model=response["llm_model"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analyze/mood")
async def analyze_mood(text: str):
    """Analyze the emotional content of text."""
    try:
        # TODO: Implement actual mood analysis
        is_positive = any(word in text.lower() for word in ["love", "happy", "good", "wonderful"])
        is_negative = any(word in text.lower() for word in ["sad", "angry", "upset", "bad"])
        
        mood = "positive" if is_positive else "negative" if is_negative else "neutral"
        confidence = 0.8
        
        return {"mood": mood, "confidence": confidence}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/gesture/{mood}")
async def get_gesture(mood: str):
    """Get appropriate gesture/expression for given mood."""
    try:
        # TODO: Implement actual gesture mapping
        gestures = {
            "positive": {"gesture": "smile", "intensity": 0.8},
            "negative": {"gesture": "concerned", "intensity": 0.6},
            "neutral": {"gesture": "attentive", "intensity": 0.5}
        }
        return gestures.get(mood, {"gesture": "neutral", "intensity": 0.5})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/relationship/status", response_model=RelationshipStatus)
async def get_relationship_status():
    """Get the current relationship status and metrics"""
    try:
        return RelationshipStatus(
            devotion=persona_state.relationship.devotion,
            trust=persona_state.relationship.trust,
            intimacy=persona_state.relationship.intimacy,
            understanding=persona_state.relationship.understanding,
            emotional_sync=persona_state.relationship.emotional_synchronization,
            milestones={
                "conversations": persona_state.milestones.deep_conversation_count,
                "trust_events": len(persona_state.milestones.trust_building_events),
                "emotional_breakthroughs": len(persona_state.milestones.emotional_breakthroughs)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
