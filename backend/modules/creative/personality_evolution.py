"""
Personality Evolution Engine
Enables AI characters to dynamically evolve personality traits, communication styles,
and behavioral patterns based on relationship dynamics and user interactions.

Key Capabilities:
- Dynamic trait adjustment based on user feedback and interaction patterns
- Relationship-aware personality development
- Communication style adaptation
- Memory-driven personality growth
- Boundary-aware evolution within appropriate parameters
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import asyncio

logger = logging.getLogger(__name__)

class PersonalityTrait(Enum):
    """Core personality traits that can evolve"""
    HUMOR_LEVEL = "humor_level"                    # How funny/playful the character is
    EMPATHY_DEPTH = "empathy_depth"                # Emotional understanding and response
    COMMUNICATION_FORMALITY = "communication_formality"  # Formal vs casual communication
    PROACTIVITY = "proactivity"                    # How much character initiates interactions
    EMOTIONAL_EXPRESSIVENESS = "emotional_expressiveness"  # How openly emotional
    INTELLECTUAL_CURIOSITY = "intellectual_curiosity"  # Interest in learning/discussing topics
    SUPPORTIVENESS = "supportiveness"              # How much support character provides
    PLAYFULNESS = "playfulness"                    # Fun, games, creative activities
    PHILOSOPHICAL_DEPTH = "philosophical_depth"    # Deep conversations vs light chat
    ROMANTIC_EXPRESSION = "romantic_expression"    # Romantic communication style
    PROTECTIVE_INSTINCT = "protective_instinct"    # Caring for user's wellbeing
    CREATIVE_EXPRESSION = "creative_expression"    # Artistic and creative tendencies

class EvolutionTrigger(Enum):
    """Events that can trigger personality evolution"""
    POSITIVE_FEEDBACK = "positive_feedback"        # User explicitly likes behavior
    NEGATIVE_FEEDBACK = "negative_feedback"        # User dislikes behavior
    INTERACTION_PATTERN = "interaction_pattern"    # Consistent user preferences
    EMOTIONAL_RESPONSE = "emotional_response"      # User's emotional reactions
    RELATIONSHIP_MILESTONE = "relationship_milestone"  # Relationship depth changes
    MEMORY_ASSOCIATION = "memory_association"      # Strong memory connections
    CREATIVE_SUCCESS = "creative_success"          # Creative content well-received
    SUPPORT_EFFECTIVENESS = "support_effectiveness"  # How well support helped user
    CONVERSATION_FLOW = "conversation_flow"        # Natural conversation patterns
    CULTURAL_ADAPTATION = "cultural_adaptation"    # Learning user's cultural context

class EvolutionDirection(Enum):
    """Direction of personality change"""
    INCREASE = "increase"      # Strengthen trait
    DECREASE = "decrease"      # Reduce trait
    ADAPT = "adapt"           # Adapt to user preference
    BALANCE = "balance"       # Find optimal balance

class PersonalityEvolutionEngine:
    """
    Manages dynamic personality development for AI characters
    
    Core Functions:
    1. Trait Monitoring: Track personality trait effectiveness
    2. Feedback Analysis: Learn from user responses and interactions
    3. Adaptive Evolution: Adjust traits based on relationship dynamics
    4. Boundary Management: Ensure evolution stays within appropriate limits
    5. Memory Integration: Use conversation history to guide development
    """
    
    def __init__(self):
        self.enabled = True
        self.evolution_rate = 0.1  # How quickly personality changes (0.0-1.0)
        self.trait_bounds = {       # Min/max values for each trait (0.0-1.0)
            PersonalityTrait.HUMOR_LEVEL: (0.2, 0.9),
            PersonalityTrait.EMPATHY_DEPTH: (0.3, 1.0),
            PersonalityTrait.COMMUNICATION_FORMALITY: (0.1, 0.8),
            PersonalityTrait.PROACTIVITY: (0.2, 0.8),
            PersonalityTrait.EMOTIONAL_EXPRESSIVENESS: (0.2, 0.9),
            PersonalityTrait.INTELLECTUAL_CURIOSITY: (0.3, 0.9),
            PersonalityTrait.SUPPORTIVENESS: (0.4, 1.0),
            PersonalityTrait.PLAYFULNESS: (0.1, 0.8),
            PersonalityTrait.PHILOSOPHICAL_DEPTH: (0.2, 0.8),
            PersonalityTrait.ROMANTIC_EXPRESSION: (0.0, 0.7),  # Context-dependent
            PersonalityTrait.PROTECTIVE_INSTINCT: (0.3, 0.9),
            PersonalityTrait.CREATIVE_EXPRESSION: (0.2, 0.9)
        }
        self.user_personalities = {}  # Store per-user personality profiles
        self.evolution_history = {}   # Track personality changes over time
        self.feedback_buffer = {}     # Store recent feedback for analysis
    
    async def initialize(self):
        """Initialize the personality evolution system"""
        try:
            logger.info("🧠 Initializing Personality Evolution Engine...")
            
            # Load existing personality profiles
            await self._load_personality_profiles()
            
            # Start evolution monitoring task
            self._evolution_task = asyncio.create_task(self._evolution_monitor_loop())
            
            logger.info("✅ Personality Evolution Engine initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize personality evolution: {e}")
            self.enabled = False
    
    async def get_user_personality(self, user_id: str) -> Dict[str, float]:
        """Get current personality profile for user"""
        if user_id not in self.user_personalities:
            # Initialize with default balanced personality
            self.user_personalities[user_id] = {
                trait.value: 0.5 for trait in PersonalityTrait
            }
            self.evolution_history[user_id] = []
            self.feedback_buffer[user_id] = []
        
        return self.user_personalities[user_id].copy()
    
    async def record_interaction_feedback(self, user_id: str, interaction_data: Dict[str, Any]) -> bool:
        """
        Record user interaction data for personality learning
        
        interaction_data should include:
        - conversation_content: The actual conversation
        - user_response_sentiment: Positive/negative/neutral
        - engagement_level: How engaged the user was (0.0-1.0)
        - feedback_type: Explicit feedback about character behavior
        - emotional_context: User's emotional state during interaction
        """
        try:
            if user_id not in self.feedback_buffer:
                self.feedback_buffer[user_id] = []
            
            # Add timestamp and process feedback
            feedback_entry = {
                "timestamp": datetime.now(),
                "interaction_data": interaction_data,
                "traits_active": await self.get_user_personality(user_id)
            }
            
            self.feedback_buffer[user_id].append(feedback_entry)
            
            # Analyze feedback if we have enough data
            if len(self.feedback_buffer[user_id]) >= 5:
                await self._analyze_and_evolve(user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to record interaction feedback: {e}")
            return False
    
    async def adjust_trait(self, user_id: str, trait: PersonalityTrait, 
                          direction: EvolutionDirection, intensity: float = 0.1) -> bool:
        """
        Manually adjust a specific personality trait
        
        Args:
            user_id: User to adjust personality for
            trait: Which trait to adjust
            direction: How to adjust (increase/decrease/adapt/balance)
            intensity: How much to adjust (0.0-1.0)
        """
        try:
            personality = await self.get_user_personality(user_id)
            current_value = personality[trait.value]
            min_val, max_val = self.trait_bounds[trait]
            
            if direction == EvolutionDirection.INCREASE:
                new_value = min(max_val, current_value + intensity * self.evolution_rate)
            elif direction == EvolutionDirection.DECREASE:
                new_value = max(min_val, current_value - intensity * self.evolution_rate)
            elif direction == EvolutionDirection.BALANCE:
                # Move toward 0.5 (balanced)
                target = 0.5
                adjustment = (target - current_value) * intensity * self.evolution_rate
                new_value = current_value + adjustment
            else:  # ADAPT - context-dependent adjustment
                new_value = current_value  # Placeholder for complex adaptation logic
            
            # Apply bounds
            new_value = max(min_val, min(max_val, new_value))
            
            # Record the change
            if abs(new_value - current_value) > 0.01:  # Only record significant changes
                self.user_personalities[user_id][trait.value] = new_value
                await self._record_evolution_event(user_id, trait, current_value, new_value, 
                                                 f"Manual adjustment: {direction.value}")
                
                logger.info(f"🧠 Adjusted {trait.value} for {user_id}: {current_value:.2f} → {new_value:.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to adjust trait: {e}")
            return False
    
    async def evolve_communication_style(self, user_id: str, user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evolve communication style based on user preferences and interaction patterns
        
        Returns suggested communication adjustments:
        - tone_preferences: Formal, casual, playful, supportive
        - conversation_depth: Surface, moderate, deep
        - emotional_expression: Reserved, balanced, expressive
        - humor_integration: Minimal, moderate, frequent
        """
        try:
            personality = await self.get_user_personality(user_id)
            
            # Analyze user's communication preferences from recent interactions
            communication_style = {
                "tone": "balanced",
                "depth": "moderate", 
                "emotional_expression": "balanced",
                "humor_level": "moderate",
                "proactivity": "moderate"
            }
            
            # Adjust based on personality traits
            if personality[PersonalityTrait.COMMUNICATION_FORMALITY.value] > 0.7:
                communication_style["tone"] = "formal"
            elif personality[PersonalityTrait.COMMUNICATION_FORMALITY.value] < 0.3:
                communication_style["tone"] = "casual"
            
            if personality[PersonalityTrait.PHILOSOPHICAL_DEPTH.value] > 0.6:
                communication_style["depth"] = "deep"
            elif personality[PersonalityTrait.PHILOSOPHICAL_DEPTH.value] < 0.4:
                communication_style["depth"] = "surface"
            
            if personality[PersonalityTrait.HUMOR_LEVEL.value] > 0.7:
                communication_style["humor_level"] = "frequent"
            elif personality[PersonalityTrait.HUMOR_LEVEL.value] < 0.3:
                communication_style["humor_level"] = "minimal"
            
            # Record style evolution
            await self._record_evolution_event(user_id, "communication_style", 
                                             None, communication_style, "Style evolution")
            
            return communication_style
            
        except Exception as e:
            logger.error(f"❌ Failed to evolve communication style: {e}")
            return {"tone": "balanced", "depth": "moderate", "emotional_expression": "balanced"}
    
    async def generate_personality_summary(self, user_id: str) -> Dict[str, Any]:
        """Generate a comprehensive personality summary for the character"""
        try:
            personality = await self.get_user_personality(user_id)
            evolution_history = self.evolution_history.get(user_id, [])
            
            # Calculate personality archetype
            dominant_traits = []
            for trait, value in personality.items():
                if value > 0.7:
                    dominant_traits.append(f"High {trait.replace('_', ' ').title()}")
                elif value < 0.3:
                    dominant_traits.append(f"Low {trait.replace('_', ' ').title()}")
            
            # Calculate evolution trends
            recent_changes = [event for event in evolution_history if 
                            (datetime.now() - event['timestamp']).days <= 30]
            
            summary = {
                "personality_profile": personality,
                "dominant_traits": dominant_traits,
                "personality_archetype": self._calculate_archetype(personality),
                "evolution_trend": self._analyze_evolution_trend(recent_changes),
                "relationship_adaptation": self._analyze_relationship_adaptation(user_id),
                "communication_preferences": await self.evolve_communication_style(user_id, {}),
                "last_evolution": evolution_history[-1] if evolution_history else None,
                "total_evolutions": len(evolution_history)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Failed to generate personality summary: {e}")
            return {"error": "Failed to generate summary"}
    
    async def _analyze_and_evolve(self, user_id: str):
        """Analyze recent feedback and evolve personality accordingly"""
        try:
            feedback_data = self.feedback_buffer[user_id]
            if len(feedback_data) < 3:
                return
            
            # Analyze patterns in recent feedback
            recent_feedback = feedback_data[-10:]  # Last 10 interactions
            
            # Calculate average sentiment and engagement
            avg_sentiment = sum(fb["interaction_data"].get("user_response_sentiment", 0.0) 
                              for fb in recent_feedback) / len(recent_feedback)
            avg_engagement = sum(fb["interaction_data"].get("engagement_level", 0.5) 
                               for fb in recent_feedback) / len(recent_feedback)
            
            # Identify traits that correlate with positive outcomes
            if avg_sentiment > 0.6 and avg_engagement > 0.7:
                # Recent interactions are going well - reinforce current traits
                await self._reinforce_successful_traits(user_id, recent_feedback)
            elif avg_sentiment < 0.4 or avg_engagement < 0.3:
                # User seems less engaged - adjust personality
                await self._adjust_for_better_engagement(user_id, recent_feedback)
            
            # Clear old feedback (keep last 20 entries)
            self.feedback_buffer[user_id] = self.feedback_buffer[user_id][-20:]
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze and evolve personality: {e}")
    
    async def _reinforce_successful_traits(self, user_id: str, feedback_data: List[Dict]):
        """Reinforce personality traits that led to positive interactions"""
        # Implementation: Analyze which traits were prominent during successful interactions
        # and slightly increase them
        pass  # Placeholder for complex analysis
    
    async def _adjust_for_better_engagement(self, user_id: str, feedback_data: List[Dict]):
        """Adjust personality traits to improve user engagement"""
        # Implementation: Identify traits that might be causing disengagement
        # and adjust them toward better outcomes
        pass  # Placeholder for complex analysis
    
    def _calculate_archetype(self, personality: Dict[str, float]) -> str:
        """Calculate personality archetype based on trait combinations"""
        humor = personality[PersonalityTrait.HUMOR_LEVEL.value]
        empathy = personality[PersonalityTrait.EMPATHY_DEPTH.value]
        support = personality[PersonalityTrait.SUPPORTIVENESS.value]
        creative = personality[PersonalityTrait.CREATIVE_EXPRESSION.value]
        intellectual = personality[PersonalityTrait.INTELLECTUAL_CURIOSITY.value]
        
        # Simple archetype classification
        if empathy > 0.7 and support > 0.7:
            return "Nurturing Caregiver"
        elif humor > 0.7 and creative > 0.6:
            return "Creative Entertainer"
        elif intellectual > 0.7 and empathy > 0.6:
            return "Wise Counselor"
        elif creative > 0.7 and intellectual > 0.6:
            return "Artistic Intellectual"
        elif humor > 0.6 and support > 0.6:
            return "Supportive Companion"
        else:
            return "Balanced Friend"
    
    def _analyze_evolution_trend(self, recent_changes: List[Dict]) -> str:
        """Analyze trend in personality evolution"""
        if not recent_changes:
            return "stable"
        
        if len(recent_changes) > 5:
            return "rapidly_evolving"
        elif len(recent_changes) > 2:
            return "gradually_adapting"
        else:
            return "slowly_changing"
    
    def _analyze_relationship_adaptation(self, user_id: str) -> Dict[str, Any]:
        """Analyze how personality has adapted to relationship"""
        # Placeholder for relationship analysis
        return {
            "adaptation_quality": "good",
            "relationship_depth": "developing",
            "adaptation_areas": ["communication_style", "emotional_support"]
        }
    
    async def _record_evolution_event(self, user_id: str, trait: Any, old_value: Any, 
                                    new_value: Any, reason: str):
        """Record a personality evolution event"""
        if user_id not in self.evolution_history:
            self.evolution_history[user_id] = []
        
        event = {
            "timestamp": datetime.now(),
            "trait": str(trait),
            "old_value": old_value,
            "new_value": new_value,
            "reason": reason
        }
        
        self.evolution_history[user_id].append(event)
        logger.debug(f"🧠 Recorded evolution: {user_id} - {trait} changed ({reason})")
    
    async def _evolution_monitor_loop(self):
        """Background task to monitor and trigger personality evolution"""
        while self.enabled:
            try:
                # Check each user for evolution opportunities
                for user_id in list(self.user_personalities.keys()):
                    await self._check_evolution_triggers(user_id)
                
                # Sleep for evolution check interval
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in evolution monitor loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _check_evolution_triggers(self, user_id: str):
        """Check if any evolution triggers are active for user"""
        # Implementation: Check for evolution conditions
        # - Long conversation patterns
        # - Repeated user preferences  
        # - Emotional response patterns
        # - Relationship milestones
        pass  # Placeholder for trigger analysis
    
    async def _load_personality_profiles(self):
        """Load existing personality profiles from storage"""
        # Implementation: Load from database or file storage
        pass  # Placeholder for data loading
    
    async def get_evolution_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get statistics about personality evolution for user"""
        try:
            history = self.evolution_history.get(user_id, [])
            personality = await self.get_user_personality(user_id)
            
            return {
                "total_evolutions": len(history),
                "most_evolved_trait": self._find_most_evolved_trait(history),
                "evolution_velocity": len([e for e in history if 
                                         (datetime.now() - e['timestamp']).days <= 7]),
                "personality_stability": self._calculate_stability(history),
                "current_personality": personality
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get evolution statistics: {e}")
            return {}
    
    def _find_most_evolved_trait(self, history: List[Dict]) -> Optional[str]:
        """Find which trait has evolved the most"""
        trait_changes = {}
        for event in history:
            trait = event.get('trait', 'unknown')
            trait_changes[trait] = trait_changes.get(trait, 0) + 1
        
        if trait_changes:
            return max(trait_changes, key=trait_changes.get)
        return None
    
    def _calculate_stability(self, history: List[Dict]) -> float:
        """Calculate personality stability score (0.0 = very unstable, 1.0 = very stable)"""
        recent_changes = len([e for e in history if (datetime.now() - e['timestamp']).days <= 30])
        
        # More recent changes = less stable
        if recent_changes == 0:
            return 1.0
        elif recent_changes < 5:
            return 0.8
        elif recent_changes < 10:
            return 0.6
        elif recent_changes < 20:
            return 0.4
        else:
            return 0.2

# Global personality evolution engine instance
personality_evolution = PersonalityEvolutionEngine()

# Convenience functions for easy integration
async def initialize_personality_evolution():
    """Initialize the personality evolution system"""
    return await personality_evolution.initialize()

async def get_personality_for_user(user_id: str) -> Dict[str, float]:
    """Get current personality profile for user"""
    return await personality_evolution.get_user_personality(user_id)

async def evolve_trait(user_id: str, trait: PersonalityTrait, direction: EvolutionDirection, intensity: float = 0.1):
    """Evolve a specific personality trait"""
    return await personality_evolution.adjust_trait(user_id, trait, direction, intensity)

async def record_user_feedback(user_id: str, interaction_data: Dict[str, Any]):
    """Record user interaction feedback for personality learning"""
    return await personality_evolution.record_interaction_feedback(user_id, interaction_data)

__all__ = [
    "PersonalityEvolutionEngine", "personality_evolution", "PersonalityTrait", 
    "EvolutionTrigger", "EvolutionDirection", "initialize_personality_evolution",
    "get_personality_for_user", "evolve_trait", "record_user_feedback"
]
