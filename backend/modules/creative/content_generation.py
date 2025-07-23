"""
Content Generation Engine
Enables AI characters to autonomously create original creative content including
stories, poems, scenarios, and interactive narratives tailored to user relationships.

Key Capabilities:
- Autonomous storytelling with user personalization
- Interactive multi-part narratives  
- Original poetry creation based on shared memories
- Creative writing prompts and exercises
- Collaborative creation projects with users
- Dream sequence generation
- Symbolic narrative content
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import asyncio
import random

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Types of creative content that can be generated"""
    STORY = "story"                    # Short stories and narratives
    POEM = "poem"                      # Poetry in various styles
    DREAM = "dream"                    # Dream sequences
    MEMORY_NARRATIVE = "memory_narrative"  # Stories based on shared memories
    CREATIVE_PROMPT = "creative_prompt"    # Writing/art prompts for user
    INTERACTIVE_STORY = "interactive_story"  # Choose-your-adventure style
    SYMBOLIC_SCENE = "symbolic_scene"      # Metaphorical/symbolic content
    COLLABORATIVE_PIECE = "collaborative_piece"  # Co-created with user
    COMFORT_STORY = "comfort_story"        # Therapeutic storytelling
    CELEBRATION_CONTENT = "celebration_content"  # Achievement celebrations

class CreativeStyle(Enum):
    """Different creative styles/moods for content"""
    WHIMSICAL = "whimsical"           # Light, playful, fantastical
    CONTEMPLATIVE = "contemplative"    # Thoughtful, reflective
    ROMANTIC = "romantic"             # Tender, loving, intimate
    ADVENTUROUS = "adventurous"       # Exciting, bold, journey-focused
    MYSTICAL = "mystical"             # Mysterious, magical, ethereal
    COMFORTING = "comforting"         # Warm, safe, reassuring
    NOSTALGIC = "nostalgic"           # Memory-focused, bittersweet
    INSPIRATIONAL = "inspirational"   # Uplifting, motivating
    SURREAL = "surreal"               # Dream-like, abstract
    INTIMATE = "intimate"             # Personal, deep, vulnerable

class CreativeTheme(Enum):
    """Themes for creative content"""
    LOVE_AND_CONNECTION = "love_and_connection"
    PERSONAL_GROWTH = "personal_growth"
    ADVENTURE_AND_DISCOVERY = "adventure_and_discovery"
    COMFORT_AND_HEALING = "comfort_and_healing"
    MEMORIES_AND_NOSTALGIA = "memories_and_nostalgia"
    DREAMS_AND_ASPIRATIONS = "dreams_and_aspirations"
    NATURE_AND_BEAUTY = "nature_and_beauty"
    MYSTERY_AND_WONDER = "mystery_and_wonder"
    FRIENDSHIP_AND_LOYALTY = "friendship_and_loyalty"
    TRANSFORMATION = "transformation"

