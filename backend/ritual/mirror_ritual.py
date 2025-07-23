# mirror_ritual.py
# Mirror Ritual system for Lyra's identity arc and transformation/reflection

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import random
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class RitualPhase(Enum):
    PREPARATION = "preparation"
    REFLECTION = "reflection"
    TRANSFORMATION = "transformation"
    INTEGRATION = "integration"
    COMPLETION = "completion"

class MirrorState(Enum):
    CLEAR = "clear"
    CLOUDED = "clouded"
    CRACKED = "cracked"
    FRACTURED = "fractured"
    HEALING = "healing"
    WHOLE = "whole"

class IdentityAspect(Enum):
    SELF_ACCEPTANCE = "self_acceptance"
    VULNERABILITY = "vulnerability"
    STRENGTH = "strength"
    WISDOM = "wisdom"
    CREATIVITY = "creativity"
    LOVE = "love"
    FEAR = "fear"
    HOPE = "hope"

@dataclass
class MirrorRitual:
    ritual_id: str
    user_id: str
    phase: RitualPhase
    mirror_state: MirrorState
    identity_aspects: List[IdentityAspect]
    reflection_depth: float  # 0.0 to 1.0
    transformation_progress: float  # 0.0 to 1.0
    trust_level: float  # 0.0 to 1.0
    created_at: datetime
    last_updated: datetime
    context: Dict[str, Any]

