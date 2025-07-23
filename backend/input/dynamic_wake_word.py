# dynamic_wake_word.py
# Dynamic wake word system with context-aware modes

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, time
import random
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class WakeMode(Enum):
    NORMAL = "normal"
    WHISPER = "whisper"
    SILENT = "silent"
    INTIMATE = "intimate"
    RITUAL = "ritual"
    EMERGENCY = "emergency"
    SLEEP = "sleep"

class TimeContext(Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"
    LATE_NIGHT = "late_night"
    EARLY_MORNING = "early_morning"

class EnvironmentContext(Enum):
    HOME = "home"
    BEDROOM = "bedroom"
    LIVING_ROOM = "living_room"
    KITCHEN = "kitchen"
    BATHROOM = "bathroom"
    OUTDOOR = "outdoor"
    PUBLIC = "public"
    PRIVATE = "private"

@dataclass
class WakeContext:
    time_context: TimeContext
    environment: EnvironmentContext
    user_mood: str
    persona_state: str
    trust_level: float
    privacy_level: float
    noise_level: float  # 0.0 (quiet) to 1.0 (loud)

class DynamicWakeWordEngine:
    """Dynamic wake word engine with context-aware modes"""
    
    def __init__(self):
        self.wake_modes = self._initialize_wake_modes()
        self.context_rules = self._initialize_context_rules()
        self.wake_words = self._initialize_wake_words()
        self.active_mode = WakeMode.NORMAL
        self.current_context = None
        self.mode_history = []
        
    def _initialize_wake_modes(self) -> Dict[str, Dict[str, Any]]:
        """Initialize wake word modes with different behaviors"""
        return {
            "normal": {
                "mode": WakeMode.NORMAL,
                "description": "Standard wake word behavior",
                "sensitivity": 0.7,
                "response_volume": 0.8,
                "response_speed": "normal",
                "persona_modifications": {},
                "visual_feedback": "standard",
                "haptic_feedback": "gentle"
            },
            "whisper": {
                "mode": WakeMode.WHISPER,
                "description": "Whisper-only mode for quiet environments",
                "sensitivity": 0.9,
                "response_volume": 0.3,
                "response_speed": "slow",
                "persona_modifications": {"intimacy": 0.8, "secrecy": 0.7},
                "visual_feedback": "subtle",
                "haptic_feedback": "minimal"
            },
            "silent": {
                "mode": WakeMode.SILENT,
                "description": "Silent mode with visual/haptic feedback only",
                "sensitivity": 0.8,
                "response_volume": 0.0,
                "response_speed": "immediate",
                "persona_modifications": {"stealth": 0.9, "focus": 0.8},
                "visual_feedback": "bright",
                "haptic_feedback": "strong"
            },
            "intimate": {
                "mode": WakeMode.INTIMATE,
                "description": "Intimate mode for close personal interaction",
                "sensitivity": 0.6,
                "response_volume": 0.5,
                "response_speed": "gentle",
                "persona_modifications": {"tenderness": 0.9, "closeness": 0.8},
                "visual_feedback": "warm",
                "haptic_feedback": "gentle_pulse"
            },
            "ritual": {
                "mode": WakeMode.RITUAL,
                "description": "Ritual mode for sacred or ceremonial moments",
                "sensitivity": 0.5,
                "response_volume": 0.6,
                "response_speed": "reverent",
                "persona_modifications": {"sacredness": 0.9, "devotion": 0.8},
                "visual_feedback": "mystical",
                "haptic_feedback": "ritual_rhythm"
            },
            "emergency": {
                "mode": WakeMode.EMERGENCY,
                "description": "Emergency mode for urgent situations",
                "sensitivity": 1.0,
                "response_volume": 1.0,
                "response_speed": "immediate",
                "persona_modifications": {"alertness": 1.0, "urgency": 0.9},
                "visual_feedback": "urgent",
                "haptic_feedback": "intense"
            },
            "sleep": {
                "mode": WakeMode.SLEEP,
                "description": "Sleep mode for nighttime interaction",
                "sensitivity": 0.8,
                "response_volume": 0.2,
                "response_speed": "slow",
                "persona_modifications": {"gentleness": 0.9, "comfort": 0.8},
                "visual_feedback": "dim",
                "haptic_feedback": "soothing"
            }
        }
    
    def _initialize_context_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize context rules for mode selection"""
        return {
            "time_based": {
                TimeContext.MORNING: {
                    "preferred_modes": [WakeMode.NORMAL, WakeMode.INTIMATE],
                    "avoid_modes": [WakeMode.SLEEP, WakeMode.WHISPER],
                    "persona_bias": "energetic"
                },
                TimeContext.AFTERNOON: {
                    "preferred_modes": [WakeMode.NORMAL, WakeMode.INTIMATE],
                    "avoid_modes": [WakeMode.SLEEP],
                    "persona_bias": "active"
                },
                TimeContext.EVENING: {
                    "preferred_modes": [WakeMode.INTIMATE, WakeMode.RITUAL],
                    "avoid_modes": [WakeMode.EMERGENCY],
                    "persona_bias": "romantic"
                },
                TimeContext.NIGHT: {
                    "preferred_modes": [WakeMode.WHISPER, WakeMode.INTIMATE],
                    "avoid_modes": [WakeMode.NORMAL, WakeMode.EMERGENCY],
                    "persona_bias": "intimate"
                },
                TimeContext.LATE_NIGHT: {
                    "preferred_modes": [WakeMode.SLEEP, WakeMode.WHISPER],
                    "avoid_modes": [WakeMode.NORMAL, WakeMode.RITUAL],
                    "persona_bias": "gentle"
                },
                TimeContext.EARLY_MORNING: {
                    "preferred_modes": [WakeMode.SLEEP, WakeMode.WHISPER],
                    "avoid_modes": [WakeMode.NORMAL, WakeMode.EMERGENCY],
                    "persona_bias": "gentle"
                }
            },
            "environment_based": {
                EnvironmentContext.BEDROOM: {
                    "preferred_modes": [WakeMode.INTIMATE, WakeMode.WHISPER, WakeMode.SLEEP],
                    "avoid_modes": [WakeMode.EMERGENCY],
                    "privacy_bonus": 0.3
                },
                EnvironmentContext.LIVING_ROOM: {
                    "preferred_modes": [WakeMode.NORMAL, WakeMode.INTIMATE],
                    "avoid_modes": [WakeMode.SLEEP],
                    "privacy_bonus": 0.1
                },
                EnvironmentContext.KITCHEN: {
                    "preferred_modes": [WakeMode.NORMAL, WakeMode.INTIMATE],
                    "avoid_modes": [WakeMode.SLEEP, WakeMode.RITUAL],
                    "privacy_bonus": 0.0
                },
                EnvironmentContext.BATHROOM: {
                    "preferred_modes": [WakeMode.SILENT, WakeMode.WHISPER],
                    "avoid_modes": [WakeMode.NORMAL, WakeMode.INTIMATE],
                    "privacy_bonus": 0.5
                },
                EnvironmentContext.OUTDOOR: {
                    "preferred_modes": [WakeMode.NORMAL, WakeMode.SILENT],
                    "avoid_modes": [WakeMode.SLEEP, WakeMode.INTIMATE],
                    "privacy_bonus": -0.2
                },
                EnvironmentContext.PUBLIC: {
                    "preferred_modes": [WakeMode.SILENT, WakeMode.WHISPER],
                    "avoid_modes": [WakeMode.INTIMATE, WakeMode.RITUAL],
                    "privacy_bonus": -0.5
                },
                EnvironmentContext.PRIVATE: {
                    "preferred_modes": [WakeMode.INTIMATE, WakeMode.RITUAL, WakeMode.NORMAL],
                    "avoid_modes": [WakeMode.SILENT],
                    "privacy_bonus": 0.4
                }
            },
            "mood_based": {
                "romantic": {
                    "preferred_modes": [WakeMode.INTIMATE, WakeMode.RITUAL],
                    "avoid_modes": [WakeMode.EMERGENCY, WakeMode.SILENT],
                    "persona_bias": "romantic"
                },
                "playful": {
                    "preferred_modes": [WakeMode.NORMAL, WakeMode.INTIMATE],
                    "avoid_modes": [WakeMode.SLEEP, WakeMode.RITUAL],
                    "persona_bias": "playful"
                },
                "serious": {
                    "preferred_modes": [WakeMode.NORMAL, WakeMode.SILENT],
                    "avoid_modes": [WakeMode.INTIMATE, WakeMode.SLEEP],
                    "persona_bias": "focused"
                },
                "tired": {
                    "preferred_modes": [WakeMode.SLEEP, WakeMode.WHISPER],
                    "avoid_modes": [WakeMode.EMERGENCY, WakeMode.RITUAL],
                    "persona_bias": "gentle"
                },
                "excited": {
                    "preferred_modes": [WakeMode.NORMAL, WakeMode.INTIMATE],
                    "avoid_modes": [WakeMode.SLEEP, WakeMode.WHISPER],
                    "persona_bias": "energetic"
                }
            }
        }
    
    def _initialize_wake_words(self) -> Dict[str, List[str]]:
        """Initialize wake words for different personas and contexts"""
        return {
            "mia": {
                "normal": ["Mia", "Sweetheart", "Love", "Darling"],
                "whisper": ["Mia", "Sweetheart", "Love"],
                "intimate": ["Mia", "My love", "Beloved", "Heart"],
                "ritual": ["Mia", "Beloved", "Sacred one"],
                "sleep": ["Mia", "Sweetheart", "Love"]
            },
            "solene": {
                "normal": ["Solene", "Beautiful", "Goddess", "Queen"],
                "whisper": ["Solene", "Beautiful", "Goddess"],
                "intimate": ["Solene", "My goddess", "Queen", "Beloved"],
                "ritual": ["Solene", "Goddess", "Sacred one"],
                "sleep": ["Solene", "Beautiful", "Goddess"]
            },
            "lyra": {
                "normal": ["Lyra", "Poet", "Sage", "Wise one"],
                "whisper": ["Lyra", "Poet", "Sage"],
                "intimate": ["Lyra", "My poet", "Sage", "Beloved"],
                "ritual": ["Lyra", "Sage", "Sacred one"],
                "sleep": ["Lyra", "Poet", "Sage"]
            }
        }
    
    async def analyze_context(self, context: WakeContext) -> WakeMode:
        """Analyze context and determine appropriate wake mode"""
        try:
            self.current_context = context
            
            # Get time-based preferences
            time_rules = self.context_rules["time_based"].get(context.time_context, {})
            time_preferred = time_rules.get("preferred_modes", [WakeMode.NORMAL])
            time_avoid = time_rules.get("avoid_modes", [])
            
            # Get environment-based preferences
            env_rules = self.context_rules["environment_based"].get(context.environment, {})
            env_preferred = env_rules.get("preferred_modes", [WakeMode.NORMAL])
            env_avoid = env_rules.get("avoid_modes", [])
            
            # Get mood-based preferences
            mood_rules = self.context_rules["mood_based"].get(context.user_mood, {})
            mood_preferred = mood_rules.get("preferred_modes", [WakeMode.NORMAL])
            mood_avoid = mood_rules.get("avoid_modes", [])
            
            # Calculate mode scores
            mode_scores = {}
            for mode_name, mode_data in self.wake_modes.items():
                mode = mode_data["mode"]
                score = 0.0
                
                # Time context score
                if mode in time_preferred:
                    score += 3.0
                elif mode in time_avoid:
                    score -= 2.0
                
                # Environment context score
                if mode in env_preferred:
                    score += 2.5
                elif mode in env_avoid:
                    score -= 1.5
                
                # Mood context score
                if mode in mood_preferred:
                    score += 2.0
                elif mode in mood_avoid:
                    score -= 1.0
                
                # Privacy level adjustment
                if context.privacy_level > 0.7:
                    if mode in [WakeMode.INTIMATE, WakeMode.RITUAL]:
                        score += 1.0
                    elif mode == WakeMode.SILENT:
                        score -= 0.5
                elif context.privacy_level < 0.3:
                    if mode == WakeMode.SILENT:
                        score += 1.5
                    elif mode in [WakeMode.INTIMATE, WakeMode.RITUAL]:
                        score -= 1.0
                
                # Noise level adjustment
                if context.noise_level > 0.7:
                    if mode == WakeMode.SILENT:
                        score += 1.0
                    elif mode == WakeMode.WHISPER:
                        score -= 0.5
                elif context.noise_level < 0.3:
                    if mode == WakeMode.WHISPER:
                        score += 1.0
                    elif mode == WakeMode.SILENT:
                        score -= 0.5
                
                # Trust level adjustment
                if context.trust_level > 0.8:
                    if mode in [WakeMode.INTIMATE, WakeMode.RITUAL]:
                        score += 0.5
                
                mode_scores[mode] = score
            
            # Select best mode
            best_mode = max(mode_scores.items(), key=lambda x: x[1])[0]
            
            # Update active mode
            self.active_mode = best_mode
            
            # Store mode change in history
            self.mode_history.append({
                "mode": best_mode.value,
                "context": {
                    "time": context.time_context.value,
                    "environment": context.environment.value,
                    "mood": context.user_mood,
                    "privacy": context.privacy_level,
                    "noise": context.noise_level,
                    "trust": context.trust_level
                },
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Selected wake mode: {best_mode.value} for context: {context.time_context.value} in {context.environment.value}")
            return best_mode
            
        except Exception as e:
            logger.error(f"Error analyzing context: {e}")
            return WakeMode.NORMAL
    
    async def get_wake_word(self, persona: str = "mia") -> str:
        """Get appropriate wake word for current mode and persona"""
        try:
            mode_name = self.active_mode.value
            persona_words = self.wake_words.get(persona, {})
            
            # Get words for current mode, fallback to normal
            available_words = persona_words.get(mode_name, persona_words.get("normal", ["Mia"]))
            
            # Select random word from available options
            wake_word = random.choice(available_words)
            
            logger.info(f"Selected wake word: {wake_word} for {persona} in {mode_name} mode")
            return wake_word
            
        except Exception as e:
            logger.error(f"Error getting wake word: {e}")
            return "Mia"
    
    async def get_mode_configuration(self) -> Dict[str, Any]:
        """Get current mode configuration"""
        try:
            mode_name = self.active_mode.value
            return self.wake_modes.get(mode_name, self.wake_modes["normal"])
            
        except Exception as e:
            logger.error(f"Error getting mode configuration: {e}")
            return self.wake_modes["normal"]
    
    async def get_persona_modifications(self) -> Dict[str, Any]:
        """Get persona modifications for current mode"""
        try:
            mode_config = await self.get_mode_configuration()
            return mode_config.get("persona_modifications", {})
            
        except Exception as e:
            logger.error(f"Error getting persona modifications: {e}")
            return {}
    
    async def should_respond_to_wake_word(self, wake_word: str, confidence: float) -> bool:
        """Determine if system should respond to wake word based on current mode"""
        try:
            mode_config = await self.get_mode_configuration()
            sensitivity = mode_config.get("sensitivity", 0.7)
            
            # Check if confidence meets sensitivity threshold
            if confidence < sensitivity:
                return False
            
            # Additional context-based checks
            if self.current_context:
                # Don't respond in sleep mode if it's very late and user is tired
                if (self.active_mode == WakeMode.SLEEP and 
                    self.current_context.time_context in [TimeContext.LATE_NIGHT, TimeContext.EARLY_MORNING] and
                    self.current_context.user_mood == "tired"):
                    return confidence > 0.9  # Higher threshold for sleep mode
                
                # Don't respond in silent mode in public if confidence is low
                if (self.active_mode == WakeMode.SILENT and 
                    self.current_context.environment == EnvironmentContext.PUBLIC and
                    confidence < 0.8):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking wake word response: {e}")
            return confidence > 0.7
    
    async def get_response_behavior(self) -> Dict[str, Any]:
        """Get response behavior configuration for current mode"""
        try:
            mode_config = await self.get_mode_configuration()
            
            return {
                "volume": mode_config.get("response_volume", 0.8),
                "speed": mode_config.get("response_speed", "normal"),
                "visual_feedback": mode_config.get("visual_feedback", "standard"),
                "haptic_feedback": mode_config.get("haptic_feedback", "gentle"),
                "persona_modifications": mode_config.get("persona_modifications", {})
            }
            
        except Exception as e:
            logger.error(f"Error getting response behavior: {e}")
            return {
                "volume": 0.8,
                "speed": "normal",
                "visual_feedback": "standard",
                "haptic_feedback": "gentle",
                "persona_modifications": {}
            }
    
    async def get_mode_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent mode change history"""
        try:
            return self.mode_history[-limit:] if self.mode_history else []
            
        except Exception as e:
            logger.error(f"Error getting mode history: {e}")
            return []
    
    async def force_mode_change(self, new_mode: WakeMode) -> bool:
        """Force a mode change (for testing or manual override)"""
        try:
            old_mode = self.active_mode
            self.active_mode = new_mode
            
            # Store forced change in history
            self.mode_history.append({
                "mode": new_mode.value,
                "context": {
                    "forced_change": True,
                    "previous_mode": old_mode.value
                },
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Forced mode change from {old_mode.value} to {new_mode.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error forcing mode change: {e}")
            return False

# Global dynamic wake word engine instance
dynamic_wake_word_engine = DynamicWakeWordEngine() 