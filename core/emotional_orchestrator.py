#!/usr/bin/env python3
"""
Master Emotional Orchestrator - Central coordination for emotional state

This module provides centralized emotional state management and coordination
between the various emotional subsystems:
- Emotion Loop Core
- Reflection Engine  
- Memory Management
- Dream Logic
- Council Monitoring

Author: Emotional AI System
Date: August 3, 2025
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class EmotionalState(Enum):
    """Core emotional states"""
    NEUTRAL = "neutral"
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    LOVE = "love"
    EXCITEMENT = "excitement"
    CONTEMPLATIVE = "contemplative"
    EMPATHETIC = "empathetic"
    CREATIVE = "creative"

class EmotionalIntensity(Enum):
    """Emotional intensity levels"""
    SUBTLE = 0.2
    MILD = 0.4
    MODERATE = 0.6
    STRONG = 0.8
    INTENSE = 1.0

@dataclass
class EmotionalVector:
    """Multi-dimensional emotional state representation"""
    primary_emotion: EmotionalState
    intensity: float
    secondary_emotions: Dict[EmotionalState, float] = field(default_factory=dict)
    valence: float = 0.0  # -1.0 (negative) to 1.0 (positive)
    arousal: float = 0.0  # 0.0 (calm) to 1.0 (excited)
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "unknown"  # Which subsystem triggered this state
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EmotionalTransition:
    """Record of emotional state transitions"""
    from_state: EmotionalVector
    to_state: EmotionalVector
    trigger: str
    transition_time: datetime = field(default_factory=datetime.now)
    confidence: float = 1.0

@dataclass
class EmotionalMemory:
    """Consolidated emotional memory entry"""
    memory_id: str
    emotional_vector: EmotionalVector
    associated_content: str
    importance_score: float
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    decay_factor: float = 1.0

class MasterEmotionalOrchestrator:
    """Central coordinator for all emotional subsystems"""
    
    def __init__(self, config_path: str = "config/emotional_orchestrator.json"):
        self.config_path = config_path
        self.config = self._load_config()
        
        # Current emotional state
        self.current_state = EmotionalVector(
            primary_emotion=EmotionalState.NEUTRAL,
            intensity=0.5
        )
        
        # State tracking
        self.state_history = []  # List[EmotionalVector]
        self.transition_history = []  # List[EmotionalTransition]
        self.emotional_memories = {}  # memory_id -> EmotionalMemory
        
        # Subsystem coordination
        self.subsystem_states = {}  # subsystem_name -> current_state
        self.subsystem_weights = {  # How much each subsystem influences overall state
            "emotion_loop": 0.3,
            "reflection_engine": 0.2,
            "memory_system": 0.15,
            "dream_logic": 0.15,
            "council_monitor": 0.1,
            "user_interaction": 0.1
        }
        
        # Affect reactors - behavioral adaptations based on emotional state
        self.affect_reactors = {}
        self._setup_affect_reactors()
        
        # State persistence
        self.state_file = "data/emotional_state.json"
        self._load_persistent_state()
        
        logger.info("Master Emotional Orchestrator initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load orchestrator configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default configuration
            default_config = {
                "state_retention_hours": 168,  # 1 week
                "memory_consolidation_threshold": 0.7,
                "emotional_decay_rate": 0.01,
                "transition_smoothing": 0.3,
                "affect_reactor_sensitivity": 0.5
            }
            self._save_config(default_config)
            return default_config
        except Exception as e:
            logger.error(f"Error loading orchestrator config: {e}")
            return {}
    
    def _save_config(self, config: Dict[str, Any]):
        """Save orchestrator configuration"""
        try:
            import os
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving orchestrator config: {e}")
    
    def _setup_affect_reactors(self):
        """Setup behavioral adaptation reactors"""
        self.affect_reactors = {
            "response_tone": self._adjust_response_tone,
            "creativity_level": self._adjust_creativity,
            "empathy_sensitivity": self._adjust_empathy,
            "conversation_style": self._adjust_conversation_style,
            "memory_formation": self._adjust_memory_formation
        }
    
    async def register_subsystem_state(self, 
                                     subsystem: str, 
                                     emotional_vector: EmotionalVector):
        """Register emotional state from a subsystem"""
        self.subsystem_states[subsystem] = emotional_vector
        
        # Recalculate overall emotional state
        new_state = await self._calculate_unified_state()
        
        # Check for significant transition
        if self._is_significant_transition(self.current_state, new_state):
            transition = EmotionalTransition(
                from_state=self.current_state,
                to_state=new_state,
                trigger=f"subsystem_{subsystem}"
            )
            self.transition_history.append(transition)
            
            # Trigger affect reactors
            await self._trigger_affect_reactors(transition)
            
            logger.info(f"Emotional transition: {self.current_state.primary_emotion.value} -> {new_state.primary_emotion.value}")
        
        # Update current state
        self.current_state = new_state
        self.state_history.append(new_state)
        
        # Cleanup old history
        self._cleanup_old_states()
        
        # Persist state
        self._save_persistent_state()
    
    async def _calculate_unified_state(self) -> EmotionalVector:
        """Calculate unified emotional state from all subsystems"""
        if not self.subsystem_states:
            return self.current_state
        
        # Weighted average of emotional dimensions
        total_valence = 0.0
        total_arousal = 0.0
        total_intensity = 0.0
        emotion_votes = {}
        total_weight = 0.0
        
        for subsystem, state in self.subsystem_states.items():
            weight = self.subsystem_weights.get(subsystem, 0.1)
            total_weight += weight
            
            total_valence += state.valence * weight
            total_arousal += state.arousal * weight
            total_intensity += state.intensity * weight
            
            # Vote for primary emotion
            emotion_votes[state.primary_emotion] = emotion_votes.get(state.primary_emotion, 0) + weight
        
        if total_weight > 0:
            avg_valence = total_valence / total_weight
            avg_arousal = total_arousal / total_weight
            avg_intensity = total_intensity / total_weight
        else:
            avg_valence = self.current_state.valence
            avg_arousal = self.current_state.arousal
            avg_intensity = self.current_state.intensity
        
        # Determine primary emotion by vote
        primary_emotion = max(emotion_votes.items(), key=lambda x: x[1])[0] if emotion_votes else self.current_state.primary_emotion
        
        # Apply transition smoothing
        smoothing = self.config.get("transition_smoothing", 0.3)
        unified_state = EmotionalVector(
            primary_emotion=primary_emotion,
            intensity=self.current_state.intensity * smoothing + avg_intensity * (1 - smoothing),
            valence=self.current_state.valence * smoothing + avg_valence * (1 - smoothing),
            arousal=self.current_state.arousal * smoothing + avg_arousal * (1 - smoothing),
            source="unified_calculation"
        )
        
        return unified_state
    
    def _is_significant_transition(self, old_state: EmotionalVector, new_state: EmotionalVector) -> bool:
        """Determine if transition is significant enough to trigger reactions"""
        # Emotion change
        if old_state.primary_emotion != new_state.primary_emotion:
            return True
        
        # Significant intensity change
        intensity_change = abs(old_state.intensity - new_state.intensity)
        if intensity_change > 0.3:
            return True
        
        # Significant valence change
        valence_change = abs(old_state.valence - new_state.valence)
        if valence_change > 0.4:
            return True
        
        return False
    
    async def _trigger_affect_reactors(self, transition: EmotionalTransition):
        """Trigger behavioral adaptations based on emotional transition"""
        for reactor_name, reactor_func in self.affect_reactors.items():
            try:
                await reactor_func(transition)
            except Exception as e:
                logger.error(f"Error in affect reactor {reactor_name}: {e}")
    
    async def _adjust_response_tone(self, transition: EmotionalTransition):
        """Adjust response tone based on emotional state"""
        new_state = transition.to_state
        
        # This would integrate with the main AI response generation
        tone_adjustments = {
            "warmth": max(0.1, new_state.valence),
            "energy": new_state.arousal,
            "empathy": 1.0 if new_state.primary_emotion in [EmotionalState.EMPATHETIC, EmotionalState.SADNESS] else 0.5,
            "creativity": 1.0 if new_state.primary_emotion in [EmotionalState.CREATIVE, EmotionalState.EXCITEMENT] else 0.5
        }
        
        logger.debug(f"Tone adjustments: {tone_adjustments}")
    
    async def _adjust_creativity(self, transition: EmotionalTransition):
        """Adjust creativity level based on emotional state"""
        new_state = transition.to_state
        
        creativity_boost = 0.0
        if new_state.primary_emotion in [EmotionalState.CREATIVE, EmotionalState.JOY, EmotionalState.EXCITEMENT]:
            creativity_boost = new_state.intensity * 0.5
        
        logger.debug(f"Creativity boost: {creativity_boost}")
    
    async def _adjust_empathy(self, transition: EmotionalTransition):
        """Adjust empathy sensitivity based on emotional state"""
        new_state = transition.to_state
        
        empathy_level = 0.5  # baseline
        if new_state.primary_emotion in [EmotionalState.EMPATHETIC, EmotionalState.LOVE]:
            empathy_level = min(1.0, 0.7 + new_state.intensity * 0.3)
        elif new_state.primary_emotion in [EmotionalState.SADNESS]:
            empathy_level = min(1.0, 0.8 + new_state.intensity * 0.2)
        
        logger.debug(f"Empathy level: {empathy_level}")
    
    async def _adjust_conversation_style(self, transition: EmotionalTransition):
        """Adjust conversation style based on emotional state"""
        new_state = transition.to_state
        
        style_adjustments = {
            "formality": max(0.2, 0.5 - new_state.arousal * 0.3),
            "verbosity": 0.5 + new_state.intensity * 0.3,
            "playfulness": max(0.1, new_state.valence * 0.8)
        }
        
        logger.debug(f"Style adjustments: {style_adjustments}")
    
    async def _adjust_memory_formation(self, transition: EmotionalTransition):
        """Adjust memory formation based on emotional state"""
        new_state = transition.to_state
        
        # Higher emotional intensity = stronger memory formation
        memory_strength_multiplier = 0.5 + new_state.intensity * 0.5
        
        # Certain emotions create stronger memories
        if new_state.primary_emotion in [EmotionalState.LOVE, EmotionalState.FEAR, EmotionalState.JOY]:
            memory_strength_multiplier *= 1.3
        
        logger.debug(f"Memory strength multiplier: {memory_strength_multiplier}")
    
    async def store_emotional_memory(self, 
                                   content: str, 
                                   importance_score: float,
                                   context: Optional[Dict[str, Any]] = None) -> str:
        """Store an emotionally significant memory"""
        memory_id = f"mem_{int(datetime.now().timestamp())}_{len(self.emotional_memories)}"
        
        memory = EmotionalMemory(
            memory_id=memory_id,
            emotional_vector=self.current_state,
            associated_content=content,
            importance_score=importance_score
        )
        
        if context:
            memory.emotional_vector.context.update(context)
        
        self.emotional_memories[memory_id] = memory
        
        # Trigger memory consolidation if threshold reached
        if importance_score >= self.config.get("memory_consolidation_threshold", 0.7):
            await self._consolidate_memory(memory)
        
        logger.info(f"Stored emotional memory: {memory_id} (importance: {importance_score:.2f})")
        return memory_id
    
    async def _consolidate_memory(self, memory: EmotionalMemory):
        """Consolidate high-importance memories for long-term storage"""
        # This would integrate with the memory system to create lasting memories
        logger.info(f"Consolidating memory: {memory.memory_id}")
    
    def recall_emotional_memories(self, 
                                emotion_filter: Optional[EmotionalState] = None,
                                min_importance: float = 0.5,
                                max_age_hours: Optional[int] = None) -> List[EmotionalMemory]:
        """Recall emotional memories based on criteria"""
        memories = []
        current_time = datetime.now()
        
        for memory in self.emotional_memories.values():
            # Filter by emotion
            if emotion_filter and memory.emotional_vector.primary_emotion != emotion_filter:
                continue
            
            # Filter by importance
            if memory.importance_score < min_importance:
                continue
            
            # Filter by age
            if max_age_hours:
                age_hours = (current_time - memory.created_at).total_seconds() / 3600
                if age_hours > max_age_hours:
                    continue
            
            memories.append(memory)
        
        # Sort by importance and recency
        memories.sort(key=lambda m: (m.importance_score, m.created_at), reverse=True)
        return memories
    
    def get_emotional_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze emotional trends over time"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_states = [
            state for state in self.state_history
            if state.timestamp > cutoff_time
        ]
        
        if not recent_states:
            return {"error": "No recent emotional data"}
        
        # Calculate averages
        avg_valence = sum(state.valence for state in recent_states) / len(recent_states)
        avg_arousal = sum(state.arousal for state in recent_states) / len(recent_states)
        avg_intensity = sum(state.intensity for state in recent_states) / len(recent_states)
        
        # Emotion distribution
        emotion_counts = {}
        for state in recent_states:
            emotion = state.primary_emotion.value
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Transition patterns
        transition_count = len([t for t in self.transition_history if t.transition_time > cutoff_time])
        
        return {
            "period_hours": hours,
            "sample_count": len(recent_states),
            "avg_valence": round(avg_valence, 3),
            "avg_arousal": round(avg_arousal, 3),
            "avg_intensity": round(avg_intensity, 3),
            "emotion_distribution": emotion_counts,
            "transition_count": transition_count,
            "current_emotion": self.current_state.primary_emotion.value,
            "current_intensity": round(self.current_state.intensity, 3)
        }
    
    def _cleanup_old_states(self):
        """Remove old states to prevent memory bloat"""
        retention_hours = self.config.get("state_retention_hours", 168)  # 1 week
        cutoff_time = datetime.now() - timedelta(hours=retention_hours)
        
        self.state_history = [
            state for state in self.state_history
            if state.timestamp > cutoff_time
        ]
        
        self.transition_history = [
            transition for transition in self.transition_history
            if transition.transition_time > cutoff_time
        ]
    
    def _load_persistent_state(self):
        """Load persistent emotional state from disk"""
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
            
            # Restore current state
            if "current_state" in data:
                state_data = data["current_state"]
                self.current_state = EmotionalVector(
                    primary_emotion=EmotionalState(state_data["primary_emotion"]),
                    intensity=state_data["intensity"],
                    valence=state_data.get("valence", 0.0),
                    arousal=state_data.get("arousal", 0.0),
                    timestamp=datetime.fromisoformat(state_data["timestamp"])
                )
            
            # Restore memories
            if "emotional_memories" in data:
                for mem_id, mem_data in data["emotional_memories"].items():
                    # Reconstruct EmotionalMemory objects
                    pass  # Simplified for now
            
            logger.info("Loaded persistent emotional state")
            
        except FileNotFoundError:
            logger.info("No persistent state file found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading persistent state: {e}")
    
    def _save_persistent_state(self):
        """Save persistent emotional state to disk"""
        try:
            import os
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            
            data = {
                "current_state": {
                    "primary_emotion": self.current_state.primary_emotion.value,
                    "intensity": self.current_state.intensity,
                    "valence": self.current_state.valence,
                    "arousal": self.current_state.arousal,
                    "timestamp": self.current_state.timestamp.isoformat()
                },
                "emotional_memories": {
                    mem_id: {
                        "importance_score": mem.importance_score,
                        "created_at": mem.created_at.isoformat(),
                        "associated_content": mem.associated_content[:200]  # Truncate for storage
                    }
                    for mem_id, mem in self.emotional_memories.items()
                },
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving persistent state: {e}")

# Global orchestrator instance
emotional_orchestrator = MasterEmotionalOrchestrator()
