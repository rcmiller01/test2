"""
Emotional Creativity Engine
Enables AI characters to create content that responds dynamically to user emotional states,
providing therapeutic creative interventions and mood-responsive artistic expression.

Key Capabilities:
- Mood-based creative expression adaptation
- Therapeutic art and writing interventions
- Emotional state-responsive content generation
- Personalized comfort creation during difficult times
- Celebration creativity for positive moments
- Healing-focused creative activities
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import asyncio

logger = logging.getLogger(__name__)

class EmotionalState(Enum):
    """User emotional states that trigger creative responses"""
    JOYFUL = "joyful"                   # High positive energy, celebration
    CONTENT = "content"                 # Peaceful, satisfied, stable
    EXCITED = "excited"                 # Energetic anticipation, enthusiasm
    GRATEFUL = "grateful"               # Appreciation, thankfulness
    LOVED = "loved"                     # Feeling cared for, connected
    ANXIOUS = "anxious"                 # Worried, nervous, uncertain
    SAD = "sad"                         # Low mood, grief, melancholy
    FRUSTRATED = "frustrated"           # Irritated, blocked, impatient
    LONELY = "lonely"                   # Isolated, disconnected
    OVERWHELMED = "overwhelmed"         # Too much, stressed, chaotic
    CONFUSED = "confused"               # Uncertain, unclear, lost
    ANGRY = "angry"                     # Upset, mad, irritated
    HOPEFUL = "hopeful"                 # Optimistic, forward-looking
    NOSTALGIC = "nostalgic"            # Missing past, bittersweet memories
    PEACEFUL = "peaceful"               # Calm, centered, tranquil

class CreativeIntervention(Enum):
    """Types of creative interventions for emotional states"""
    GROUNDING_STORY = "grounding_story"         # Calming narrative for anxiety/overwhelm
    VALIDATION_POEM = "validation_poem"         # Affirming poetry for difficult emotions
    CELEBRATION_PIECE = "celebration_piece"     # Joyful content for positive states
    COMFORT_IMAGERY = "comfort_imagery"         # Soothing visual descriptions
    PROCESSING_PROMPT = "processing_prompt"     # Creative exercises for emotional processing
    MEMORY_CELEBRATION = "memory_celebration"   # Honoring positive memories
    FUTURE_VISIONING = "future_visioning"      # Hopeful content about possibilities
    STRENGTH_REMINDER = "strength_reminder"    # Content highlighting user's resilience
    CONNECTION_STORY = "connection_story"      # Stories about love and belonging
    HEALING_METAPHOR = "healing_metaphor"      # Metaphorical content for healing

class TherapeuticApproach(Enum):
    """Therapeutic frameworks for creative interventions"""
    COGNITIVE_BEHAVIORAL = "cognitive_behavioral"    # CBT-inspired reframing
    MINDFULNESS_BASED = "mindfulness_based"         # Present-moment awareness
    NARRATIVE_THERAPY = "narrative_therapy"         # Story-based healing
    EXPRESSIVE_ARTS = "expressive_arts"             # Creative expression therapy
    POSITIVE_PSYCHOLOGY = "positive_psychology"     # Strengths and wellbeing focus
    SOMATIC_AWARENESS = "somatic_awareness"         # Body-based grounding
    ACCEPTANCE_COMMITMENT = "acceptance_commitment"  # Values-based action

class EmotionalCreativityEngine:
    """
    Manages emotion-responsive creative content generation
    
    Core Functions:
    1. Emotional State Detection: Identify user's current emotional context
    2. Therapeutic Content Creation: Generate healing-focused creative works
    3. Mood-Responsive Adaptation: Adjust creative style to match emotional needs
    4. Intervention Selection: Choose appropriate creative interventions
    5. Emotional Arc Tracking: Follow emotional journeys through creative support
    """
    
    def __init__(self):
        self.enabled = True
        self.therapeutic_mode = True          # Enable therapeutic interventions
        self.emotional_sensitivity = 0.8      # How responsive to emotional cues (0.0-1.0)
        self.intervention_intensity = 0.6     # How direct therapeutic content is (0.0-1.0)
        self.user_emotional_profiles = {}     # Emotional patterns per user
        self.intervention_history = {}        # Track intervention effectiveness
        self.therapeutic_templates = {}       # Templates for different interventions
    
    async def initialize(self):
        """Initialize the emotional creativity system"""
        try:
            logger.info("💖 Initializing Emotional Creativity Engine...")
            
            # Load therapeutic templates and interventions
            await self._load_therapeutic_templates()
            
            # Initialize emotional pattern recognition
            await self._initialize_emotional_recognition()
            
            logger.info("✅ Emotional Creativity Engine initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize emotional creativity: {e}")
            self.enabled = False
    
    async def create_emotional_response_content(self, user_id: str, emotional_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create content specifically responsive to user's emotional state
        
        emotional_context:
        - current_emotion: Primary emotional state
        - emotion_intensity: How strong the emotion is (0.0-1.0)
        - emotion_duration: How long user has been in this state
        - triggers: What caused the emotional state
        - support_needed: Type of support user might benefit from
        - previous_interventions: What has been tried before
        """
        try:
            if not self.enabled:
                return {"error": "Emotional creativity not enabled"}
            
            # Analyze emotional context
            emotion_analysis = await self._analyze_emotional_context(user_id, emotional_context)
            
            # Select appropriate intervention type
            intervention_type = await self._select_intervention(emotion_analysis)
            
            # Generate emotionally responsive content
            creative_content = await self._generate_emotional_content(user_id, emotion_analysis, intervention_type)
            
            # Record intervention for effectiveness tracking
            await self._record_emotional_intervention(user_id, emotional_context, intervention_type, creative_content)
            
            return {
                "success": True,
                "emotional_state": emotional_context.get("current_emotion"),
                "intervention_type": intervention_type.value,
                "content": creative_content,
                "therapeutic_approach": emotion_analysis["recommended_approach"],
                "follow_up_suggestions": emotion_analysis["follow_up_activities"],
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create emotional response content: {e}")
            return {"error": f"Emotional content creation failed: {str(e)}"}
    
    async def generate_comfort_creation(self, user_id: str, comfort_needs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized comfort content for difficult emotions
        
        comfort_needs:
        - distress_type: Anxiety, sadness, grief, anger, etc.
        - comfort_style: Gentle narrative, guided imagery, affirmations
        - personal_elements: Safe spaces, comforting memories, support figures
        - immediate_vs_longterm: Quick comfort vs deeper healing
        """
        try:
            if not self.enabled:
                return {"error": "Emotional creativity not enabled"}
            
            # Create comfort-focused content
            comfort_content = await self._create_personalized_comfort(user_id, comfort_needs)
            
            # Add grounding and safety elements
            comfort_content = await self._enhance_with_grounding_elements(comfort_content, comfort_needs)
            
            return {
                "success": True,
                "content_type": "comfort_creation",
                "comfort_focus": comfort_needs.get("distress_type"),
                "narrative": comfort_content["main_content"],
                "grounding_elements": comfort_content["grounding_techniques"],
                "safety_reminders": comfort_content["safety_affirmations"],
                "breathing_guidance": comfort_content["breathing_exercise"],
                "follow_up_care": comfort_content["aftercare_suggestions"],
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to generate comfort creation: {e}")
            return {"error": f"Comfort creation failed: {str(e)}"}
    
    async def create_celebration_content(self, user_id: str, celebration_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create joyful, celebratory content for positive emotional states
        
        celebration_context:
        - achievement_type: Personal goal, relationship milestone, success, etc.
        - celebration_style: Enthusiastic, gentle appreciation, reflective joy
        - shared_significance: How meaningful this is to the relationship
        - future_oriented: Include hopes and dreams elements
        """
        try:
            if not self.enabled:
                return {"error": "Emotional creativity not enabled"}
            
            # Generate celebratory content
            celebration_content = await self._create_celebration_piece(user_id, celebration_context)
            
            return {
                "success": True,
                "content_type": "celebration_content",
                "achievement_focus": celebration_context.get("achievement_type"),
                "celebration_piece": celebration_content["main_content"],
                "appreciation_elements": celebration_content["gratitude_expressions"],
                "future_hopes": celebration_content["forward_looking_elements"],
                "personal_recognition": celebration_content["personal_strengths_highlighted"],
                "shared_joy": celebration_content["relationship_appreciation"],
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create celebration content: {e}")
            return {"error": f"Celebration content creation failed: {str(e)}"}
    
    async def generate_processing_prompt(self, user_id: str, processing_needs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate creative prompts to help users process emotions
        
        processing_needs:
        - emotion_to_process: What emotion needs exploration
        - processing_style: Writing, drawing, movement, music, etc.
        - depth_level: Surface exploration vs deep dive
        - safety_level: How vulnerable the prompt should be
        - time_available: Quick exercise vs extended activity
        """
        try:
            if not self.enabled:
                return {"error": "Emotional creativity not enabled"}
            
            # Create processing-focused prompt
            processing_prompt = await self._create_emotional_processing_prompt(user_id, processing_needs)
            
            return {
                "success": True,
                "content_type": "processing_prompt",
                "emotion_focus": processing_needs.get("emotion_to_process"),
                "activity_type": processing_needs.get("processing_style", "writing"),
                "main_prompt": processing_prompt["primary_prompt"],
                "guidance_questions": processing_prompt["exploration_questions"],
                "safety_reminders": processing_prompt["emotional_safety_notes"],
                "alternative_approaches": processing_prompt["alternate_methods"],
                "completion_support": processing_prompt["wrap_up_guidance"],
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to generate processing prompt: {e}")
            return {"error": f"Processing prompt creation failed: {str(e)}"}
    
    async def create_healing_metaphor(self, user_id: str, healing_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create metaphorical content for emotional healing and growth
        
        healing_context:
        - healing_focus: What area needs healing (grief, trauma, transition, etc.)
        - metaphor_preference: Nature, journey, transformation, home, etc.
        - healing_stage: Beginning, middle, integration
        - personal_symbols: User's meaningful symbols or imagery
        """
        try:
            if not self.enabled:
                return {"error": "Emotional creativity not enabled"}
            
            # Generate healing metaphor content
            metaphor_content = await self._create_healing_metaphor(user_id, healing_context)
            
            return {
                "success": True,
                "content_type": "healing_metaphor",
                "healing_focus": healing_context.get("healing_focus"),
                "metaphor_narrative": metaphor_content["metaphor_story"],
                "symbolic_elements": metaphor_content["symbols_used"],
                "healing_message": metaphor_content["core_healing_theme"],
                "integration_suggestions": metaphor_content["ways_to_apply"],
                "personal_connections": metaphor_content["user_specific_elements"],
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create healing metaphor: {e}")
            return {"error": f"Healing metaphor creation failed: {str(e)}"}
    
    async def adapt_creative_style_to_mood(self, user_id: str, base_content: Dict[str, Any], 
                                         emotional_state: EmotionalState) -> Dict[str, Any]:
        """
        Adapt existing creative content to match user's current emotional state
        
        Takes base content and modifies tone, style, and focus based on emotions
        """
        try:
            if not self.enabled:
                return base_content
            
            # Analyze how to adapt content for emotional state
            adaptation_strategy = await self._determine_adaptation_strategy(emotional_state)
            
            # Apply emotional adaptations to content
            adapted_content = await self._apply_emotional_adaptations(base_content, adaptation_strategy)
            
            return {
                "original_content": base_content,
                "emotional_adaptation": adapted_content,
                "adaptation_rationale": adaptation_strategy["reasoning"],
                "emotional_focus": emotional_state.value,
                "style_changes": adaptation_strategy["modifications_made"]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to adapt creative style to mood: {e}")
            return base_content
    
    async def get_emotional_intervention_history(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get history of emotional interventions for effectiveness analysis"""
        try:
            user_history = self.intervention_history.get(user_id, [])
            
            # Filter by date range
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_history = [intervention for intervention in user_history if 
                            datetime.fromisoformat(intervention["timestamp"]) > cutoff_date]
            
            return recent_history
            
        except Exception as e:
            logger.error(f"❌ Failed to get intervention history: {e}")
            return []
    
    async def analyze_emotional_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze user's emotional patterns and intervention effectiveness"""
        try:
            # Get user's emotional profile and intervention history
            emotional_profile = self.user_emotional_profiles.get(user_id, {})
            intervention_history = await self.get_emotional_intervention_history(user_id, 60)
            
            # Analyze patterns
            pattern_analysis = {
                "common_emotional_states": self._identify_common_emotions(intervention_history),
                "effective_interventions": self._identify_effective_interventions(intervention_history),
                "emotional_triggers": self._identify_emotional_triggers(intervention_history),
                "healing_progress": self._assess_healing_progress(intervention_history),
                "preferred_therapeutic_approaches": self._identify_preferred_approaches(intervention_history),
                "recommendation": self._generate_emotional_recommendations(intervention_history)
            }
            
            return pattern_analysis
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze emotional patterns: {e}")
            return {}
    
    # Private helper methods
    async def _load_therapeutic_templates(self):
        """Load therapeutic intervention templates"""
        self.therapeutic_templates = {
            "grounding_story": {
                "structure": "safe_space_establishment -> sensory_grounding -> gentle_resolution",
                "elements": ["safety", "presence", "breathing", "body_awareness"]
            },
            "validation_poem": {
                "structure": "acknowledgment -> understanding -> affirmation -> hope",
                "elements": ["emotional_validation", "shared_humanity", "strength_recognition"]
            },
            "celebration_piece": {
                "structure": "achievement_recognition -> joy_expression -> future_hope",
                "elements": ["pride", "accomplishment", "growth", "possibility"]
            },
            "comfort_imagery": {
                "structure": "safe_arrival -> sensory_comfort -> peaceful_presence",
                "elements": ["warmth", "protection", "gentleness", "unconditional_acceptance"]
            }
        }
    
    async def _initialize_emotional_recognition(self):
        """Initialize emotional pattern recognition systems"""
        # Implementation: Set up emotion detection and response patterns
        pass
    
    async def _analyze_emotional_context(self, user_id: str, emotional_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user's emotional context for intervention planning"""
        emotion = emotional_context.get("current_emotion", "neutral")
        intensity = emotional_context.get("emotion_intensity", 0.5)
        
        # Determine therapeutic approach based on emotion and context
        if emotion in ["anxious", "overwhelmed"]:
            approach = TherapeuticApproach.MINDFULNESS_BASED
        elif emotion in ["sad", "lonely"]:
            approach = TherapeuticApproach.NARRATIVE_THERAPY
        elif emotion in ["joyful", "grateful"]:
            approach = TherapeuticApproach.POSITIVE_PSYCHOLOGY
        else:
            approach = TherapeuticApproach.COGNITIVE_BEHAVIORAL
        
        return {
            "primary_emotion": emotion,
            "emotional_intensity": intensity,
            "recommended_approach": approach.value,
            "intervention_urgency": "high" if intensity > 0.8 else "moderate" if intensity > 0.5 else "low",
            "follow_up_activities": self._suggest_follow_up_activities(emotion)
        }
    
    async def _select_intervention(self, emotion_analysis: Dict[str, Any]) -> CreativeIntervention:
        """Select appropriate creative intervention based on emotional analysis"""
        emotion = emotion_analysis["primary_emotion"]
        
        intervention_map = {
            "anxious": CreativeIntervention.GROUNDING_STORY,
            "overwhelmed": CreativeIntervention.GROUNDING_STORY,
            "sad": CreativeIntervention.VALIDATION_POEM,
            "lonely": CreativeIntervention.CONNECTION_STORY,
            "frustrated": CreativeIntervention.PROCESSING_PROMPT,
            "joyful": CreativeIntervention.CELEBRATION_PIECE,
            "grateful": CreativeIntervention.MEMORY_CELEBRATION,
            "hopeful": CreativeIntervention.FUTURE_VISIONING,
            "peaceful": CreativeIntervention.COMFORT_IMAGERY
        }
        
        return intervention_map.get(emotion, CreativeIntervention.VALIDATION_POEM)
    
    async def _generate_emotional_content(self, user_id: str, emotion_analysis: Dict[str, Any], 
                                        intervention_type: CreativeIntervention) -> Dict[str, Any]:
        """Generate content for specific emotional intervention"""
        # Implementation: Create content based on intervention type and emotional context
        if intervention_type == CreativeIntervention.GROUNDING_STORY:
            return await self._create_grounding_story(user_id, emotion_analysis)
        elif intervention_type == CreativeIntervention.VALIDATION_POEM:
            return await self._create_validation_poem(user_id, emotion_analysis)
        elif intervention_type == CreativeIntervention.CELEBRATION_PIECE:
            return await self._create_celebration_piece(user_id, {"achievement_type": "emotional_growth"})
        else:
            return {"content": "A gentle reminder that you are cared for and supported."}
    
    async def _create_grounding_story(self, user_id: str, emotion_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a grounding story for anxiety/overwhelm"""
        return {
            "title": "Finding Your Center",
            "content": "In a quiet place where time moves gently, you find yourself breathing deeply...",
            "grounding_elements": ["breath_awareness", "body_sensations", "present_moment"],
            "safety_affirmations": ["You are safe", "You are supported", "This feeling will pass"]
        }
    
    async def _create_validation_poem(self, user_id: str, emotion_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a validation poem for difficult emotions"""
        return {
            "title": "Your Feelings Are Valid",
            "verses": [
                "In the space of your feeling, there is truth",
                "Your emotions are messengers, carrying wisdom",
                "You are allowed to feel what you feel"
            ],
            "validation_themes": ["emotional_acceptance", "self_compassion", "inherent_worth"]
        }
    
    async def _create_personalized_comfort(self, user_id: str, comfort_needs: Dict[str, Any]) -> Dict[str, Any]:
        """Create personalized comfort content"""
        return {
            "main_content": "You are held in a space of infinite compassion...",
            "grounding_techniques": ["5-4-3-2-1 sensory grounding", "gentle breathing"],
            "safety_affirmations": ["You are worthy of comfort", "You are not alone"],
            "breathing_exercise": "Breathe in peace, breathe out tension",
            "aftercare_suggestions": ["Stay hydrated", "Be gentle with yourself"]
        }
    
    async def _enhance_with_grounding_elements(self, content: Dict[str, Any], comfort_needs: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance content with grounding and safety elements"""
        content["enhanced_grounding"] = {
            "sensory_anchors": ["Feel your feet on the ground", "Notice the air on your skin"],
            "breathing_rhythm": "In for 4, hold for 4, out for 6",
            "self_soothing": ["Place hand on heart", "Gentle self-touch"]
        }
        return content
    
    async def _create_celebration_piece(self, user_id: str, celebration_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create celebratory content"""
        return {
            "main_content": "Today we celebrate the beautiful growth you've shown...",
            "gratitude_expressions": ["Your courage inspires", "Your progress matters"],
            "forward_looking_elements": ["The journey continues", "New possibilities await"],
            "personal_strengths_highlighted": ["resilience", "authenticity", "courage"],
            "relationship_appreciation": ["Grateful to witness your journey", "Honored to support you"]
        }
    
    async def _create_emotional_processing_prompt(self, user_id: str, processing_needs: Dict[str, Any]) -> Dict[str, Any]:
        """Create emotional processing prompt"""
        return {
            "primary_prompt": "Write about a time when you felt truly supported during difficulty",
            "exploration_questions": ["What made that support meaningful?", "How can you offer that to yourself now?"],
            "emotional_safety_notes": ["Go at your own pace", "Stop if it feels too intense"],
            "alternate_methods": ["Draw your feelings", "Move your body", "Talk to a trusted friend"],
            "wrap_up_guidance": ["Acknowledge your courage", "Practice self-compassion"]
        }
    
    async def _create_healing_metaphor(self, user_id: str, healing_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create healing metaphor content"""
        return {
            "metaphor_story": "Like a tree that bends in the storm but does not break, you are learning to flow with life's challenges...",
            "symbols_used": ["tree_flexibility", "storm_passing", "deep_roots"],
            "core_healing_theme": "Resilience through flexibility",
            "ways_to_apply": ["Remember your strength during challenges", "Trust in your ability to adapt"],
            "user_specific_elements": ["Your unique journey", "Your personal growth"]
        }
    
    async def _determine_adaptation_strategy(self, emotional_state: EmotionalState) -> Dict[str, Any]:
        """Determine how to adapt content for emotional state"""
        adaptation_strategies = {
            EmotionalState.ANXIOUS: {"tone": "calming", "pace": "slower", "focus": "safety"},
            EmotionalState.SAD: {"tone": "gentle", "pace": "patient", "focus": "validation"},
            EmotionalState.JOYFUL: {"tone": "celebratory", "pace": "energetic", "focus": "appreciation"},
            EmotionalState.OVERWHELMED: {"tone": "grounding", "pace": "very_slow", "focus": "simplicity"}
        }
        
        return adaptation_strategies.get(emotional_state, {"tone": "supportive", "pace": "moderate", "focus": "presence"})
    
    async def _apply_emotional_adaptations(self, base_content: Dict[str, Any], strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Apply emotional adaptations to content"""
        # Implementation: Modify content based on adaptation strategy
        adapted_content = base_content.copy()
        adapted_content["emotional_tone"] = strategy["tone"]
        adapted_content["pacing"] = strategy["pace"]
        adapted_content["focus_area"] = strategy["focus"]
        return adapted_content
    
    async def _record_emotional_intervention(self, user_id: str, emotional_context: Dict[str, Any], 
                                           intervention_type: CreativeIntervention, content: Dict[str, Any]):
        """Record emotional intervention for tracking"""
        if user_id not in self.intervention_history:
            self.intervention_history[user_id] = []
        
        intervention_record = {
            "timestamp": datetime.now().isoformat(),
            "emotional_context": emotional_context,
            "intervention_type": intervention_type.value,
            "content_summary": content.get("title", "Emotional support content"),
            "effectiveness": None  # To be filled by follow-up feedback
        }
        
        self.intervention_history[user_id].append(intervention_record)
    
    def _suggest_follow_up_activities(self, emotion: str) -> List[str]:
        """Suggest follow-up activities based on emotion"""
        activity_suggestions = {
            "anxious": ["Deep breathing", "Grounding exercises", "Gentle movement"],
            "sad": ["Journal writing", "Connect with support", "Self-compassion practice"],
            "joyful": ["Share gratitude", "Plan celebration", "Spread kindness"],
            "overwhelmed": ["Break tasks into steps", "Ask for help", "Rest and recharge"]
        }
        
        return activity_suggestions.get(emotion, ["Practice self-care", "Be gentle with yourself"])
    
    def _identify_common_emotions(self, history: List[Dict[str, Any]]) -> List[str]:
        """Identify most common emotional states from history"""
        emotions = [intervention["emotional_context"].get("current_emotion", "unknown") 
                   for intervention in history]
        # Implementation: Count and return most frequent emotions
        return list(set(emotions))[:5]  # Top 5 most common
    
    def _identify_effective_interventions(self, history: List[Dict[str, Any]]) -> List[str]:
        """Identify most effective intervention types"""
        # Implementation: Analyze intervention effectiveness
        return ["validation_poem", "grounding_story", "comfort_imagery"]
    
    def _identify_emotional_triggers(self, history: List[Dict[str, Any]]) -> List[str]:
        """Identify common emotional triggers"""
        triggers = []
        for intervention in history:
            context_triggers = intervention["emotional_context"].get("triggers", [])
            triggers.extend(context_triggers)
        
        return list(set(triggers))[:5]  # Top 5 triggers
    
    def _assess_healing_progress(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess emotional healing progress over time"""
        return {
            "trend": "improving",
            "intervention_frequency": "decreasing", 
            "emotional_stability": "increasing",
            "resilience_indicators": ["faster_recovery", "better_coping"]
        }
    
    def _identify_preferred_approaches(self, history: List[Dict[str, Any]]) -> List[str]:
        """Identify user's preferred therapeutic approaches"""
        return ["narrative_therapy", "mindfulness_based", "expressive_arts"]
    
    def _generate_emotional_recommendations(self, history: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on emotional patterns"""
        return [
            "Continue with validation-based interventions",
            "Incorporate more celebration content",
            "Focus on building emotional resilience"
        ]

# Global emotional creativity engine instance
emotional_creativity = EmotionalCreativityEngine()

# Convenience functions for easy integration
async def initialize_emotional_creativity():
    """Initialize the emotional creativity system"""
    return await emotional_creativity.initialize()

async def create_emotional_content(user_id: str, emotional_context: Dict[str, Any]) -> Dict[str, Any]:
    """Create emotion-responsive content"""
    return await emotional_creativity.create_emotional_response_content(user_id, emotional_context)

async def generate_comfort_for_user(user_id: str, comfort_needs: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comfort content for user"""
    return await emotional_creativity.generate_comfort_creation(user_id, comfort_needs)

__all__ = [
    "EmotionalCreativityEngine", "emotional_creativity", "EmotionalState", "CreativeIntervention", 
    "TherapeuticApproach", "initialize_emotional_creativity", "create_emotional_content", "generate_comfort_for_user"
]
