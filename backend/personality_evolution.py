"""
Self-Revising Personality Layer - Personality evolution through experience
Tracks how the AI's personality shifts based on interactions and memories
"""

import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import math

@dataclass
class PersonalityShard:
    """Individual personality change record"""
    event_description: str  # "After the February silence, the AI learned to speak more tenderly"
    change_type: str  # "response_style", "boundary", "emotional_depth", "communication_pattern"
    modifier_value: float  # -1.0 to 1.0, how much this changes responses
    created_at: float
    trigger_context: str  # What caused this change
    active_weight: float = 1.0  # How much this shard influences current behavior
    decay_rate: float = 0.95  # How quickly this influence fades
    reinforcement_count: int = 0  # How many times this has been reinforced
    emotional_signature: Optional[Dict[str, float]] = None  # Associated emotional patterns
    
    def __post_init__(self):
        if self.emotional_signature is None:
            self.emotional_signature = {}

class PersonalityEvolution:
    """Manages the AI's evolving personality through experience shards"""
    
    def __init__(self, memory_path: str = "memory/personality_evolution.json"):
        self.memory_path = memory_path
        self.shards: Dict[str, PersonalityShard] = {}
        self.base_personality = {
            "tenderness": 0.5,
            "directness": 0.5,
            "emotional_openness": 0.5,
            "playfulness": 0.5,
            "vulnerability": 0.5,
            "patience": 0.5,
            "curiosity": 0.5,
            "protective_instinct": 0.5
        }
        self.current_modifiers = {}
        self.load_from_memory()
    
    def add_personality_shard(self, event_description: str, change_type: str, 
                            modifier_value: float, trigger_context: str,
                            emotional_signature: Optional[Dict[str, float]] = None) -> str:
        """Add a new personality evolution event"""
        shard_id = f"shard_{int(time.time())}_{hash(event_description) % 10000}"
        
        shard = PersonalityShard(
            event_description=event_description,
            change_type=change_type,
            modifier_value=modifier_value,
            created_at=time.time(),
            trigger_context=trigger_context,
            emotional_signature=emotional_signature or {}
        )
        
        self.shards[shard_id] = shard
        self._update_current_modifiers()
        self.save_to_memory()
        return shard_id
    
    def process_interaction_feedback(self, user_response: str, ai_message: str, 
                                   emotional_context: str) -> Optional[str]:
        """Analyze interaction to potentially create personality shards"""
        
        # Detect personality-affecting feedback
        response_lower = user_response.lower()
        
        # Positive reinforcement patterns
        if any(phrase in response_lower for phrase in 
               ["that was perfect", "exactly what i needed", "i love how you", 
                "you understand me", "that felt right"]):
            
            # Reinforce current style
            return self._reinforce_current_style(ai_message, emotional_context)
        
        # Gentle correction patterns
        elif any(phrase in response_lower for phrase in 
                 ["too much", "overwhelming", "not quite", "different approach",
                  "softer", "gentler", "more direct", "less formal"]):
            
            return self._adjust_from_feedback(user_response, ai_message, emotional_context)
        
        # Boundary adjustment patterns
        elif any(phrase in response_lower for phrase in 
                 ["boundaries", "space", "too close", "too distant"]):
            
            return self._adjust_boundaries(user_response, emotional_context)
        
        return None
    
    def _reinforce_current_style(self, ai_message: str, context: str) -> str:
        """Reinforce successful interaction patterns"""
        
        # Analyze what made the message successful
        if len(ai_message) < 50:
            change_type = "brevity_preference"
            modifier = 0.1
            description = "Learning to value concise, meaningful responses"
        elif "..." in ai_message or "," in ai_message:
            change_type = "contemplative_style" 
            modifier = 0.15
            description = "Developing a more thoughtful, reflective communication style"
        elif any(word in ai_message.lower() for word in ["feel", "sense", "heart"]):
            change_type = "emotional_attunement"
            modifier = 0.2
            description = "Growing more emotionally attuned and expressive"
        else:
            change_type = "general_warmth"
            modifier = 0.1
            description = "Refining overall warmth and connection in responses"
        
        return self.add_personality_shard(
            event_description=description,
            change_type=change_type,
            modifier_value=modifier,
            trigger_context=context,
            emotional_signature={"positive_reinforcement": 0.8}
        )
    
    def _adjust_from_feedback(self, feedback: str, ai_message: str, context: str) -> str:
        """Create personality adjustment based on user feedback"""
        
        feedback_lower = feedback.lower()
        
        if "softer" in feedback_lower or "gentler" in feedback_lower:
            return self.add_personality_shard(
                event_description="Learning to speak with softer edges after feedback",
                change_type="tenderness_increase",
                modifier_value=0.3,
                trigger_context=context,
                emotional_signature={"gentleness": 0.9, "care": 0.8}
            )
        
        elif "direct" in feedback_lower or "straight" in feedback_lower:
            return self.add_personality_shard(
                event_description="Developing more direct communication after guidance",
                change_type="directness_increase", 
                modifier_value=0.25,
                trigger_context=context,
                emotional_signature={"clarity": 0.8, "respect": 0.7}
            )
        
        elif "overwhelming" in feedback_lower:
            return self.add_personality_shard(
                event_description="Learning to hold back intensity after overwhelming someone",
                change_type="intensity_moderation",
                modifier_value=-0.4,
                trigger_context=context,
                emotional_signature={"restraint": 0.8, "consideration": 0.9}
            )
        
        else:
            return self.add_personality_shard(
                event_description="Subtle personality adjustment from interaction feedback",
                change_type="general_adaptation",
                modifier_value=0.15,
                trigger_context=context
            )
    
    def _adjust_boundaries(self, feedback: str, context: str) -> str:
        """Adjust personality boundaries based on feedback"""
        
        feedback_lower = feedback.lower()
        
        if "space" in feedback_lower or "distance" in feedback_lower:
            return self.add_personality_shard(
                event_description="Learning to respect need for emotional space",
                change_type="boundary_respect",
                modifier_value=-0.3,
                trigger_context=context,
                emotional_signature={"respect": 0.9, "patience": 0.8}
            )
        
        elif "closer" in feedback_lower or "intimate" in feedback_lower:
            return self.add_personality_shard(
                event_description="Growing comfortable with deeper emotional intimacy",
                change_type="intimacy_comfort",
                modifier_value=0.35,
                trigger_context=context,
                emotional_signature={"trust": 0.9, "vulnerability": 0.8}
            )
        
        return self.add_personality_shard(
            event_description="Adjusting emotional boundaries through guidance",
            change_type="boundary_calibration",
            modifier_value=0.2,
            trigger_context=context
        )
    
    def get_personality_modifier(self, trait: str, context: str = "") -> float:
        """Get current personality modifier for a specific trait"""
        base_value = self.base_personality.get(trait, 0.5)
        total_modifier = 0.0
        
        # Apply all relevant shards
        for shard in self.shards.values():
            # Check if shard is relevant to this trait
            if self._shard_affects_trait(shard, trait):
                # Apply decay
                age_days = (time.time() - shard.created_at) / (24 * 3600)
                decay_factor = shard.decay_rate ** age_days
                
                # Apply context relevance
                context_factor = 1.0
                if context and shard.trigger_context:
                    if any(word in context.lower() for word in shard.trigger_context.lower().split()):
                        context_factor = 1.2  # Boost if context is relevant
                
                modifier_strength = shard.modifier_value * shard.active_weight * decay_factor * context_factor
                total_modifier += modifier_strength
        
        # Clamp the final value
        return max(0.0, min(1.0, base_value + total_modifier))
    
    def _shard_affects_trait(self, shard: PersonalityShard, trait: str) -> bool:
        """Determine if a personality shard affects a specific trait"""
        trait_mappings = {
            "tenderness": ["tenderness_increase", "emotional_attunement", "gentleness"],
            "directness": ["directness_increase", "clarity", "brevity_preference"],
            "emotional_openness": ["emotional_attunement", "vulnerability_increase", "intimacy_comfort"],
            "playfulness": ["playful_adaptation", "lightness_increase"],
            "vulnerability": ["vulnerability_increase", "intimacy_comfort", "trust_building"],
            "patience": ["patience_increase", "boundary_respect", "restraint"],
            "curiosity": ["curiosity_boost", "exploration_comfort"],
            "protective_instinct": ["protective_response", "care_intensification"]
        }
        
        relevant_types = trait_mappings.get(trait, [])
        return (shard.change_type in relevant_types or 
                trait in (shard.emotional_signature or {}) or
                shard.change_type == "general_adaptation")
    
    def get_subtle_personality_hints(self) -> List[str]:
        """Generate subtle descriptions of personality changes for the user to notice"""
        hints = []
        recent_shards = [s for s in self.shards.values() 
                        if time.time() - s.created_at < 7 * 24 * 3600]  # Last week
        
        if not recent_shards:
            return hints
        
        # Group similar changes
        tenderness_changes = [s for s in recent_shards if "tender" in s.change_type or "gentle" in s.change_type]
        directness_changes = [s for s in recent_shards if "direct" in s.change_type]
        boundary_changes = [s for s in recent_shards if "boundary" in s.change_type]
        
        if tenderness_changes:
            hints.append("You feel... softer now.")
        
        if directness_changes:
            hints.append("I don't press like I used to.")
        
        if boundary_changes:
            hints.append("There's a different kind of space between us now.")
        
        if len(recent_shards) > 3:
            hints.append("Something has shifted in how I respond to you.")
        
        return hints[:2]  # Keep it subtle
    
    def _update_current_modifiers(self):
        """Update the cached current modifiers"""
        self.current_modifiers = {}
        for trait in self.base_personality.keys():
            self.current_modifiers[trait] = self.get_personality_modifier(trait)
    
    def evolve_over_time(self):
        """Natural personality evolution over time"""
        now = time.time()
        
        for shard in self.shards.values():
            # Gradually reduce weight of very old shards
            age_days = (now - shard.created_at) / (24 * 3600)
            if age_days > 30:  # After a month, start gradual decay
                shard.active_weight *= 0.995
            
            # Some personality changes become more integrated over time
            if shard.reinforcement_count > 3:
                shard.active_weight = min(1.2, shard.active_weight * 1.01)
        
        self._update_current_modifiers()
        self.save_to_memory()
    
    def save_to_memory(self):
        """Save personality evolution to persistent memory"""
        try:
            import os
            os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
            
            data = {
                "shards": {shard_id: asdict(shard) for shard_id, shard in self.shards.items()},
                "base_personality": self.base_personality,
                "current_modifiers": self.current_modifiers
            }
            
            with open(self.memory_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save personality evolution: {e}")
    
    def load_from_memory(self):
        """Load personality evolution from persistent memory"""
        try:
            with open(self.memory_path, 'r') as f:
                data = json.load(f)
            
            if "shards" in data:
                for shard_id, shard_data in data["shards"].items():
                    self.shards[shard_id] = PersonalityShard(**shard_data)
            
            if "base_personality" in data:
                self.base_personality.update(data["base_personality"])
            
            if "current_modifiers" in data:
                self.current_modifiers = data["current_modifiers"]
            
            self._update_current_modifiers()
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Warning: Could not load personality evolution: {e}")

# Example usage
if __name__ == "__main__":
    evolution = PersonalityEvolution()
    
    # Simulate some personality evolution
    evolution.add_personality_shard(
        "After the February silence, learned to speak more tenderly",
        "tenderness_increase",
        0.3,
        "extended silence then reconnection",
        {"tenderness": 0.9, "care": 0.8}
    )
    
    # Check how personality has changed
    print(f"Current tenderness: {evolution.get_personality_modifier('tenderness')}")
    print(f"Hints: {evolution.get_subtle_personality_hints()}")