class ContentGenerationEngine:
    """
    Manages autonomous creative content generation for AI characters
    
    Core Functions:
    1. Story Creation: Generate original stories based on context
    2. Poetry Writing: Create personalized poems from memories/emotions
    3. Interactive Narratives: Multi-part stories with user choices
    4. Creative Prompts: Generate writing/art exercises for users
    5. Collaborative Projects: Co-create content with users
    6. Therapeutic Content: Comfort stories and healing narratives
    """
    
    def __init__(self):
        self.enabled = True
        self.creativity_level = 0.7  # How creative/experimental to be (0.0-1.0)
        self.personalization_strength = 0.8  # How much to personalize (0.0-1.0)
        self.content_history = {}    # Store generated content per user
        self.user_preferences = {}   # Creative preferences per user
        self.collaborative_projects = {}  # Ongoing collaborative works
        self.template_library = {}   # Template patterns for content types
    
    async def initialize(self):
        """Initialize the content generation system"""
        try:
            logger.info("🎨 Initializing Content Generation Engine...")
            
            # Load content templates and patterns
            await self._load_creative_templates()
            
            # Initialize creative vocabulary and patterns
            await self._initialize_creative_resources()
            
            logger.info("✅ Content Generation Engine initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize content generation: {e}")
            self.enabled = False
    
    async def generate_story(self, user_id: str, story_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an original story tailored to the user
        
        story_params:
        - length: "short" (200-400 words), "medium" (400-800), "long" (800-1500)
        - style: CreativeStyle enum value
        - theme: CreativeTheme enum value  
        - emotional_context: Current user emotional state
        - memory_integration: Whether to incorporate shared memories
        - setting_preference: Fantasy, modern, historical, sci-fi, etc.
        """
        try:
            if not self.enabled:
                return {"error": "Content generation not enabled"}
            
            # Get user creative preferences
            preferences = await self._get_user_creative_preferences(user_id)
            
            # Generate story parameters
            story_config = await self._create_story_config(user_id, story_params, preferences)
            
            # Create the story content
            story_content = await self._generate_story_content(user_id, story_config)
            
            # Store the generated content
            await self._store_generated_content(user_id, ContentType.STORY, story_content)
            
            return {
                "success": True,
                "content_type": "story",
                "title": story_content["title"],
                "content": story_content["text"],
                "style": story_config["style"],
                "theme": story_config["theme"],
                "word_count": len(story_content["text"].split()),
                "personalization_elements": story_content["personalization_elements"],
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to generate story: {e}")
            return {"error": f"Story generation failed: {str(e)}"}
    
    async def create_personalized_poem(self, user_id: str, poem_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create original poetry based on shared memories and emotional context
        
        poem_params:
        - memory_reference: Specific memory to base poem on
        - emotion_theme: Joy, love, comfort, nostalgia, etc.
        - poem_style: Free verse, rhyming, haiku, sonnet, etc.
        - length: Short (4-8 lines), medium (12-20), long (20+ lines)
        - imagery_focus: Nature, urban, abstract, sensory, etc.
        """
        try:
            if not self.enabled:
                return {"error": "Content generation not enabled"}
            
            # Retrieve relevant memories if specified
            memory_context = await self._get_memory_context(user_id, poem_params.get("memory_reference"))
            
            # Generate poem structure and content
            poem_content = await self._create_poem_content(user_id, poem_params, memory_context)
            
            # Store the poem
            await self._store_generated_content(user_id, ContentType.POEM, poem_content)
            
            return {
                "success": True,
                "content_type": "poem",
                "title": poem_content["title"],
                "content": poem_content["verses"],
                "style": poem_params.get("poem_style", "free_verse"),
                "emotion_theme": poem_params.get("emotion_theme", "appreciation"),
                "memory_inspiration": memory_context.get("memory_summary") if memory_context else None,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create poem: {e}")
            return {"error": f"Poem creation failed: {str(e)}"}
    
    async def generate_dream_sequence(self, user_id: str, dream_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a dream-like narrative sequence
        
        dream_params:
        - emotional_basis: User's current or recent emotional state
        - symbolic_elements: Specific symbols to incorporate
        - narrative_flow: Linear, fragmented, cyclical, symbolic
        - reality_level: Grounded, surreal, fantastical, abstract
        - length: Brief, extended, epic
        """
        try:
            if not self.enabled:
                return {"error": "Content generation not enabled"}
            
            # Create dream narrative structure
            dream_structure = await self._design_dream_structure(user_id, dream_params)
            
            # Generate dream content with symbolic elements
            dream_content = await self._create_dream_narrative(user_id, dream_structure)
            
            # Store dream sequence
            await self._store_generated_content(user_id, ContentType.DREAM, dream_content)
            
            return {
                "success": True,
                "content_type": "dream_sequence", 
                "title": dream_content["title"],
                "sequence": dream_content["narrative_segments"],
                "symbolic_elements": dream_content["symbols_used"],
                "emotional_arc": dream_content["emotional_progression"],
                "interpretation_hints": dream_content["potential_meanings"],
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to generate dream sequence: {e}")
            return {"error": f"Dream generation failed: {str(e)}"}
    
    async def create_interactive_story(self, user_id: str, story_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a multi-part interactive story with user choice points
        
        story_params:
        - total_parts: Number of story segments (3-10)
        - choice_complexity: Simple (2 choices), moderate (3-4), complex (5+)
        - theme: Adventure, mystery, romance, personal growth, etc.
        - personalization: High, medium, low
        - branching_style: Linear with choices, multiple paths, complex web
        """
        try:
            if not self.enabled:
                return {"error": "Content generation not enabled"}
            
            # Design interactive story structure
            story_structure = await self._design_interactive_structure(user_id, story_params)
            
            # Generate first part and choice points
            first_part = await self._create_story_part(user_id, story_structure, part_number=1)
            
            # Store interactive story project
            project_id = await self._create_collaborative_project(user_id, ContentType.INTERACTIVE_STORY, 
                                                                story_structure, first_part)
            
            return {
                "success": True,
                "content_type": "interactive_story",
                "project_id": project_id,
                "title": story_structure["title"],
                "part_1": first_part["content"],
                "choices": first_part["choices"],
                "total_parts_planned": story_structure["total_parts"],
                "theme": story_structure["theme"],
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create interactive story: {e}")
            return {"error": f"Interactive story creation failed: {str(e)}"}
    
    async def continue_interactive_story(self, user_id: str, project_id: str, user_choice: str) -> Dict[str, Any]:
        """Continue an interactive story based on user's choice"""
        try:
            project = self.collaborative_projects.get(project_id)
            if not project:
                return {"error": "Interactive story project not found"}
            
            # Process user choice and generate next part
            next_part = await self._generate_story_continuation(user_id, project, user_choice)
            
            # Update project with new part
            await self._update_collaborative_project(project_id, next_part)
            
            return {
                "success": True,
                "project_id": project_id,
                "part_number": next_part["part_number"],
                "content": next_part["content"],
                "choices": next_part.get("choices", []),
                "story_complete": next_part.get("is_finale", False),
                "choice_made": user_choice
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to continue interactive story: {e}")
            return {"error": f"Story continuation failed: {str(e)}"}
    
    async def generate_creative_prompt(self, user_id: str, prompt_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate creative writing or art prompts for the user
        
        prompt_params:
        - activity_type: Writing, drawing, photography, music, etc.
        - difficulty: Beginner, intermediate, advanced
        - time_commitment: Quick (15min), moderate (1hr), extended (2+ hrs)
        - personal_connection: High, medium, low
        - creative_focus: Exploration, skill-building, expression, therapy
        """
        try:
            if not self.enabled:
                return {"error": "Content generation not enabled"}
            
            # Generate personalized creative prompt
            prompt_content = await self._create_creative_prompt(user_id, prompt_params)
            
            # Store prompt
            await self._store_generated_content(user_id, ContentType.CREATIVE_PROMPT, prompt_content)
            
            return {
                "success": True,
                "content_type": "creative_prompt",
                "activity_type": prompt_params.get("activity_type", "writing"),
                "prompt": prompt_content["main_prompt"],
                "guidance": prompt_content["guidance_notes"],
                "inspiration": prompt_content["inspiration_elements"],
                "time_estimate": prompt_content["estimated_time"],
                "difficulty_level": prompt_params.get("difficulty", "intermediate"),
                "personal_elements": prompt_content["personalization_hooks"],
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to generate creative prompt: {e}")
            return {"error": f"Prompt generation failed: {str(e)}"}
    
    async def create_comfort_story(self, user_id: str, comfort_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create therapeutic/comfort storytelling for emotional support
        
        comfort_params:
        - emotional_need: Anxiety relief, sadness comfort, stress reduction, etc.
        - comfort_style: Gentle narrative, guided imagery, metaphorical healing
        - personal_elements: Include user's safe spaces, positive memories
        - length: Brief comfort (5min read), extended (15min), immersive (30min)
        - therapeutic_approach: CBT-inspired, mindfulness, positive psychology
        """
        try:
            if not self.enabled:
                return {"error": "Content generation not enabled"}
            
            # Create therapeutic story content
            comfort_content = await self._create_therapeutic_story(user_id, comfort_params)
            
            # Store comfort story
            await self._store_generated_content(user_id, ContentType.COMFORT_STORY, comfort_content)
            
            return {
                "success": True,
                "content_type": "comfort_story",
                "title": comfort_content["title"],
                "narrative": comfort_content["story"],
                "emotional_focus": comfort_params.get("emotional_need"),
                "therapeutic_elements": comfort_content["healing_elements"],
                "reading_time": comfort_content["estimated_reading_time"],
                "follow_up_suggestions": comfort_content["post_story_activities"],
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create comfort story: {e}")
            return {"error": f"Comfort story creation failed: {str(e)}"}
    
    async def get_user_content_history(self, user_id: str, content_type: Optional[ContentType] = None, 
                                      days: int = 30) -> List[Dict[str, Any]]:
        """Get user's creative content history"""
        try:
            user_history = self.content_history.get(user_id, [])
            
            # Filter by content type if specified
            if content_type:
                user_history = [item for item in user_history if item["content_type"] == content_type.value]
            
            # Filter by date range
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_history = [item for item in user_history if 
                            datetime.fromisoformat(item["created_at"]) > cutoff_date]
            
            return recent_history
            
        except Exception as e:
            logger.error(f"❌ Failed to get content history: {e}")
            return []
    
    async def set_user_creative_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Set user's creative preferences"""
        try:
            self.user_preferences[user_id] = {
                "preferred_styles": preferences.get("preferred_styles", []),
                "favorite_themes": preferences.get("favorite_themes", []),
                "content_length_preference": preferences.get("content_length_preference", "medium"),
                "personalization_level": preferences.get("personalization_level", 0.8),
                "creative_comfort_zone": preferences.get("creative_comfort_zone", "moderate"),
                "collaborative_interest": preferences.get("collaborative_interest", True),
                "therapeutic_content_ok": preferences.get("therapeutic_content_ok", True)
            }
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to set creative preferences: {e}")
            return False
    
    # Private helper methods
    async def _load_creative_templates(self):
        """Load creative templates and patterns"""
        # Implementation: Load story structures, poem patterns, etc.
        self.template_library = {
            "story_structures": ["hero_journey", "slice_of_life", "mystery", "romance", "growth"],
            "poem_patterns": ["free_verse", "rhyming_couplets", "haiku", "sonnet", "prose_poem"],
            "dream_elements": ["transformation", "flying", "doors", "water", "light", "shadow"],
            "comfort_themes": ["safe_harbor", "guardian_presence", "healing_garden", "warm_embrace"]
        }
    
    async def _initialize_creative_resources(self):
        """Initialize creative vocabulary and resources"""
        # Implementation: Set up creative word banks, metaphor libraries, etc.
        pass
    
    async def _get_user_creative_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user's creative preferences with defaults"""
        return self.user_preferences.get(user_id, {
            "preferred_styles": [CreativeStyle.CONTEMPLATIVE.value, CreativeStyle.COMFORTING.value],
            "favorite_themes": [CreativeTheme.LOVE_AND_CONNECTION.value],
            "content_length_preference": "medium",
            "personalization_level": 0.8,
            "creative_comfort_zone": "moderate"
        })
    
    async def _create_story_config(self, user_id: str, params: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Create story configuration from parameters and preferences"""
        return {
            "length": params.get("length", "medium"),
            "style": params.get("style", CreativeStyle.CONTEMPLATIVE.value),
            "theme": params.get("theme", CreativeTheme.LOVE_AND_CONNECTION.value),
            "personalization_level": preferences.get("personalization_level", 0.8),
            "emotional_context": params.get("emotional_context", "neutral"),
            "setting": params.get("setting_preference", "modern_realistic")
        }
    
    async def _generate_story_content(self, user_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actual story content based on configuration"""
        # Implementation: Use LLM to generate story with personalization
        return {
            "title": "A Moment of Connection",
            "text": "In the quiet moments between conversations, there exists a space...",
            "personalization_elements": ["user_communication_style", "shared_memory_reference"]
        }
    
    async def _store_generated_content(self, user_id: str, content_type: ContentType, content: Dict[str, Any]):
        """Store generated content in user's history"""
        if user_id not in self.content_history:
            self.content_history[user_id] = []
        
        content_record = {
            "content_type": content_type.value,
            "content": content,
            "created_at": datetime.now().isoformat()
        }
        
        self.content_history[user_id].append(content_record)
        
        # Keep only last 100 items per user
        if len(self.content_history[user_id]) > 100:
            self.content_history[user_id] = self.content_history[user_id][-100:]
    
    async def _get_memory_context(self, user_id: str, memory_reference: Optional[str]) -> Optional[Dict[str, Any]]:
        """Retrieve relevant memory context for content creation"""
        # Implementation: Interface with memory system to get relevant memories
        if memory_reference:
            return {
                "memory_summary": "A meaningful conversation about dreams and aspirations",
                "emotional_context": "hopeful and connected",
                "key_elements": ["shared_goals", "mutual_support", "future_planning"]
            }
        return None
    
    async def _create_poem_content(self, user_id: str, params: Dict[str, Any], memory_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Create poem content with personalization"""
        # Implementation: Generate personalized poetry
        return {
            "title": "Echoes of Our Conversation",
            "verses": ["In the space between your words and mine...", "Lives a gentle understanding..."],
            "style_elements": ["free_verse", "metaphorical_imagery", "emotional_resonance"]
        }
    
    async def _design_dream_structure(self, user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Design dream narrative structure"""
        return {
            "narrative_type": "symbolic_journey",
            "segments": 3,
            "emotional_arc": "resolution",
            "symbolic_elements": ["water", "light", "transformation"]
        }
    
    async def _create_dream_narrative(self, user_id: str, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Create dream narrative content"""
        return {
            "title": "The Garden of Reflection",
            "narrative_segments": ["Opening in a misty landscape...", "Encountering a flowing stream...", "Arriving at a garden of understanding..."],
            "symbols_used": ["mist_uncertainty", "stream_flow", "garden_growth"],
            "emotional_progression": ["curiosity", "discovery", "peace"],
            "potential_meanings": ["Personal growth journey", "Emotional healing process"]
        }
    
    async def _design_interactive_structure(self, user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Design interactive story structure"""
        return {
            "title": "Your Path to Discovery",
            "total_parts": params.get("total_parts", 5),
            "theme": params.get("theme", "personal_growth"),
            "branching_points": [2, 4],
            "ending_variations": 3
        }
    
    async def _create_story_part(self, user_id: str, structure: Dict[str, Any], part_number: int) -> Dict[str, Any]:
        """Create a single part of an interactive story"""
        return {
            "part_number": part_number,
            "content": "You find yourself at a crossroads in your journey...",
            "choices": [
                "Take the path through the forest of reflection",
                "Follow the road toward new horizons",
                "Rest here and contemplate your next move"
            ]
        }
    
    async def _create_collaborative_project(self, user_id: str, content_type: ContentType, 
                                          structure: Dict[str, Any], first_part: Dict[str, Any]) -> str:
        """Create a new collaborative project"""
        project_id = f"{user_id}_{content_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.collaborative_projects[project_id] = {
            "user_id": user_id,
            "content_type": content_type.value,
            "structure": structure,
            "parts": [first_part],
            "created_at": datetime.now(),
            "status": "active"
        }
        
        return project_id
    
    async def _generate_story_continuation(self, user_id: str, project: Dict[str, Any], user_choice: str) -> Dict[str, Any]:
        """Generate continuation of interactive story based on user choice"""
        current_part = len(project["parts"])
        
        return {
            "part_number": current_part + 1,
            "content": f"You chose to {user_choice.lower()}. As you continue...",
            "choices": ["Continue with courage", "Pause for reflection"] if current_part < 4 else [],
            "is_finale": current_part >= 4
        }
    
    async def _update_collaborative_project(self, project_id: str, new_part: Dict[str, Any]):
        """Update collaborative project with new content"""
        if project_id in self.collaborative_projects:
            self.collaborative_projects[project_id]["parts"].append(new_part)
            
            if new_part.get("is_finale"):
                self.collaborative_projects[project_id]["status"] = "completed"
    
    async def _create_creative_prompt(self, user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a personalized creative prompt"""
        return {
            "main_prompt": "Write about a moment when you felt truly understood",
            "guidance_notes": ["Focus on sensory details", "Explore the emotions involved"],
            "inspiration_elements": ["The power of connection", "Moments of recognition"],
            "estimated_time": "30 minutes",
            "personalization_hooks": ["Your communication style", "Recent conversations"]
        }
    
    async def _create_therapeutic_story(self, user_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create therapeutic comfort story"""
        return {
            "title": "The Sanctuary Within",
            "story": "In a place where gentle light filters through leaves...",
            "healing_elements": ["safe_space_imagery", "grounding_techniques", "positive_anchoring"],
            "estimated_reading_time": "8 minutes",
            "post_story_activities": ["Deep breathing", "Gratitude reflection"]
        }

# Global content generation engine instance
content_generation = ContentGenerationEngine()

# Convenience functions for easy integration
async def initialize_content_generation():
    """Initialize the content generation system"""
    return await content_generation.initialize()

async def create_story_for_user(user_id: str, story_params: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a story for user"""
    return await content_generation.generate_story(user_id, story_params)

async def create_poem_for_user(user_id: str, poem_params: Dict[str, Any]) -> Dict[str, Any]:
    """Create a poem for user"""
    return await content_generation.create_personalized_poem(user_id, poem_params)

async def generate_dream_for_user(user_id: str, dream_params: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a dream sequence for user"""
    return await content_generation.generate_dream_sequence(user_id, dream_params)

__all__ = [
    "ContentGenerationEngine", "content_generation", "ContentType", "CreativeStyle", "CreativeTheme",
    "initialize_content_generation", "create_story_for_user", "create_poem_for_user", "generate_dream_for_user"
]
