# emotion_state.py
# Enhanced emotion state management for romantic companionship

import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class EmotionState:
    def __init__(self):
        # Core emotions
        self.emotions = {
            "joy": 0.0,
            "sadness": 0.0,
            "anger": 0.0,
            "fear": 0.0,
            "surprise": 0.0,
            "disgust": 0.0,
            "calm": 0.5,  # Default neutral state
            "tired": 0.0,
            "stressed": 0.0,
            "anxious": 0.0
        }
        
        # Romantic emotions for Phase 1
        self.romantic_emotions = {
            "love": 0.0,
            "longing": 0.0,
            "passion": 0.0,
            "tenderness": 0.0,
            "jealousy": 0.0,
            "security": 0.0,
            "romantic": 0.0,
            "affection": 0.0,
            "desire": 0.0,
            "intimacy": 0.0
        }
        
        # Relationship context
        self.relationship_context = {
            "relationship_stage": "new",  # new, developing, established, long_term
            "relationship_duration_days": 0,
            "last_interaction": datetime.now(),
            "interaction_count": 0,
            "milestones": [],
            "preferences": {},
            "inside_jokes": [],
            "shared_memories": []
        }
        
        # Emotion decay settings
        self.decay_rate = 0.1  # Emotions decay by 10% per minute
        self.last_update = datetime.now()
        
    def update_from_text(self, detected_emotions: Dict[str, float]):
        """Update emotions based on text analysis"""
        current_time = datetime.now()
        self._apply_decay(current_time)
        
        # Update core emotions
        for emotion, intensity in detected_emotions.items():
            if emotion in self.emotions:
                self.emotions[emotion] = min(1.0, self.emotions[emotion] + intensity)
            elif emotion in self.romantic_emotions:
                self.romantic_emotions[emotion] = min(1.0, self.romantic_emotions[emotion] + intensity)
        
        self.last_update = current_time
        self._update_relationship_context()
        
    def update_from_biometrics(self, bpm: int, hrv: int, context: str = "general"):
        """Update emotions based on biometric data"""
        current_time = datetime.now()
        self._apply_decay(current_time)
        
        # Heart rate analysis
        if bpm > 100:
            if context == "romantic":
                self.romantic_emotions["passion"] = min(1.0, self.romantic_emotions["passion"] + 0.3)
                self.romantic_emotions["desire"] = min(1.0, self.romantic_emotions["desire"] + 0.2)
            else:
                self.emotions["stressed"] = min(1.0, self.emotions["stressed"] + 0.3)
        elif bpm < 60:
            self.emotions["calm"] = min(1.0, self.emotions["calm"] + 0.2)
            self.romantic_emotions["security"] = min(1.0, self.romantic_emotions["security"] + 0.1)
        
        # Heart rate variability analysis
        if hrv > 50:  # High HRV indicates relaxation
            self.emotions["calm"] = min(1.0, self.emotions["calm"] + 0.2)
            self.romantic_emotions["security"] = min(1.0, self.romantic_emotions["security"] + 0.1)
        elif hrv < 20:  # Low HRV indicates stress
            self.emotions["stressed"] = min(1.0, self.emotions["stressed"] + 0.3)
            self.emotions["anxious"] = min(1.0, self.emotions["anxious"] + 0.2)
        
        self.last_update = current_time
        self._update_relationship_context()
        
    def _apply_decay(self, current_time: datetime):
        """Apply emotion decay over time"""
        time_diff = (current_time - self.last_update).total_seconds() / 60  # minutes
        decay_factor = 1 - (self.decay_rate * time_diff)
        
        # Decay all emotions
        for emotion in self.emotions:
            self.emotions[emotion] = max(0.0, self.emotions[emotion] * decay_factor)
        
        for emotion in self.romantic_emotions:
            self.romantic_emotions[emotion] = max(0.0, self.romantic_emotions[emotion] * decay_factor)
    
    def _update_relationship_context(self):
        """Update relationship context based on interactions"""
        self.relationship_context["interaction_count"] += 1
        self.relationship_context["last_interaction"] = datetime.now()
        
        # Update relationship stage based on interaction count
        if self.relationship_context["interaction_count"] < 10:
            self.relationship_context["relationship_stage"] = "new"
        elif self.relationship_context["interaction_count"] < 50:
            self.relationship_context["relationship_stage"] = "developing"
        elif self.relationship_context["interaction_count"] < 200:
            self.relationship_context["relationship_stage"] = "established"
        else:
            self.relationship_context["relationship_stage"] = "long_term"
    
    def current_emotion(self) -> str:
        """Get the dominant emotion"""
        all_emotions = {**self.emotions, **self.romantic_emotions}
        if not all_emotions:
            return "neutral"
        
        dominant_emotion = max(all_emotions, key=all_emotions.get)
        return dominant_emotion if all_emotions[dominant_emotion] > 0.1 else "neutral"
    
    def get_romantic_context(self) -> Dict[str, any]:
        """Get romantic context for persona responses"""
        dominant_romantic_emotion = None
        romantic_intensity = 0.0
        
        if any(value > 0 for value in self.romantic_emotions.values()):
            dominant_romantic_emotion = max(self.romantic_emotions, key=lambda k: self.romantic_emotions[k])
            romantic_intensity = max(self.romantic_emotions.values())
        
        return {
            "dominant_romantic_emotion": dominant_romantic_emotion,
            "romantic_intensity": romantic_intensity,
            "relationship_stage": self.relationship_context["relationship_stage"],
            "interaction_count": self.relationship_context["interaction_count"],
            "days_since_start": self.relationship_context["relationship_duration_days"]
        }
    
    def add_milestone(self, milestone: str, date: Optional[datetime] = None):
        """Add a relationship milestone"""
        if date is None:
            date = datetime.now()
        self.relationship_context["milestones"].append({
            "description": milestone,
            "date": date,
            "emotions": self.to_dict()
        })
    
    def add_preference(self, category: str, preference: str):
        """Add a user preference"""
        if category not in self.relationship_context["preferences"]:
            self.relationship_context["preferences"][category] = []
        self.relationship_context["preferences"][category].append(preference)
    
    def add_shared_memory(self, memory: str, emotion: Optional[str] = None):
        """Add a shared memory"""
        self.relationship_context["shared_memories"].append({
            "description": memory,
            "date": datetime.now(),
            "emotion": emotion or self.current_emotion(),
            "context": self.to_dict()
        })
    
    def to_dict(self) -> Dict[str, any]:
        """Convert emotion state to dictionary"""
        return {
            "emotions": self.emotions.copy(),
            "romantic_emotions": self.romantic_emotions.copy(),
            "relationship_context": self.relationship_context.copy(),
            "current_emotion": self.current_emotion(),
            "last_update": self.last_update.isoformat()
        }
    
    def from_dict(self, data: Dict[str, any]):
        """Load emotion state from dictionary"""
        if "emotions" in data:
            self.emotions.update(data["emotions"])
        if "romantic_emotions" in data:
            self.romantic_emotions.update(data["romantic_emotions"])
        if "relationship_context" in data:
            self.relationship_context.update(data["relationship_context"])
        if "last_update" in data:
            self.last_update = datetime.fromisoformat(data["last_update"])

# Global emotion state instance
emotion_state = EmotionState() 