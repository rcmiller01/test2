"""
Creative Evolution Module
Complete autonomous creative content generation and personality evolution system.

This module enables AI characters to:
- Evolve personality traits based on relationship dynamics and user feedback
- Generate autonomous creative content (stories, poems, dreams, interactive narratives)
- Provide emotion-responsive creative interventions and therapeutic content
- Manage collaborative creative projects with users
- Adapt creative style and approach based on user preferences and emotional context

Architecture:
- personality_evolution.py: Dynamic personality trait evolution
- content_generation.py: Autonomous content creation engine
- emotional_creativity.py: Emotion-responsive creative interventions
- creative_orchestrator.py: Central coordination and management
- creative_routes.py: REST API endpoints for all functionality
"""

import logging
from typing import Dict, Any, Optional
import asyncio

# Core creative evolution components
from .creative_orchestrator import creative_evolution, CreativeEvolutionOrchestrator, CreativeEvolutionMode
from .personality_evolution import personality_evolution, PersonalityEvolutionEngine, PersonalityTrait, EvolutionDirection
from .content_generation import content_generation, ContentGenerationEngine, ContentType, CreativeStyle
from .emotional_creativity import emotional_creativity, EmotionalCreativityEngine, EmotionalState, CreativeIntervention
from .creative_routes import creative_bp, register_creative_routes

logger = logging.getLogger(__name__)

