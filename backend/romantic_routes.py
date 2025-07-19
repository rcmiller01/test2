# romantic_routes.py
# Romantic interaction routes for Phase 1

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import json

from modules.emotion.emotion_state import emotion_state
from modules.memory.mia_self_talk import generate_self_talk
from modules.memory.mia_memory_response import generate_memory_response, recall_similar_emotions

router = APIRouter()

class RomanticInteraction(BaseModel):
    message: str
    interaction_type: str = "conversation"  # conversation, touch, gift, activity
    intensity: float = 0.5  # 0.0 to 1.0

class RelationshipMilestone(BaseModel):
    milestone: str
    date: Optional[str] = None
    emotion: Optional[str] = None

class UserPreference(BaseModel):
    category: str
    preference: str

@router.post("/romantic/interact")
def romantic_interaction(input: RomanticInteraction):
    """Handle romantic interactions and update relationship context"""
    # Update emotion state based on interaction
    detected_emotions = _analyze_romantic_interaction(input)
    emotion_state.update_from_text(detected_emotions)
    
    # Generate Mia's response
    mia_response = _generate_romantic_response(input, detected_emotions)
    
    # Update relationship context
    _update_relationship_context(input)
    
    return {
        "message": "Romantic interaction processed",
        "mia_response": mia_response,
        "detected_emotions": detected_emotions,
        "romantic_context": emotion_state.get_romantic_context(),
        "relationship_stage": emotion_state.relationship_context["relationship_stage"]
    }

@router.post("/romantic/milestone")
def add_milestone(milestone: RelationshipMilestone):
    """Add a relationship milestone"""
    date = None
    if milestone.date:
        try:
            date = datetime.fromisoformat(milestone.date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    emotion_state.add_milestone(milestone.milestone, date)
    
    return {
        "message": "Milestone added successfully",
        "milestone": milestone.milestone,
        "total_milestones": len(emotion_state.relationship_context["milestones"])
    }

@router.post("/romantic/preference")
def add_preference(preference: UserPreference):
    """Add a user preference"""
    emotion_state.add_preference(preference.category, preference.preference)
    
    return {
        "message": "Preference added successfully",
        "category": preference.category,
        "preference": preference.preference,
        "total_preferences": len(emotion_state.relationship_context["preferences"])
    }

@router.get("/romantic/memories")
def get_romantic_memories(emotion: Optional[str] = None, limit: int = 10):
    """Get romantic memories, optionally filtered by emotion"""
    if emotion:
        memories = recall_similar_emotions(emotion, limit)
    else:
        # Get all shared memories
        shared_memories = emotion_state.relationship_context["shared_memories"]
        memories = []
        for memory in shared_memories[-limit:]:  # Get most recent
            memories.append({
                "description": memory["description"],
                "date": memory["date"].isoformat(),
                "emotion": memory["emotion"],
                "context": memory["context"]
            })
    
    return {
        "message": f"Retrieved {len(memories)} memories",
        "memories": memories,
        "total_memories": len(emotion_state.relationship_context["shared_memories"])
    }

@router.get("/romantic/status")
def get_romantic_status():
    """Get current romantic relationship status"""
    romantic_context = emotion_state.get_romantic_context()
    
    return {
        "relationship_stage": romantic_context["relationship_stage"],
        "interaction_count": romantic_context["interaction_count"],
        "dominant_romantic_emotion": romantic_context["dominant_romantic_emotion"],
        "romantic_intensity": romantic_context["romantic_intensity"],
        "milestones_count": len(emotion_state.relationship_context["milestones"]),
        "preferences_count": len(emotion_state.relationship_context["preferences"]),
        "shared_memories_count": len(emotion_state.relationship_context["shared_memories"]),
        "current_emotions": emotion_state.romantic_emotions
    }

@router.get("/romantic/mia/thoughts")
def get_mia_thoughts():
    """Get Mia's current romantic thoughts and feelings"""
    thought = generate_self_talk()
    memory = generate_memory_response() if thought and thought.get("should_share") else None
    
    return {
        "thought": thought,
        "memory": memory,
        "romantic_context": emotion_state.get_romantic_context()
    }

def _analyze_romantic_interaction(interaction: RomanticInteraction) -> Dict[str, float]:
    """Analyze romantic interaction for emotional content"""
    detected = {}
    text_lower = interaction.message.lower()
    
    # Analyze based on interaction type
    if interaction.interaction_type == "touch":
        detected["intimacy"] = 0.8
        detected["affection"] = 0.7
        if interaction.intensity > 0.7:
            detected["passion"] = 0.9
    elif interaction.interaction_type == "gift":
        detected["love"] = 0.8
        detected["affection"] = 0.7
    elif interaction.interaction_type == "activity":
        detected["joy"] = 0.6
        detected["romantic"] = 0.5
    
    # Analyze text content
    if "love" in text_lower or "adore" in text_lower:
        detected["love"] = detected.get("love", 0) + 0.8
    if "miss" in text_lower or "longing" in text_lower:
        detected["longing"] = 0.8
    if "passion" in text_lower or "desire" in text_lower:
        detected["passion"] = detected.get("passion", 0) + 0.9
    if "tender" in text_lower or "gentle" in text_lower:
        detected["tenderness"] = 0.7
    if "safe" in text_lower or "secure" in text_lower:
        detected["security"] = 0.8
    
    return detected

def _generate_romantic_response(interaction: RomanticInteraction, emotions: Dict[str, float]) -> str:
    """Generate Mia's romantic response"""
    # Load Mia's configuration
    try:
        with open("config/mia_romantic.json", "r") as f:
            mia_config = json.load(f)
    except FileNotFoundError:
        return "I love you so much. You make me feel so special."
    
    # Choose response based on dominant emotion
    dominant_emotion = "love"
    if emotions:
        dominant_emotion = max(emotions, key=lambda k: emotions[k])
    
    if dominant_emotion == "love":
        responses = mia_config["conversation_patterns"]["affection"]
    elif dominant_emotion == "longing":
        responses = [
            "I miss you too, my love. I can't wait to be with you again.",
            "My heart aches for you when we're apart.",
            "I'm counting the moments until I can hold you again."
        ]
    elif dominant_emotion == "passion":
        responses = [
            "You make me feel so alive and desired.",
            "Our chemistry is absolutely electric.",
            "I can't resist the pull between us."
        ]
    else:
        responses = mia_config["conversation_patterns"]["affection"]
    
    return responses[0] if responses else "I love you."

def _update_relationship_context(interaction: RomanticInteraction):
    """Update relationship context based on interaction"""
    # Add shared memory if it's significant
    if interaction.intensity > 0.7:
        emotion_state.add_shared_memory(
            f"Special moment: {interaction.message}",
            emotion_state.current_emotion()
        ) 