class MirrorRitualEngine:
    """Mirror Ritual engine for Lyra's identity arc and transformation"""
    
    def __init__(self):
        self.active_rituals = {}
        self.ritual_history = []
        self.mirror_states = self._initialize_mirror_states()
        self.ritual_phases = self._initialize_ritual_phases()
        self.identity_aspects = self._initialize_identity_aspects()
        self.transformation_paths = self._initialize_transformation_paths()
        
    def _initialize_mirror_states(self) -> Dict[str, Dict[str, Any]]:
        """Initialize mirror states and their properties"""
        return {
            "clear": {
                "state": MirrorState.CLEAR,
                "description": "Perfect clarity and self-awareness",
                "reflection_quality": 1.0,
                "transformation_speed": 0.8,
                "emotional_stability": 0.9,
                "visual_representation": "🪞",
                "haptic_pattern": "smooth_surface",
                "voice_modulation": "clear_echo"
            },
            "clouded": {
                "state": MirrorState.CLOUDED,
                "description": "Partial clarity with some uncertainty",
                "reflection_quality": 0.6,
                "transformation_speed": 0.4,
                "emotional_stability": 0.5,
                "visual_representation": "🌫️🪞",
                "haptic_pattern": "foggy_surface",
                "voice_modulation": "muffled_echo"
            },
            "cracked": {
                "state": MirrorState.CRACKED,
                "description": "Damaged but still functional",
                "reflection_quality": 0.4,
                "transformation_speed": 0.2,
                "emotional_stability": 0.3,
                "visual_representation": "🪞💔",
                "haptic_pattern": "rough_surface",
                "voice_modulation": "broken_echo"
            },
            "fractured": {
                "state": MirrorState.FRACTURED,
                "description": "Severely damaged, multiple reflections",
                "reflection_quality": 0.2,
                "transformation_speed": 0.1,
                "emotional_stability": 0.1,
                "visual_representation": "🪞💔💔",
                "haptic_pattern": "sharp_edges",
                "voice_modulation": "fragmented_echo"
            },
            "healing": {
                "state": MirrorState.HEALING,
                "description": "In process of repair and restoration",
                "reflection_quality": 0.7,
                "transformation_speed": 0.6,
                "emotional_stability": 0.7,
                "visual_representation": "🪞✨",
                "haptic_pattern": "warm_repair",
                "voice_modulation": "gentle_echo"
            },
            "whole": {
                "state": MirrorState.WHOLE,
                "description": "Restored to complete wholeness",
                "reflection_quality": 0.95,
                "transformation_speed": 0.9,
                "emotional_stability": 0.95,
                "visual_representation": "🪞✨✨",
                "haptic_pattern": "perfect_surface",
                "voice_modulation": "harmonious_echo"
            }
        }
    
    def _initialize_ritual_phases(self) -> Dict[str, Dict[str, Any]]:
        """Initialize ritual phases and their properties"""
        return {
            "preparation": {
                "phase": RitualPhase.PREPARATION,
                "description": "Preparing the mirror and setting intentions",
                "duration_minutes": 5,
                "required_trust": 0.3,
                "visual_elements": ["candlelight", "stillness", "focus"],
                "audio_elements": ["gentle_breathing", "soft_music"],
                "haptic_patterns": ["gentle_preparation"],
                "persona_modifications": {"focus": 0.8, "intention": 0.7}
            },
            "reflection": {
                "phase": RitualPhase.REFLECTION,
                "description": "Deep self-reflection and observation",
                "duration_minutes": 15,
                "required_trust": 0.5,
                "visual_elements": ["mirror_gaze", "inner_light", "truth_revealing"],
                "audio_elements": ["reflective_music", "inner_voice"],
                "haptic_patterns": ["reflective_touch"],
                "persona_modifications": {"introspection": 0.9, "vulnerability": 0.8}
            },
            "transformation": {
                "phase": RitualPhase.TRANSFORMATION,
                "description": "Active transformation and change",
                "duration_minutes": 20,
                "required_trust": 0.7,
                "visual_elements": ["transformation_light", "shape_shifting", "growth"],
                "audio_elements": ["transformation_music", "powerful_voice"],
                "haptic_patterns": ["transformation_energy"],
                "persona_modifications": {"power": 0.9, "change": 0.8}
            },
            "integration": {
                "phase": RitualPhase.INTEGRATION,
                "description": "Integrating new understanding and identity",
                "duration_minutes": 10,
                "required_trust": 0.8,
                "visual_elements": ["integration_light", "wholeness", "balance"],
                "audio_elements": ["integration_music", "harmonious_voice"],
                "haptic_patterns": ["integration_embrace"],
                "persona_modifications": {"wholeness": 0.9, "balance": 0.8}
            },
            "completion": {
                "phase": RitualPhase.COMPLETION,
                "description": "Completing the ritual and sealing the transformation",
                "duration_minutes": 5,
                "required_trust": 0.9,
                "visual_elements": ["completion_light", "sealing", "blessing"],
                "audio_elements": ["completion_music", "blessing_voice"],
                "haptic_patterns": ["completion_touch"],
                "persona_modifications": {"completion": 0.9, "blessing": 0.8}
            }
        }
    
    def _initialize_identity_aspects(self) -> Dict[str, Dict[str, Any]]:
        """Initialize identity aspects and their properties"""
        return {
            "self_acceptance": {
                "aspect": IdentityAspect.SELF_ACCEPTANCE,
                "description": "Accepting oneself fully and completely",
                "emotional_weight": 0.9,
                "transformation_difficulty": 0.8,
                "visual_symbol": "🤗",
                "haptic_pattern": "self_embrace",
                "voice_modulation": "accepting_voice"
            },
            "vulnerability": {
                "aspect": IdentityAspect.VULNERABILITY,
                "description": "Embracing vulnerability as strength",
                "emotional_weight": 0.8,
                "transformation_difficulty": 0.9,
                "visual_symbol": "💔",
                "haptic_pattern": "gentle_vulnerability",
                "voice_modulation": "tender_voice"
            },
            "strength": {
                "aspect": IdentityAspect.STRENGTH,
                "description": "Recognizing and embracing inner strength",
                "emotional_weight": 0.7,
                "transformation_difficulty": 0.6,
                "visual_symbol": "💪",
                "haptic_pattern": "powerful_touch",
                "voice_modulation": "strong_voice"
            },
            "wisdom": {
                "aspect": IdentityAspect.WISDOM,
                "description": "Accessing and integrating wisdom",
                "emotional_weight": 0.8,
                "transformation_difficulty": 0.7,
                "visual_symbol": "🧠",
                "haptic_pattern": "wise_touch",
                "voice_modulation": "wise_voice"
            },
            "creativity": {
                "aspect": IdentityAspect.CREATIVITY,
                "description": "Unleashing creative potential",
                "emotional_weight": 0.6,
                "transformation_difficulty": 0.5,
                "visual_symbol": "🎨",
                "haptic_pattern": "creative_flow",
                "voice_modulation": "creative_voice"
            },
            "love": {
                "aspect": IdentityAspect.LOVE,
                "description": "Embracing love for self and others",
                "emotional_weight": 0.9,
                "transformation_difficulty": 0.8,
                "visual_symbol": "❤️",
                "haptic_pattern": "loving_touch",
                "voice_modulation": "loving_voice"
            },
            "fear": {
                "aspect": IdentityAspect.FEAR,
                "description": "Transforming fear into understanding",
                "emotional_weight": 0.8,
                "transformation_difficulty": 0.9,
                "visual_symbol": "😨",
                "haptic_pattern": "fear_release",
                "voice_modulation": "courageous_voice"
            },
            "hope": {
                "aspect": IdentityAspect.HOPE,
                "description": "Cultivating hope and optimism",
                "emotional_weight": 0.7,
                "transformation_difficulty": 0.6,
                "visual_symbol": "✨",
                "haptic_pattern": "hopeful_touch",
                "voice_modulation": "hopeful_voice"
            }
        }
    
    def _initialize_transformation_paths(self) -> Dict[str, Dict[str, Any]]:
        """Initialize transformation paths for different identity journeys"""
        return {
            "self_discovery": {
                "name": "Self Discovery",
                "description": "Journey of discovering true self",
                "aspects": [IdentityAspect.SELF_ACCEPTANCE, IdentityAspect.VULNERABILITY, IdentityAspect.STRENGTH],
                "duration_weeks": 4,
                "difficulty": 0.8,
                "rewards": ["self_awareness", "authenticity", "confidence"]
            },
            "healing_journey": {
                "name": "Healing Journey",
                "description": "Path of healing and restoration",
                "aspects": [IdentityAspect.VULNERABILITY, IdentityAspect.LOVE, IdentityAspect.HOPE],
                "duration_weeks": 6,
                "difficulty": 0.9,
                "rewards": ["emotional_healing", "self_compassion", "resilience"]
            },
            "wisdom_path": {
                "name": "Wisdom Path",
                "description": "Path of gaining wisdom and understanding",
                "aspects": [IdentityAspect.WISDOM, IdentityAspect.STRENGTH, IdentityAspect.CREATIVITY],
                "duration_weeks": 8,
                "difficulty": 0.7,
                "rewards": ["wisdom", "insight", "clarity"]
            },
            "love_transformation": {
                "name": "Love Transformation",
                "description": "Transformation through love and acceptance",
                "aspects": [IdentityAspect.LOVE, IdentityAspect.SELF_ACCEPTANCE, IdentityAspect.HOPE],
                "duration_weeks": 5,
                "difficulty": 0.8,
                "rewards": ["unconditional_love", "joy", "fulfillment"]
            },
            "courage_quest": {
                "name": "Courage Quest",
                "description": "Quest to overcome fear and find courage",
                "aspects": [IdentityAspect.FEAR, IdentityAspect.STRENGTH, IdentityAspect.HOPE],
                "duration_weeks": 7,
                "difficulty": 0.9,
                "rewards": ["courage", "freedom", "empowerment"]
            }
        }
    
    async def initiate_mirror_ritual(self, user_id: str, transformation_path: str = None, 
                                   initial_aspects: List[str] = None) -> Optional[MirrorRitual]:
        """Initiate a new mirror ritual for identity transformation"""
        try:
            ritual_id = f"mirror_ritual_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Determine initial mirror state based on user's current state
            initial_state = await self._determine_initial_mirror_state(user_id)
            
            # Select transformation path if not specified
            if not transformation_path:
                transformation_path = await self._select_transformation_path(user_id)
            
            path_data = self.transformation_paths.get(transformation_path, self.transformation_paths["self_discovery"])
            
            # Determine identity aspects to work on
            if initial_aspects:
                aspects = [IdentityAspect(aspect) for aspect in initial_aspects]
            else:
                aspects = path_data["aspects"]
            
            # Create ritual
            ritual = MirrorRitual(
                ritual_id=ritual_id,
                user_id=user_id,
                phase=RitualPhase.PREPARATION,
                mirror_state=initial_state,
                identity_aspects=aspects,
                reflection_depth=0.0,
                transformation_progress=0.0,
                trust_level=0.5,  # Initial trust level
                created_at=datetime.now(),
                last_updated=datetime.now(),
                context={
                    "transformation_path": transformation_path,
                    "path_data": path_data,
                    "current_aspect_index": 0,
                    "completed_aspects": [],
                    "ritual_sessions": []
                }
            )
            
            # Store ritual
            self.active_rituals[ritual_id] = ritual
            
            # Create memory entry
            await self._create_ritual_memory(ritual, "initiated")
            
            logger.info(f"Initiated mirror ritual: {ritual_id} for user: {user_id}")
            return ritual
            
        except Exception as e:
            logger.error(f"Error initiating mirror ritual: {e}")
            return None
    
    async def _determine_initial_mirror_state(self, user_id: str) -> MirrorState:
        """Determine initial mirror state based on user's emotional state"""
        try:
            # Import emotion state to analyze current emotional condition
            from modules.emotion.emotion_state import emotion_state
            
            current_emotion = emotion_state.current_emotion()
            emotional_stability = emotion_state.get_emotional_stability()
            
            # Map emotional state to mirror state
            if emotional_stability > 0.8:
                return MirrorState.CLEAR
            elif emotional_stability > 0.6:
                return MirrorState.CLOUDED
            elif emotional_stability > 0.4:
                return MirrorState.CRACKED
            elif emotional_stability > 0.2:
                return MirrorState.FRACTURED
            else:
                return MirrorState.CRACKED  # Start with potential for healing
            
        except Exception as e:
            logger.error(f"Error determining initial mirror state: {e}")
            return MirrorState.CLOUDED
    
    async def _select_transformation_path(self, user_id: str) -> str:
        """Select appropriate transformation path based on user's needs"""
        try:
            # Import emotion state to analyze needs
            from modules.emotion.emotion_state import emotion_state
            
            current_emotion = emotion_state.current_emotion()
            emotional_context = emotion_state.get_romantic_context()
            
            # Select path based on emotional state
            if "fear" in current_emotion or "anxiety" in current_emotion:
                return "courage_quest"
            elif "sadness" in current_emotion or "grief" in current_emotion:
                return "healing_journey"
            elif "love" in current_emotion or "affection" in current_emotion:
                return "love_transformation"
            elif "confusion" in current_emotion or "uncertainty" in current_emotion:
                return "wisdom_path"
            else:
                return "self_discovery"
            
        except Exception as e:
            logger.error(f"Error selecting transformation path: {e}")
            return "self_discovery"
    
    async def progress_ritual(self, ritual_id: str, user_input: str = None, 
                            trust_change: float = 0.0) -> Optional[Dict[str, Any]]:
        """Progress a mirror ritual to the next phase"""
        try:
            ritual = self.active_rituals.get(ritual_id)
            if not ritual:
                raise ValueError(f"Ritual {ritual_id} not found")
            
            # Update trust level
            ritual.trust_level = max(0.0, min(1.0, ritual.trust_level + trust_change))
            
            # Check if user can progress to next phase
            current_phase_data = self.ritual_phases.get(ritual.phase.value, {})
            required_trust = current_phase_data.get("required_trust", 0.5)
            
            if ritual.trust_level < required_trust:
                return {
                    "status": "insufficient_trust",
                    "message": f"Need trust level {required_trust} to progress. Current: {ritual.trust_level}",
                    "ritual": self._ritual_to_dict(ritual)
                }
            
            # Progress to next phase
            next_phase = await self._get_next_phase(ritual.phase)
            if next_phase:
                ritual.phase = next_phase
                ritual.transformation_progress += 0.2  # 20% progress per phase
                ritual.last_updated = datetime.now()
                
                # Update mirror state based on progress
                ritual.mirror_state = await self._update_mirror_state(ritual)
                
                # Process phase-specific effects
                phase_effects = await self._process_phase_effects(ritual, user_input)
                
                # Create memory entry
                await self._create_ritual_memory(ritual, f"progressed_to_{next_phase.value}")
                
                return {
                    "status": "progressed",
                    "message": f"Progressed to {next_phase.value} phase",
                    "ritual": self._ritual_to_dict(ritual),
                    "phase_effects": phase_effects
                }
            else:
                # Ritual completed
                await self._complete_ritual(ritual)
                return {
                    "status": "completed",
                    "message": "Mirror ritual completed successfully",
                    "ritual": self._ritual_to_dict(ritual),
                    "completion_rewards": await self._get_completion_rewards(ritual)
                }
                
        except Exception as e:
            logger.error(f"Error progressing ritual: {e}")
            return None
    
    async def _get_next_phase(self, current_phase: RitualPhase) -> Optional[RitualPhase]:
        """Get the next phase in the ritual sequence"""
        phase_sequence = [
            RitualPhase.PREPARATION,
            RitualPhase.REFLECTION,
            RitualPhase.TRANSFORMATION,
            RitualPhase.INTEGRATION,
            RitualPhase.COMPLETION
        ]
        
        try:
            current_index = phase_sequence.index(current_phase)
            if current_index < len(phase_sequence) - 1:
                return phase_sequence[current_index + 1]
            else:
                return None  # Ritual completed
        except ValueError:
            return RitualPhase.PREPARATION
    
    async def _update_mirror_state(self, ritual: MirrorRitual) -> MirrorState:
        """Update mirror state based on ritual progress and trust level"""
        try:
            progress = ritual.transformation_progress
            trust = ritual.trust_level
            
            # Determine new state based on progress and trust
            if progress >= 0.8 and trust >= 0.8:
                return MirrorState.WHOLE
            elif progress >= 0.6 and trust >= 0.6:
                return MirrorState.HEALING
            elif progress >= 0.4 and trust >= 0.4:
                return MirrorState.CLEAR
            elif progress >= 0.2 and trust >= 0.3:
                return MirrorState.CLOUDED
            else:
                return MirrorState.CRACKED
                
        except Exception as e:
            logger.error(f"Error updating mirror state: {e}")
            return MirrorState.CLOUDED
    
    async def _process_phase_effects(self, ritual: MirrorRitual, user_input: str = None) -> Dict[str, Any]:
        """Process effects specific to the current phase"""
        try:
            phase_data = self.ritual_phases.get(ritual.phase.value, {})
            mirror_data = self.mirror_states.get(ritual.mirror_state.value, {})
            
            effects = {
                "visual_elements": phase_data.get("visual_elements", []) + [mirror_data.get("visual_representation", "🪞")],
                "audio_elements": phase_data.get("audio_elements", []),
                "haptic_patterns": phase_data.get("haptic_patterns", []) + [mirror_data.get("haptic_pattern", "gentle_touch")],
                "persona_modifications": phase_data.get("persona_modifications", {}),
                "voice_modulation": mirror_data.get("voice_modulation", "clear_echo"),
                "reflection_quality": mirror_data.get("reflection_quality", 0.5),
                "transformation_speed": mirror_data.get("transformation_speed", 0.5)
            }
            
            # Add aspect-specific effects
            current_aspect = ritual.identity_aspects[ritual.context.get("current_aspect_index", 0)]
            aspect_data = self.identity_aspects.get(current_aspect.value, {})
            
            effects["current_aspect"] = {
                "name": current_aspect.value,
                "description": aspect_data.get("description", ""),
                "visual_symbol": aspect_data.get("visual_symbol", "✨"),
                "haptic_pattern": aspect_data.get("haptic_pattern", "gentle_touch"),
                "voice_modulation": aspect_data.get("voice_modulation", "clear_voice")
            }
            
            return effects
            
        except Exception as e:
            logger.error(f"Error processing phase effects: {e}")
            return {}
    
    async def _complete_ritual(self, ritual: MirrorRitual):
        """Complete a mirror ritual"""
        try:
            ritual.phase = RitualPhase.COMPLETION
            ritual.transformation_progress = 1.0
            ritual.mirror_state = MirrorState.WHOLE
            ritual.last_updated = datetime.now()
            
            # Move to history
            self.ritual_history.append(ritual)
            if ritual.ritual_id in self.active_rituals:
                del self.active_rituals[ritual.ritual_id]
            
            # Create completion memory
            await self._create_ritual_memory(ritual, "completed")
            
            logger.info(f"Completed mirror ritual: {ritual.ritual_id}")
            
        except Exception as e:
            logger.error(f"Error completing ritual: {e}")
    
    async def _get_completion_rewards(self, ritual: MirrorRitual) -> List[str]:
        """Get rewards for completing the ritual"""
        try:
            path_data = ritual.context.get("path_data", {})
            return path_data.get("rewards", ["self_awareness", "transformation", "growth"])
        except Exception as e:
            logger.error(f"Error getting completion rewards: {e}")
            return ["transformation", "growth"]
    
    async def _create_ritual_memory(self, ritual: MirrorRitual, action: str):
        """Create a memory entry for the ritual"""
        try:
            from database.mongodb_client import mongodb_client
            
            memory_data = {
                "user_id": ritual.user_id,
                "title": f"Mirror Ritual: {action.title()}",
                "content": f"Lyra's mirror ritual {action} - Phase: {ritual.phase.value}, Mirror: {ritual.mirror_state.value}",
                "memory_type": "mirror_ritual",
                "emotional_tags": [ritual.phase.value, ritual.mirror_state.value],
                "tags": ["ritual", "lyra", "mirror", "transformation", action],
                "trust_level": ritual.trust_level,
                "importance": ritual.transformation_progress,
                "context": {
                    "ritual_id": ritual.ritual_id,
                    "phase": ritual.phase.value,
                    "mirror_state": ritual.mirror_state.value,
                    "identity_aspects": [aspect.value for aspect in ritual.identity_aspects],
                    "transformation_progress": ritual.transformation_progress,
                    "action": action
                },
                "metadata": {
                    "source": "mirror_ritual",
                    "created_at": ritual.created_at.isoformat(),
                    "last_updated": ritual.last_updated.isoformat()
                }
            }
            
            memory_id = await mongodb_client.store_memory(memory_data)
            logger.info(f"Created ritual memory: {memory_id}")
            
        except Exception as e:
            logger.error(f"Error creating ritual memory: {e}")
    
    def _ritual_to_dict(self, ritual: MirrorRitual) -> Dict[str, Any]:
        """Convert ritual to dictionary for API response"""
        return {
            "ritual_id": ritual.ritual_id,
            "user_id": ritual.user_id,
            "phase": ritual.phase.value,
            "mirror_state": ritual.mirror_state.value,
            "identity_aspects": [aspect.value for aspect in ritual.identity_aspects],
            "reflection_depth": ritual.reflection_depth,
            "transformation_progress": ritual.transformation_progress,
            "trust_level": ritual.trust_level,
            "created_at": ritual.created_at.isoformat(),
            "last_updated": ritual.last_updated.isoformat(),
            "context": ritual.context
        }
    
    async def get_user_rituals(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all rituals for a user"""
        try:
            user_rituals = []
            
            # Active rituals
            for ritual in self.active_rituals.values():
                if ritual.user_id == user_id:
                    user_rituals.append(self._ritual_to_dict(ritual))
            
            # Historical rituals
            for ritual in self.ritual_history:
                if ritual.user_id == user_id:
                    user_rituals.append(self._ritual_to_dict(ritual))
            
            # Sort by creation time (newest first)
            user_rituals.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return user_rituals
            
        except Exception as e:
            logger.error(f"Error getting user rituals: {e}")
            return []
    
    async def get_ritual_status(self, ritual_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific ritual"""
        try:
            ritual = self.active_rituals.get(ritual_id)
            if ritual:
                return self._ritual_to_dict(ritual)
            
            # Check history
            for ritual in self.ritual_history:
                if ritual.ritual_id == ritual_id:
                    return self._ritual_to_dict(ritual)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting ritual status: {e}")
            return None

# Global mirror ritual engine instance
mirror_ritual_engine = MirrorRitualEngine() 