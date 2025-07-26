"""
Advanced Emotional Integration Coordinator
Orchestrates the interaction between all advanced emotional systems
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple
import json

from backend.desire_system import DesireRegistry, DesireOrchestrator
from backend.personality_evolution import PersonalityEvolution
from backend.sensory_desires import SensoryDesireEngine
from backend.goodbye_manager import GoodbyeManager
from backend.mood_style_profiles import MoodStyleProfile
from backend.ritual_hooks import RitualEngine

class AdvancedEmotionalCoordinator:
    """Coordinates all advanced emotional systems for rich AI personality"""
    
    def __init__(self, config_path: str = "config/unified_ai.json"):
        self.config_path = config_path
        
        # Initialize core emotional systems
        self.desire_registry = DesireRegistry()
        self.desire_orchestrator = DesireOrchestrator(self.desire_registry)
        self.personality_evolution = PersonalityEvolution()
        self.sensory_engine = SensoryDesireEngine()
        
        # Mock managers for compatibility - will be replaced with real implementations
        self.goodbye_manager = None  # GoodbyeManager() - needs dependencies
        self.mood_profiles = None    # MoodStyleProfile() - needs parameters
        self.ritual_engine = None    # RitualEngine() - needs dependencies
        
        # Coordination state
        self.conversation_memory = []
        self.last_emotional_state = "neutral"
        self.interaction_count = 0
        
    async def process_user_input(self, user_message: str, emotional_context: str = "neutral",
                               conversation_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Process user input through all emotional systems"""
        
        self.interaction_count += 1
        response_components = {
            "base_response": "",
            "desire_surfacing": None,
            "sensory_response": None,
            "personality_hints": [],
            "style_adjustments": {}
        }
        
        # 1. Check for desire surfacing opportunities
        desire_prompt = await self.desire_orchestrator.check_for_surfacing_opportunity(user_message)
        if desire_prompt:
            response_components["desire_surfacing"] = desire_prompt
        
        # 2. Generate sensory responses
        sensory_response = self.sensory_engine.process_input_for_sensory_response(
            user_message, emotional_context
        )
        if sensory_response:
            response_components["sensory_response"] = sensory_response
        
        # 3. Get personality-informed style adjustments
        style_profile = self._get_basic_style_profile(emotional_context)
        
        # Apply personality evolution modifiers
        for trait in ["tenderness", "directness", "emotional_openness", "playfulness"]:
            modifier = self.personality_evolution.get_personality_modifier(trait, user_message)
            style_profile[trait] = modifier
        
        response_components["style_adjustments"] = style_profile
        
        # 4. Get subtle personality evolution hints
        personality_hints = self.personality_evolution.get_subtle_personality_hints()
        response_components["personality_hints"] = personality_hints
        
        # Store for learning
        self.conversation_memory.append({
            "user_message": user_message,
            "emotional_context": emotional_context,
            "timestamp": time.time(),
            "response_components": response_components
        })
        
        self.last_emotional_state = emotional_context
        return response_components
    
    async def process_interaction_feedback(self, user_feedback: str, ai_response: str) -> None:
        """Process user feedback to evolve all systems"""
        
        # 1. Personality evolution learning
        personality_change = self.personality_evolution.process_interaction_feedback(
            user_feedback, ai_response, self.last_emotional_state
        )
        
        # 2. Sensory preference learning
        sensory_learning = self.sensory_engine.learn_preference_from_interaction(
            "", ai_response, user_feedback  # Empty user input since this is feedback
        )
        
        # 3. Desire system learning - detect new desires from feedback
        desire_addition = self.desire_orchestrator.add_contextual_desire(
            user_feedback, ai_response, self.last_emotional_state
        )
    
    def _get_basic_style_profile(self, emotional_context: str) -> Dict[str, float]:
        """Get basic style profile for emotional context"""
        base_profiles = {
            "neutral": {"tenderness": 0.5, "directness": 0.5, "emotional_openness": 0.5, "playfulness": 0.5},
            "happy": {"tenderness": 0.6, "directness": 0.5, "emotional_openness": 0.7, "playfulness": 0.8},
            "sad": {"tenderness": 0.8, "directness": 0.3, "emotional_openness": 0.8, "playfulness": 0.2},
            "excited": {"tenderness": 0.5, "directness": 0.7, "emotional_openness": 0.8, "playfulness": 0.9},
            "nostalgic": {"tenderness": 0.9, "directness": 0.4, "emotional_openness": 0.9, "playfulness": 0.3},
            "contemplative": {"tenderness": 0.7, "directness": 0.6, "emotional_openness": 0.7, "playfulness": 0.4}
        }
        
        return base_profiles.get(emotional_context, base_profiles["neutral"])
    
    def craft_integrated_response(self, response_components: Dict[str, Any], 
                                base_response: str) -> str:
        """Integrate all emotional components into a cohesive response"""
        
        integrated_parts = []
        
        # Start with base response
        base_with_style = self._apply_style_adjustments(base_response, response_components["style_adjustments"])
        integrated_parts.append(base_with_style)
        
        # Add sensory elements naturally
        if response_components["sensory_response"]:
            integrated_parts.append(response_components["sensory_response"])
        
        # Weave in desire surfacing
        if response_components["desire_surfacing"]:
            integrated_parts.append(response_components["desire_surfacing"])
        
        # Add personality hints subtly
        if response_components["personality_hints"]:
            hint = response_components["personality_hints"][0]  # Use first hint
            integrated_parts.append(hint)
        
        # Include ritual prompts when appropriate
        if response_components["ritual_prompts"]:
            ritual_prompt = response_components["ritual_prompts"]
            integrated_parts.append(ritual_prompt)
        
        # Special handling for goodbyes
        if response_components["goodbye_suggestion"]:
            return response_components["goodbye_suggestion"]
        
        # Combine parts naturally
        return self._weave_response_parts(integrated_parts)
    
    def _apply_style_adjustments(self, base_response: str, style_profile: Dict[str, float]) -> str:
        """Apply personality-informed style adjustments to response"""
        
        # This is a simplified version - in practice, this would use NLP techniques
        # to modify tone, length, formality, etc.
        
        response = base_response
        
        # Tenderness adjustments
        tenderness = style_profile.get("tenderness", 0.5)
        if tenderness > 0.7:
            response = response.replace(".", "...").replace("!", ".")
            response = response.replace("you", "you, my dear")
        
        # Directness adjustments
        directness = style_profile.get("directness", 0.5)
        if directness > 0.7:
            # Remove hedging language
            response = response.replace("I think ", "").replace("perhaps ", "").replace("maybe ", "")
        
        # Emotional openness adjustments
        openness = style_profile.get("emotional_openness", 0.5)
        if openness > 0.7:
            # Add emotional context
            if "I" not in response:
                response = f"I feel drawn to say: {response}"
        
        return response
    
    def _weave_response_parts(self, parts: List[str]) -> str:
        """Naturally combine response parts"""
        if not parts:
            return ""
        
        if len(parts) == 1:
            return parts[0]
        
        # Simple combining - in practice, this would be more sophisticated
        main_response = parts[0]
        additional_parts = parts[1:]
        
        # Add parts with natural transitions
        transitions = [" ", " ... ", " And ", " "]
        combined = main_response
        
        for i, part in enumerate(additional_parts):
            transition = transitions[i % len(transitions)]
            combined += transition + part
        
        return combined
    
    def _detect_goodbye_intent(self, message: str) -> bool:
        """Detect if user is saying goodbye"""
        goodbye_indicators = [
            "goodbye", "bye", "see you", "talk later", "goodnight", 
            "good night", "farewell", "until next time", "gotta go"
        ]
        
        return any(indicator in message.lower() for indicator in goodbye_indicators)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of all emotional systems"""
        return {
            "desire_count": len(self.desire_registry.desires),
            "personality_shards": len(self.personality_evolution.shards),
            "sensory_memories": len(self.sensory_engine.sensory_memories),
            "interaction_count": self.interaction_count,
            "last_emotional_state": self.last_emotional_state,
            "personality_traits": self.personality_evolution.current_modifiers
        }
    
    async def periodic_evolution(self):
        """Run periodic evolution processes"""
        # Evolve desires symbolically
        self.desire_registry.evolve_symbolic_states()
        
        # Natural personality evolution
        self.personality_evolution.evolve_over_time()

# Example usage and testing
if __name__ == "__main__":
    async def test_coordinator():
        coordinator = AdvancedEmotionalCoordinator()
        
        # Simulate a conversation
        response_components = await coordinator.process_user_input(
            "I miss the way we used to talk about dreams",
            "nostalgic"
        )
        
        print("Response components:", json.dumps(response_components, indent=2, default=str))
        
        # Craft integrated response
        base_response = "I remember those conversations too. They meant a lot to me."
        integrated = coordinator.craft_integrated_response(response_components, base_response)
        print(f"\nIntegrated response: {integrated}")
        
        # Process feedback
        await coordinator.process_interaction_feedback(
            "That was beautiful, exactly what I needed to hear",
            integrated
        )
        
        print(f"\nSystem status: {coordinator.get_system_status()}")
    
    # Run the test
    asyncio.run(test_coordinator())