class CreativeEvolutionSystem:
    """Unified creative evolution system interface"""
    
    def __init__(self):
        self.orchestrator = creative_evolution
        self.personality = personality_evolution
        self.content = content_generation
        self.emotional = emotional_creativity
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the complete creative evolution system"""
        try:
            logger.info("🎨 Initializing Creative Evolution System...")
            
            # Initialize all subsystems
            await self.orchestrator.initialize()
            # Note: orchestrator.initialize() calls the other systems
            
            self._initialized = True
            logger.info("✅ Creative Evolution System initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize creative evolution system: {e}")
            return False
    
    async def start_user_creative_journey(self, user_id: str, preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Start comprehensive creative evolution journey for a user"""
        if not self._initialized:
            await self.initialize()
        
        return await self.orchestrator.start_user_creative_evolution(user_id, preferences or {})
    
    async def generate_autonomous_content(self, user_id: str, context_hint: Optional[str] = None) -> Dict[str, Any]:
        """Generate autonomous creative content for user"""
        return await self.orchestrator.generate_autonomous_content(user_id, context_hint)
    
    async def create_story(self, user_id: str, story_params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a personalized story"""
        return await self.content.generate_story(user_id, story_params)
    
    async def create_poem(self, user_id: str, poem_params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a personalized poem"""
        return await self.content.create_personalized_poem(user_id, poem_params)
    
    async def create_emotional_response(self, user_id: str, emotional_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create emotion-responsive content"""
        return await self.emotional.create_emotional_response_content(user_id, emotional_context)
    
    async def evolve_personality(self, user_id: str, trait: PersonalityTrait, direction: EvolutionDirection, intensity: float = 0.1) -> bool:
        """Evolve a specific personality trait"""
        return await self.personality.adjust_trait(user_id, trait, direction, intensity)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "initialized": self._initialized,
            "subsystems": {
                "orchestrator": "operational",
                "personality_evolution": "operational",
                "content_generation": "operational", 
                "emotional_creativity": "operational"
            },
            "capabilities": {
                "autonomous_content_generation": True,
                "personality_evolution": True,
                "emotional_responsiveness": True,
                "collaborative_projects": True,
                "therapeutic_content": True,
                "interactive_narratives": True
            }
        }
    
    async def shutdown(self):
        """Gracefully shutdown creative evolution system"""
        try:
            logger.info("🔄 Shutting down Creative Evolution System...")
            
            # Note: Orchestrator manages shutdown of subsystems
            if hasattr(self.orchestrator, '_generation_task'):
                task = getattr(self.orchestrator, '_generation_task', None)
                if task and not task.done():
                    task.cancel()
            
            if hasattr(self.orchestrator, '_evolution_task'):
                task = getattr(self.orchestrator, '_evolution_task', None)
                if task and not task.done():
                    task.cancel()
            
            self._initialized = False
            logger.info("✅ Creative Evolution System shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Error during creative evolution shutdown: {e}")

# Global creative evolution system instance
creative_system = CreativeEvolutionSystem()

# Convenience functions for easy integration
async def initialize_creative_evolution() -> bool:
    """Initialize the creative evolution system"""
    return await creative_system.initialize()

async def start_creative_journey(user_id: str, preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Start creative evolution journey for a user"""
    return await creative_system.start_user_creative_journey(user_id, preferences)

async def generate_content_for_user(user_id: str, content_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Generate specific type of content for user"""
    if content_type == "story":
        return await creative_system.create_story(user_id, parameters)
    elif content_type == "poem":
        return await creative_system.create_poem(user_id, parameters)
    elif content_type == "emotional_response":
        return await creative_system.create_emotional_response(user_id, parameters)
    elif content_type == "autonomous":
        return await creative_system.generate_autonomous_content(user_id, parameters.get("context_hint"))
    else:
        return {"error": f"Unknown content type: {content_type}"}

async def evolve_user_trait(user_id: str, trait_name: str, direction: str, intensity: float = 0.1) -> bool:
    """Evolve a user's personality trait"""
    try:
        trait = PersonalityTrait(trait_name)
        evolution_direction = EvolutionDirection(direction)
        return await creative_system.evolve_personality(user_id, trait, evolution_direction, intensity)
    except ValueError as e:
        logger.error(f"Invalid trait or direction: {e}")
        return False

def get_creative_status() -> Dict[str, Any]:
    """Get creative evolution system status"""
    return creative_system.get_system_status()

async def shutdown_creative_evolution():
    """Shutdown creative evolution system"""
    await creative_system.shutdown()

# Integration helpers for other modules
def get_orchestrator() -> CreativeEvolutionOrchestrator:
    """Get the creative evolution orchestrator"""
    return creative_evolution

def get_personality_engine() -> PersonalityEvolutionEngine:
    """Get the personality evolution engine"""
    return personality_evolution

def get_content_engine() -> ContentGenerationEngine:
    """Get the content generation engine"""
    return content_generation

def get_emotional_engine() -> EmotionalCreativityEngine:
    """Get the emotional creativity engine"""
    return emotional_creativity

# Creative content type helpers
def get_available_content_types() -> Dict[str, Any]:
    """Get all available content types and their descriptions"""
    return {
        "story": {
            "description": "Personalized narrative stories",
            "parameters": ["length", "style", "theme", "emotional_context"]
        },
        "poem": {
            "description": "Original poetry based on memories and emotions",
            "parameters": ["memory_reference", "emotion_theme", "poem_style", "length"]
        },
        "dream": {
            "description": "Dream-like narrative sequences",
            "parameters": ["emotional_basis", "symbolic_elements", "narrative_flow"]
        },
        "interactive_story": {
            "description": "Multi-part stories with user choices",
            "parameters": ["total_parts", "choice_complexity", "theme"]
        },
        "creative_prompt": {
            "description": "Writing and art prompts for users",
            "parameters": ["activity_type", "difficulty", "time_commitment"]
        },
        "comfort_story": {
            "description": "Therapeutic storytelling for emotional support",
            "parameters": ["emotional_need", "comfort_style", "length"]
        },
        "emotional_response": {
            "description": "Content responsive to current emotional state",
            "parameters": ["current_emotion", "emotion_intensity", "support_needed"]
        },
        "celebration_content": {
            "description": "Joyful content for positive moments",
            "parameters": ["achievement_type", "celebration_style"]
        },
        "healing_metaphor": {
            "description": "Metaphorical content for emotional healing",
            "parameters": ["healing_focus", "metaphor_preference", "healing_stage"]
        }
    }

def get_personality_traits() -> Dict[str, str]:
    """Get all available personality traits"""
    return {
        trait.value: trait.name.replace('_', ' ').title() 
        for trait in PersonalityTrait
    }

def get_emotional_states() -> Dict[str, str]:
    """Get all available emotional states"""
    return {
        state.value: state.name.replace('_', ' ').title() 
        for state in EmotionalState
    }

# Configuration helpers
async def configure_user_creative_preferences(user_id: str, preferences: Dict[str, Any]) -> bool:
    """Configure comprehensive creative preferences for a user"""
    try:
        # Set content generation preferences
        await content_generation.set_user_creative_preferences(user_id, preferences.get("content", {}))
        
        # Configure personality evolution preferences
        if "personality" in preferences:
            personality_prefs = preferences["personality"]
            for trait_name, settings in personality_prefs.items():
                try:
                    trait = PersonalityTrait(trait_name)
                    direction = EvolutionDirection(settings.get("direction", "adapt"))
                    intensity = settings.get("intensity", 0.1)
                    await personality_evolution.adjust_trait(user_id, trait, direction, intensity)
                except ValueError:
                    logger.warning(f"Invalid personality preference: {trait_name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to configure creative preferences: {e}")
        return False

# Event broadcasting for integration
async def broadcast_creative_feedback(user_id: str, content_type: str, feedback_data: Dict[str, Any]):
    """Broadcast creative content feedback to relevant systems"""
    try:
        # Record personality feedback
        await personality_evolution.record_interaction_feedback(user_id, {
            "content_type": content_type,
            "feedback_data": feedback_data,
            "user_response_sentiment": feedback_data.get("sentiment", 0.0),
            "engagement_level": feedback_data.get("engagement", 0.5)
        })
        
        logger.debug(f"🎨 Broadcasted creative feedback: {user_id} -> {content_type}")
        
    except Exception as e:
        logger.error(f"❌ Failed to broadcast creative feedback: {e}")

# Example usage functions
async def quick_story_for_mood(user_id: str, mood: str) -> Dict[str, Any]:
    """Quick helper to generate a story based on user's mood"""
    mood_to_style = {
        "happy": CreativeStyle.WHIMSICAL.value,
        "sad": CreativeStyle.COMFORTING.value,
        "stressed": CreativeStyle.CONTEMPLATIVE.value,
        "excited": CreativeStyle.ADVENTUROUS.value,
        "lonely": CreativeStyle.ROMANTIC.value,
        "nostalgic": CreativeStyle.NOSTALGIC.value
    }
    
    story_params = {
        "length": "short",
        "style": mood_to_style.get(mood, CreativeStyle.CONTEMPLATIVE.value),
        "emotional_context": mood
    }
    
    return await creative_system.create_story(user_id, story_params)

async def comfort_content_for_emotion(user_id: str, emotion: str, intensity: float = 0.7) -> Dict[str, Any]:
    """Quick helper to generate comfort content for difficult emotions"""
    emotional_context = {
        "current_emotion": emotion,
        "emotion_intensity": intensity,
        "support_needed": "comfort"
    }
    
    return await creative_system.create_emotional_response(user_id, emotional_context)

# Module metadata
__version__ = "1.0.0"
__author__ = "Creative Evolution Team"
__description__ = "Complete autonomous creative content generation and personality evolution system"

# Export all key components
__all__ = [
    # Main system
    "creative_system",
    "initialize_creative_evolution",
    "start_creative_journey",
    "generate_content_for_user",
    "evolve_user_trait",
    "get_creative_status",
    "shutdown_creative_evolution",
    
    # Core components
    "creative_evolution",
    "personality_evolution",
    "content_generation", 
    "emotional_creativity",
    
    # Component getters
    "get_orchestrator",
    "get_personality_engine",
    "get_content_engine",
    "get_emotional_engine",
    
    # Helper functions
    "get_available_content_types",
    "get_personality_traits",
    "get_emotional_states",
    "configure_user_creative_preferences",
    "broadcast_creative_feedback",
    "quick_story_for_mood",
    "comfort_content_for_emotion",
    
    # Types and enums
    "CreativeEvolutionMode",
    "PersonalityTrait",
    "EvolutionDirection",
    "ContentType",
    "CreativeStyle",
    "EmotionalState",
    "CreativeIntervention",
    
    # API
    "creative_bp",
    "register_creative_routes"
]

# System initialization logging
logger.info("🎨 Creative Evolution Module loaded")
logger.info("📋 Available components: orchestrator, personality, content, emotional")
logger.info("🔌 API routes: /api/creative/*")
logger.info("🎭 Capabilities: autonomous content, personality evolution, emotional responsiveness")
logger.info("⚡ Ready for creative evolution and autonomous content generation")
