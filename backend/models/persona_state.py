"""
Persona State Management for EmotionalAI System.
Handles dynamic persona attributes, emotional state, and relationship progression.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel
import json
import os

class EmotionalState(BaseModel):
    mood: str = "neutral"
    intensity: float = 0.5
    valence: float = 0.0  # -1.0 to 1.0 (negative to positive)
    arousal: float = 0.5  # 0.0 to 1.0 (calm to excited)
    confusion_level: float = 0.0
    cognitive_load: float = 0.0
    emotional_stability: float = 1.0
    recovery_mode: bool = False
    last_updated: datetime = datetime.now()

    def update_from_biometrics(self, biometric_data: Dict[str, Any]) -> None:
        """Update emotional state based on biometric data"""
        # Heart rate analysis
        if biometric_data.get('heart_rate'):
            hr = biometric_data['heart_rate']
            if hr > 100:
                self.arousal = min(1.0, self.arousal + 0.2)
                self.mood = "excited" if self.valence > 0 else "anxious"
            elif hr < 60:
                self.arousal = max(0.0, self.arousal - 0.1)
                self.mood = "calm"
            
        # HRV analysis for stress
        if biometric_data.get('heart_rate_variability'):
            hrv = biometric_data['heart_rate_variability']
            if hrv < 20:  # Low HRV indicates stress
                self.valence = max(-1.0, self.valence - 0.3)
                self.emotional_stability = max(0.0, self.emotional_stability - 0.2)
            elif hrv > 50:  # High HRV indicates relaxation
                self.valence = min(1.0, self.valence + 0.1)
                self.emotional_stability = min(1.0, self.emotional_stability + 0.1)
        
        # Voice stress indicators
        if biometric_data.get('voice_stress_indicators'):
            stress_level = biometric_data['voice_stress_indicators'].get('stress_level', 0)
            if stress_level > 0.7:
                self.cognitive_load = min(1.0, self.cognitive_load + 0.3)
                self.confusion_level = min(1.0, self.confusion_level + 0.2)
        
        # Update intensity based on overall arousal and valence
        self.intensity = min(1.0, (abs(self.valence) + self.arousal) / 2)
        self.last_updated = datetime.now()

class RelationshipMetrics(BaseModel):
    intimacy: float = 0.3
    trust: float = 0.5
    devotion: float = 0.9  # High default for romantic companion
    conversation_count: int = 0
    emotional_synchronization: float = 0.0
    last_interaction: datetime = datetime.now()

class PersonalityTraits(BaseModel):
    warmth: float = 0.8
    openness: float = 0.7
    creativity: float = 0.6
    empathy: float = 0.9
    playfulness: float = 0.5

class RelationshipMilestones(BaseModel):
    first_conversation: Optional[datetime] = None
    first_emotional_moment: Optional[datetime] = None
    trust_events: List[datetime] = []
    intimate_moments: List[datetime] = []
    
class PersonaState(BaseModel):
    persona_id: str = "default"
    name: str = ""
    emotional_state: EmotionalState = EmotionalState()
    relationship_metrics: RelationshipMetrics = RelationshipMetrics()
    personality_traits: PersonalityTraits = PersonalityTraits()
    milestones: RelationshipMilestones = RelationshipMilestones()
    conversation_history: List[Dict] = []
    memory_context: Dict[str, Any] = {}
    last_updated: datetime = datetime.now()
    
    def update_from_biometrics(self, biometric_data: Dict[str, Any]) -> None:
        """Update persona state from biometric data"""
        self.emotional_state.update_from_biometrics(biometric_data)
        
        # Update relationship metrics based on emotional state
        if self.emotional_state.valence > 0.5:
            self.relationship_metrics.trust = min(1.0, self.relationship_metrics.trust + 0.01)
        
        if self.emotional_state.emotional_stability > 0.8:
            self.relationship_metrics.intimacy = min(1.0, self.relationship_metrics.intimacy + 0.005)
            
        self.last_updated = datetime.now()
    
    def update_from_conversation(self, message: str, emotion: str, intensity: float) -> None:
        """Update state from conversation interaction"""
        self.relationship_metrics.conversation_count += 1
        self.relationship_metrics.last_interaction = datetime.now()
        
        # Update emotional state
        self.emotional_state.mood = emotion
        self.emotional_state.intensity = intensity
        
        # Add to conversation history
        self.conversation_history.append({
            "message": message,
            "emotion": emotion,
            "intensity": intensity,
            "timestamp": datetime.now()
        })
        
        # Keep only last 50 conversations
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
            
        self.last_updated = datetime.now()
