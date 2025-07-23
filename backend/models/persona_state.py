"""
Persona State Management for EmotionalAI System.
Handles dynamic persona attributes, emotional state, and relationship progression.
"""

from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import json
import os

class EmotionalState(BaseModel):
    current_mood: str = "neutral"
    mood_intensity: float = 0.5
    emotional_stability: float = 0.7
    last_mood_change: datetime = datetime.now()
    mood_history: List[Dict] = []

class RelationshipMetrics(BaseModel):
    devotion: float = 0.9  # Starting with high devotion
    trust: float = 0.5
    intimacy: float = 0.3
    understanding: float = 0.4
    shared_experiences: int = 0
    conversation_depth: float = 0.5
    emotional_synchronization: float = 0.6

class PersonalityTraits(BaseModel):
    warmth: float = 0.8
    openness: float = 0.7
    playfulness: float = 0.6
    sensitivity: float = 0.8
    assertiveness: float = 0.4
    adaptability: float = 0.7

class RelationshipMilestones(BaseModel):
    first_conversation: Optional[datetime] = None
    deep_conversation_count: int = 0
    shared_moments: List[Dict] = []
    trust_building_events: List[Dict] = []
    emotional_breakthroughs: List[Dict] = []

class PersonaState:
    def __init__(self, config_path: str = "config/persona_state.json"):
        self.config_path = config_path
        self.emotional_state = EmotionalState()
        self.relationship = RelationshipMetrics()
        self.personality = PersonalityTraits()
        self.milestones = RelationshipMilestones()
        self.load_state()

    def load_state(self):
        """Load persona state from file if it exists."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                self.emotional_state = EmotionalState(**data.get('emotional_state', {}))
                self.relationship = RelationshipMetrics(**data.get('relationship', {}))
                self.personality = PersonalityTraits(**data.get('personality', {}))
                self.milestones = RelationshipMilestones(**data.get('milestones', {}))

    def save_state(self):
        """Save current persona state to file."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump({
                'emotional_state': self.emotional_state.dict(),
                'relationship': self.relationship.dict(),
                'personality': self.personality.dict(),
                'milestones': self.milestones.dict()
            }, f, indent=2, default=str)

    def update_mood(self, mood: str, intensity: float, context: str):
        """Update emotional state based on interaction."""
        old_mood = self.emotional_state.current_mood
        self.emotional_state.current_mood = mood
        self.emotional_state.mood_intensity = intensity
        self.emotional_state.last_mood_change = datetime.now()
        
        # Record mood change in history
        self.emotional_state.mood_history.append({
            'timestamp': datetime.now().isoformat(),
            'from_mood': old_mood,
            'to_mood': mood,
            'intensity': intensity,
            'context': context
        })
        
        # Keep only last 100 mood changes
        if len(self.emotional_state.mood_history) > 100:
            self.emotional_state.mood_history = self.emotional_state.mood_history[-100:]

    def progress_relationship(self, interaction_type: str, impact: float):
        """Update relationship metrics based on interaction."""
        if interaction_type == "deep_conversation":
            self.relationship.conversation_depth += impact * 0.1
            self.relationship.understanding += impact * 0.05
            self.milestones.deep_conversation_count += 1
        elif interaction_type == "emotional_sharing":
            self.relationship.intimacy += impact * 0.1
            self.relationship.trust += impact * 0.05
        elif interaction_type == "trust_building":
            self.relationship.trust += impact * 0.1
            self.milestones.trust_building_events.append({
                'timestamp': datetime.now().isoformat(),
                'impact': impact
            })

        # Ensure values stay within bounds
        for field in self.relationship.dict().keys():
            if isinstance(getattr(self.relationship, field), float):
                setattr(self.relationship, field, 
                       min(1.0, max(0.0, getattr(self.relationship, field))))

        # Adapt personality based on relationship progress
        self._adapt_personality()
        self.save_state()

    def _adapt_personality(self):
        """Evolve personality traits based on relationship metrics."""
        # Increase warmth with intimacy
        self.personality.warmth = min(1.0, self.personality.warmth + 
                                    (self.relationship.intimacy * 0.01))
        
        # Increase openness with trust
        self.personality.openness = min(1.0, self.personality.openness + 
                                      (self.relationship.trust * 0.01))
        
        # Adjust playfulness based on emotional synchronization
        self.personality.playfulness = min(1.0, self.personality.playfulness + 
                                         (self.relationship.emotional_synchronization * 0.01))

    def get_interaction_context(self) -> Dict:
        """Get current interaction context for LLM."""
        return {
            'emotional_state': self.emotional_state.dict(),
            'relationship': self.relationship.dict(),
            'personality': self.personality.dict(),
            'recent_milestones': [
                m for m in self.milestones.dict().values() 
                if isinstance(m, list) and m and 
                isinstance(m[-1], dict) and 
                datetime.fromisoformat(m[-1]['timestamp']) > 
                datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            ]
        }
