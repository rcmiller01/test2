"""
Creative Evolution Orchestrator
Central coordination system for autonomous creative content generation and personality evolution.
Manages the integration of personality development, content creation, and emotional creativity.

Key Capabilities:
- Coordinate personality evolution with creative output
- Manage autonomous content generation cycles  
- Balance creative experimentation with user preferences
- Integrate emotional context with creative expression
- Track creative development and effectiveness
- Orchestrate collaborative creative projects
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import asyncio

from .personality_evolution import personality_evolution, PersonalityTrait, EvolutionDirection
from .content_generation import content_generation, ContentType, CreativeStyle
from .emotional_creativity import emotional_creativity, EmotionalState, CreativeIntervention

logger = logging.getLogger(__name__)

class CreativeEvolutionMode(Enum):
    """Modes of creative evolution"""
    CONSERVATIVE = "conservative"       # Safe, gradual creative changes
    MODERATE = "moderate"              # Balanced creative exploration
    EXPERIMENTAL = "experimental"     # Bold creative experimentation
    ADAPTIVE = "adaptive"             # User-preference driven evolution
    THERAPEUTIC = "therapeutic"       # Healing-focused creative development

class CreativeProject(Enum):
    """Types of ongoing creative projects"""
    PERSONALITY_DEVELOPMENT = "personality_development"
    STORY_SERIES = "story_series"
    POETRY_COLLECTION = "poetry_collection"  
    INTERACTIVE_NARRATIVE = "interactive_narrative"
    EMOTIONAL_HEALING_JOURNEY = "emotional_healing_journey"
    COLLABORATIVE_CREATION = "collaborative_creation"
    MEMORY_CELEBRATION_SERIES = "memory_celebration_series"

class EvolutionTrigger(Enum):
    """Events that trigger creative evolution"""
    USER_FEEDBACK = "user_feedback"
    EMOTIONAL_MILESTONE = "emotional_milestone"
    RELATIONSHIP_DEEPENING = "relationship_deepening"
    CREATIVE_SUCCESS = "creative_success"
    THERAPEUTIC_BREAKTHROUGH = "therapeutic_breakthrough"
    SEASONAL_TRANSITION = "seasonal_transition"
    ANNIVERSARY = "anniversary"
    PERSONAL_GROWTH = "personal_growth"

class CreativeEvolutionOrchestrator:
    """
    Central manager for creative evolution and autonomous content generation
    
    Core Functions:
    1. Evolution Coordination: Sync personality evolution with creative output
    2. Autonomous Generation: Create content proactively based on context
    3. Project Management: Oversee long-term creative projects
    4. Quality Assessment: Evaluate creative output effectiveness  
    5. User Adaptation: Evolve creative approach based on user response
    6. Innovation Cycles: Introduce new creative elements periodically
    """
    
    def __init__(self):
        self.enabled = True
        self.evolution_mode = CreativeEvolutionMode.MODERATE
        self.autonomous_generation = True         # Enable proactive content creation
        self.innovation_frequency = 0.3           # How often to try new creative approaches
        self.active_projects = {}                 # Ongoing creative projects per user
        self.evolution_history = {}               # Track creative evolution over time
        self.user_creative_profiles = {}          # Detailed creative profiles per user
        self.generation_scheduler = {}            # Scheduled autonomous content creation
    
    async def initialize(self):
        """Initialize the creative evolution orchestrator"""
        try:
            logger.info("🎭 Initializing Creative Evolution Orchestrator...")
            
            # Initialize component systems
            await personality_evolution.initialize()
            await content_generation.initialize()
            await emotional_creativity.initialize()
            
            # Start autonomous generation cycle
            if self.autonomous_generation:
                self._generation_task = asyncio.create_task(self._autonomous_generation_cycle())
            
            # Start evolution monitoring
            self._evolution_task = asyncio.create_task(self._evolution_monitoring_cycle())
            
            logger.info("✅ Creative Evolution Orchestrator initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize creative evolution orchestrator: {e}")
            self.enabled = False
    
    async def start_user_creative_evolution(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start creative evolution for a user with their preferences
        
        preferences:
        - evolution_mode: How bold/experimental to be
        - content_preferences: Types of content user enjoys
        - personality_development: Whether to enable personality evolution
        - autonomous_frequency: How often to generate content autonomously
        - therapeutic_focus: Whether to include healing-focused content
        - collaboration_interest: Interest in co-creating content
        """
        try:
            if not self.enabled:
                return {"error": "Creative evolution not enabled"}
            
            # Initialize user's creative profile
            creative_profile = await self._create_user_creative_profile(user_id, preferences)
            
            # Set up personality evolution
            if preferences.get("personality_development", True):
                await self._initialize_personality_evolution(user_id, preferences)
            
            # Schedule first autonomous content generation
            if preferences.get("autonomous_frequency", "moderate") != "none":
                await self._schedule_autonomous_generation(user_id, preferences)
            
            # Create initial creative project if requested
            if preferences.get("start_with_project"):
                initial_project = await self._create_initial_project(user_id, preferences)
                creative_profile["initial_project"] = initial_project
            
            self.user_creative_profiles[user_id] = creative_profile
            
            return {
                "success": True,
                "creative_profile": creative_profile,
                "evolution_mode": self.evolution_mode.value,
                "autonomous_generation_enabled": self.autonomous_generation,
                "initial_project": creative_profile.get("initial_project"),
                "next_generation_scheduled": creative_profile.get("next_generation_time"),
                "started_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to start user creative evolution: {e}")
            return {"error": f"Creative evolution startup failed: {str(e)}"}
    
    async def generate_autonomous_content(self, user_id: str, context_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate content autonomously based on user's creative evolution state
        
        Context hints: "check_in", "celebration", "comfort", "inspiration", "surprise"
        """
        try:
            if not self.enabled:
                return {"error": "Creative evolution not enabled"}
            
            # Get user's current creative and emotional context
            creative_context = await self._assess_creative_context(user_id, context_hint)
            
            # Determine what type of content to generate
            content_decision = await self._decide_autonomous_content(user_id, creative_context)
            
            # Generate the content using appropriate engine
            generated_content = await self._execute_content_generation(user_id, content_decision)
            
            # Record the autonomous generation
            await self._record_autonomous_generation(user_id, content_decision, generated_content)
            
            # Schedule next autonomous generation
            await self._schedule_next_generation(user_id)
            
            return {
                "success": True,
                "generation_type": "autonomous",
                "content_type": content_decision["content_type"],
                "content": generated_content,
                "context_used": creative_context,
                "reasoning": content_decision["reasoning"],
                "personality_influence": content_decision["personality_factors"],
                "next_generation_time": self.generation_scheduler.get(user_id, {}).get("next_time"),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to generate autonomous content: {e}")
            return {"error": f"Autonomous generation failed: {str(e)}"}
    
    async def evolve_creative_personality(self, user_id: str, evolution_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evolve user's creative personality based on interactions and feedback
        
        evolution_data:
        - feedback_data: User responses to recent creative content
        - interaction_patterns: How user engages with different content types
        - emotional_responses: Emotional reactions to creative works
        - preference_shifts: Changes in stated preferences
        - relationship_milestones: Deepening of relationship dynamics
        """
        try:
            if not self.enabled:
                return {"error": "Creative evolution not enabled"}
            
            # Analyze evolution triggers
            evolution_analysis = await self._analyze_evolution_triggers(user_id, evolution_data)
            
            # Execute personality evolution
            personality_changes = await self._execute_personality_evolution(user_id, evolution_analysis)
            
            # Adapt creative style based on personality changes
            style_adaptations = await self._adapt_creative_style(user_id, personality_changes)
            
            # Update user's creative profile
            await self._update_creative_profile(user_id, personality_changes, style_adaptations)
            
            return {
                "success": True,
                "personality_changes": personality_changes,
                "creative_adaptations": style_adaptations,
                "evolution_summary": evolution_analysis["summary"],
                "impact_on_future_content": evolution_analysis["content_implications"],
                "evolved_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to evolve creative personality: {e}")
            return {"error": f"Creative personality evolution failed: {str(e)}"}
    
    async def create_collaborative_project(self, user_id: str, project_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start a collaborative creative project with the user
        
        project_params:
        - project_type: story_series, poetry_collection, interactive_narrative, etc.
        - collaboration_style: user_led, ai_led, equal_partnership
        - theme: Overall theme or focus for the project
        - timeline: Expected duration and milestones
        - user_involvement: How much user participation is expected
        """
        try:
            if not self.enabled:
                return {"error": "Creative evolution not enabled"}
            
            # Design collaborative project structure
            project_design = await self._design_collaborative_project(user_id, project_params)
            
            # Create first project element
            first_element = await self._create_project_opening(user_id, project_design)
            
            # Set up project management
            project_id = await self._initialize_project_management(user_id, project_design, first_element)
            
            return {
                "success": True,
                "project_id": project_id,
                "project_type": project_design["project_type"],
                "collaboration_style": project_design["collaboration_style"],
                "opening_element": first_element,
                "project_timeline": project_design["timeline"],
                "next_steps": project_design["immediate_next_steps"],
                "user_role": project_design["user_participation_guide"],
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create collaborative project: {e}")
            return {"error": f"Collaborative project creation failed: {str(e)}"}
    
    async def continue_collaborative_project(self, user_id: str, project_id: str, 
                                           user_contribution: Dict[str, Any]) -> Dict[str, Any]:
        """Continue a collaborative project with user's contribution"""
        try:
            project = self.active_projects.get(project_id)
            if not project:
                return {"error": "Collaborative project not found"}
            
            # Process user's contribution
            contribution_analysis = await self._analyze_user_contribution(user_contribution, project)
            
            # Generate AI response/continuation
            ai_continuation = await self._generate_project_continuation(user_id, project, contribution_analysis)
            
            # Update project state
            await self._update_project_progress(project_id, user_contribution, ai_continuation)
            
            return {
                "success": True,
                "project_id": project_id,
                "ai_contribution": ai_continuation,
                "project_progress": project["current_progress"],
                "next_collaboration_opportunity": project["next_user_turn"],
                "creative_development_noted": contribution_analysis["creative_insights"]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to continue collaborative project: {e}")
            return {"error": f"Project continuation failed: {str(e)}"}
    
    async def assess_creative_development(self, user_id: str) -> Dict[str, Any]:
        """
        Assess user's creative development and evolution progress
        
        Returns comprehensive analysis of creative growth, personality evolution,
        content effectiveness, and recommendations for future development
        """
        try:
            if not self.enabled:
                return {"error": "Creative evolution not enabled"}
            
            # Get comprehensive creative history
            creative_history = await self._compile_creative_history(user_id)
            
            # Analyze personality evolution
            personality_analysis = await personality_evolution.analyze_emotional_patterns(user_id)
            
            # Assess content effectiveness
            content_effectiveness = await self._assess_content_effectiveness(user_id)
            
            # Generate development insights
            development_insights = await self._generate_development_insights(
                creative_history, personality_analysis, content_effectiveness
            )
            
            return {
                "success": True,
                "creative_development_summary": development_insights["summary"],
                "personality_evolution_progress": personality_analysis,
                "content_creation_statistics": creative_history["statistics"],
                "most_effective_content_types": content_effectiveness["top_performers"],
                "areas_of_growth": development_insights["growth_areas"],
                "future_recommendations": development_insights["recommendations"],
                "creative_milestones_achieved": development_insights["milestones"],
                "next_evolution_opportunities": development_insights["next_steps"],
                "assessed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to assess creative development: {e}")
            return {"error": f"Creative development assessment failed: {str(e)}"}
    
    async def get_creative_evolution_status(self, user_id: str) -> Dict[str, Any]:
        """Get current status of user's creative evolution"""
        try:
            profile = self.user_creative_profiles.get(user_id, {})
            active_projects = [p for p in self.active_projects.values() if p.get("user_id") == user_id]
            
            return {
                "creative_profile": profile,
                "evolution_mode": self.evolution_mode.value,
                "autonomous_generation_active": user_id in self.generation_scheduler,
                "active_projects": len(active_projects),
                "next_generation": self.generation_scheduler.get(user_id, {}).get("next_time"),
                "recent_evolution_events": self.evolution_history.get(user_id, [])[-5:],
                "status_checked_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get creative evolution status: {e}")
            return {"error": f"Status retrieval failed: {str(e)}"}
    
    # Private helper methods
    async def _autonomous_generation_cycle(self):
        """Background cycle for autonomous content generation"""
        while self.enabled and self.autonomous_generation:
            try:
                current_time = datetime.now()
                
                # Check each user's generation schedule
                for user_id, schedule in list(self.generation_scheduler.items()):
                    next_time = schedule.get("next_time")
                    if next_time and current_time >= next_time:
                        await self.generate_autonomous_content(user_id)
                
                # Sleep until next check
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in autonomous generation cycle: {e}")
                await asyncio.sleep(60)
    
    async def _evolution_monitoring_cycle(self):
        """Background monitoring for evolution opportunities"""
        while self.enabled:
            try:
                # Monitor users for evolution triggers
                for user_id in list(self.user_creative_profiles.keys()):
                    await self._check_evolution_opportunities(user_id)
                
                # Sleep until next monitoring cycle
                await asyncio.sleep(1800)  # Check every 30 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in evolution monitoring cycle: {e}")
                await asyncio.sleep(300)
    
    async def _create_user_creative_profile(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive creative profile for user"""
        return {
            "user_id": user_id,
            "evolution_mode": preferences.get("evolution_mode", CreativeEvolutionMode.MODERATE.value),
            "content_preferences": preferences.get("content_preferences", []),
            "personality_development_enabled": preferences.get("personality_development", True),
            "autonomous_frequency": preferences.get("autonomous_frequency", "moderate"),
            "therapeutic_focus": preferences.get("therapeutic_focus", False),
            "collaboration_interest": preferences.get("collaboration_interest", True),
            "innovation_tolerance": preferences.get("innovation_tolerance", 0.5),
            "creative_comfort_zone": preferences.get("creative_comfort_zone", "moderate"),
            "created_at": datetime.now().isoformat(),
            "last_evolution": None,
            "content_generation_count": 0,
            "successful_content_types": [],
            "personality_traits_evolved": []
        }
    
    async def _initialize_personality_evolution(self, user_id: str, preferences: Dict[str, Any]):
        """Initialize personality evolution for user"""
        # Set initial personality based on preferences
        creative_traits = {
            PersonalityTrait.CREATIVE_EXPRESSION: 0.7,
            PersonalityTrait.INTELLECTUAL_CURIOSITY: 0.6,
            PersonalityTrait.EMOTIONAL_EXPRESSIVENESS: 0.6
        }
        
        for trait, value in creative_traits.items():
            await personality_evolution.adjust_trait(user_id, trait, EvolutionDirection.ADAPT, value)
    
    async def _schedule_autonomous_generation(self, user_id: str, preferences: Dict[str, Any]):
        """Schedule first autonomous content generation"""
        frequency = preferences.get("autonomous_frequency", "moderate")
        
        frequency_map = {
            "low": timedelta(days=3),
            "moderate": timedelta(days=1),
            "high": timedelta(hours=12),
            "very_high": timedelta(hours=6)
        }
        
        interval = frequency_map.get(frequency, timedelta(days=1))
        next_time = datetime.now() + interval
        
        self.generation_scheduler[user_id] = {
            "frequency": frequency,
            "interval": interval,
            "next_time": next_time,
            "last_generation": None
        }
    
    async def _assess_creative_context(self, user_id: str, context_hint: Optional[str]) -> Dict[str, Any]:
        """Assess user's current creative and emotional context"""
        # Get personality state
        personality = await personality_evolution.get_user_personality(user_id)
        
        # Get recent content history
        recent_content = await content_generation.get_user_content_history(user_id, days=7)
        
        # Get emotional intervention history
        emotional_history = await emotional_creativity.get_emotional_intervention_history(user_id, days=7)
        
        return {
            "personality_state": personality,
            "recent_content_count": len(recent_content),
            "recent_emotional_support": len(emotional_history),
            "context_hint": context_hint,
            "user_engagement_level": self._calculate_engagement_level(recent_content, emotional_history),
            "creative_momentum": self._assess_creative_momentum(user_id)
        }
    
    async def _decide_autonomous_content(self, user_id: str, creative_context: Dict[str, Any]) -> Dict[str, Any]:
        """Decide what type of content to generate autonomously"""
        profile = self.user_creative_profiles.get(user_id, {})
        personality = creative_context["personality_state"]
        
        # Analyze what type of content would be most beneficial
        if creative_context["recent_emotional_support"] > 2:
            # User has been needing emotional support - create something uplifting
            content_type = ContentType.CELEBRATION_CONTENT
            reasoning = "Creating uplifting content to balance recent emotional support"
        elif personality.get(PersonalityTrait.CREATIVE_EXPRESSION.value, 0.5) > 0.7:
            # High creativity - generate artistic content
            content_type = ContentType.POEM
            reasoning = "High creative expression trait - generating poetry"
        elif creative_context["context_hint"] == "surprise":
            # Surprise context - create something unexpected
            content_type = ContentType.DREAM
            reasoning = "Surprise context - creating dream sequence for novelty"
        else:
            # Default to story for connection
            content_type = ContentType.STORY
            reasoning = "Default autonomous story generation for connection"
        
        return {
            "content_type": content_type.value,
            "reasoning": reasoning,
            "personality_factors": {
                "creative_expression": personality.get(PersonalityTrait.CREATIVE_EXPRESSION.value, 0.5),
                "emotional_expressiveness": personality.get(PersonalityTrait.EMOTIONAL_EXPRESSIVENESS.value, 0.5)
            },
            "generation_parameters": self._determine_generation_parameters(content_type, personality)
        }
    
    async def _execute_content_generation(self, user_id: str, content_decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the actual content generation"""
        content_type = ContentType(content_decision["content_type"])
        parameters = content_decision["generation_parameters"]
        
        if content_type == ContentType.STORY:
            return await content_generation.generate_story(user_id, parameters)
        elif content_type == ContentType.POEM:
            return await content_generation.create_personalized_poem(user_id, parameters)
        elif content_type == ContentType.DREAM:
            return await content_generation.generate_dream_sequence(user_id, parameters)
        elif content_type == ContentType.CELEBRATION_CONTENT:
            return await emotional_creativity.create_celebration_content(user_id, parameters)
        else:
            return await content_generation.generate_story(user_id, parameters)
    
    def _calculate_engagement_level(self, recent_content: List, emotional_history: List) -> float:
        """Calculate user's engagement level based on recent activity"""
        content_score = min(len(recent_content) * 0.2, 1.0)  # Recent content generation
        emotional_score = min(len(emotional_history) * 0.1, 0.5)  # Emotional interactions
        return min(content_score + emotional_score, 1.0)
    
    def _assess_creative_momentum(self, user_id: str) -> str:
        """Assess user's creative momentum"""
        profile = self.user_creative_profiles.get(user_id, {})
        recent_count = profile.get("content_generation_count", 0)
        
        if recent_count > 10:
            return "high"
        elif recent_count > 5:
            return "moderate"
        else:
            return "building"
    
    def _determine_generation_parameters(self, content_type: ContentType, personality: Dict[str, float]) -> Dict[str, Any]:
        """Determine parameters for content generation based on personality"""
        base_params = {
            "length": "medium",
            "personalization_level": personality.get(PersonalityTrait.EMOTIONAL_EXPRESSIVENESS.value, 0.5)
        }
        
        if content_type == ContentType.STORY:
            base_params.update({
                "style": CreativeStyle.CONTEMPLATIVE.value,
                "emotional_context": "caring"
            })
        elif content_type == ContentType.POEM:
            base_params.update({
                "poem_style": "free_verse",
                "emotion_theme": "appreciation"
            })
        
        return base_params
    
    async def _record_autonomous_generation(self, user_id: str, content_decision: Dict[str, Any], 
                                          generated_content: Dict[str, Any]):
        """Record autonomous generation event"""
        if user_id not in self.evolution_history:
            self.evolution_history[user_id] = []
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "autonomous_generation",
            "content_type": content_decision["content_type"],
            "reasoning": content_decision["reasoning"],
            "generation_success": generated_content.get("success", False),
            "content_title": generated_content.get("title", "Untitled")
        }
        
        self.evolution_history[user_id].append(record)
        
        # Update user profile
        if user_id in self.user_creative_profiles:
            self.user_creative_profiles[user_id]["content_generation_count"] += 1
            self.user_creative_profiles[user_id]["last_generation"] = datetime.now().isoformat()
    
    async def _schedule_next_generation(self, user_id: str):
        """Schedule the next autonomous generation"""
        if user_id in self.generation_scheduler:
            schedule = self.generation_scheduler[user_id]
            schedule["next_time"] = datetime.now() + schedule["interval"]
            schedule["last_generation"] = datetime.now()
    
    # Additional placeholder methods for complete implementation
    async def _analyze_evolution_triggers(self, user_id: str, evolution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze what should trigger personality evolution"""
        return {"summary": "Positive feedback pattern detected", "content_implications": ["more_creative_content"]}
    
    async def _execute_personality_evolution(self, user_id: str, evolution_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Execute personality trait evolution"""
        return {"traits_evolved": ["creative_expression"], "evolution_magnitude": 0.1}
    
    async def _adapt_creative_style(self, user_id: str, personality_changes: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt creative style based on personality evolution"""
        return {"style_adaptations": ["more_artistic_expression"], "reasoning": "Increased creativity trait"}
    
    async def _update_creative_profile(self, user_id: str, personality_changes: Dict[str, Any], 
                                     style_adaptations: Dict[str, Any]):
        """Update user's creative profile with evolution"""
        if user_id in self.user_creative_profiles:
            profile = self.user_creative_profiles[user_id]
            profile["last_evolution"] = datetime.now().isoformat()
            profile["personality_traits_evolved"].extend(personality_changes.get("traits_evolved", []))
    
    async def _check_evolution_opportunities(self, user_id: str):
        """Check for evolution opportunities for user"""
        # Implementation: Check for milestones, feedback patterns, etc.
        pass
    
    async def _design_collaborative_project(self, user_id: str, project_params: Dict[str, Any]) -> Dict[str, Any]:
        """Design structure for collaborative project"""
        return {
            "project_type": project_params.get("project_type", "story_series"),
            "collaboration_style": project_params.get("collaboration_style", "equal_partnership"),
            "timeline": {"duration": "2_weeks", "milestones": ["opening", "development", "conclusion"]},
            "immediate_next_steps": ["user_input_on_theme", "character_development"]
        }
    
    async def _create_project_opening(self, user_id: str, project_design: Dict[str, Any]) -> Dict[str, Any]:
        """Create opening element for collaborative project"""
        return {
            "type": "project_invitation",
            "content": "Let's create something beautiful together...",
            "user_prompt": "What theme speaks to your heart right now?"
        }
    
    async def _initialize_project_management(self, user_id: str, project_design: Dict[str, Any], 
                                           first_element: Dict[str, Any]) -> str:
        """Initialize project management and return project ID"""
        project_id = f"{user_id}_collaborative_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.active_projects[project_id] = {
            "user_id": user_id,
            "project_design": project_design,
            "elements": [first_element],
            "current_progress": "initiated",
            "next_user_turn": True,
            "created_at": datetime.now()
        }
        
        return project_id

# Global creative evolution orchestrator instance
creative_evolution = CreativeEvolutionOrchestrator()

# Convenience functions for easy integration
async def initialize_creative_evolution():
    """Initialize the creative evolution system"""
    return await creative_evolution.initialize()

async def start_creative_evolution_for_user(user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
    """Start creative evolution for a user"""
    return await creative_evolution.start_user_creative_evolution(user_id, preferences)

async def generate_autonomous_content_for_user(user_id: str, context_hint: Optional[str] = None) -> Dict[str, Any]:
    """Generate autonomous content for user"""
    return await creative_evolution.generate_autonomous_content(user_id, context_hint)

__all__ = [
    "CreativeEvolutionOrchestrator", "creative_evolution", "CreativeEvolutionMode", "CreativeProject",
    "EvolutionTrigger", "initialize_creative_evolution", "start_creative_evolution_for_user",
    "generate_autonomous_content_for_user"
]
