"""
Creative Evolution API Routes
REST endpoints for managing creative evolution, autonomous content generation,
and collaborative creative projects.
"""

import logging
from flask import Blueprint, request, jsonify
from datetime import datetime
import asyncio

from .creative_orchestrator import creative_evolution, CreativeEvolutionMode, CreativeProject
from .personality_evolution import personality_evolution, PersonalityTrait, EvolutionDirection
from .content_generation import content_generation, ContentType, CreativeStyle
from .emotional_creativity import emotional_creativity, EmotionalState, CreativeIntervention

logger = logging.getLogger(__name__)

creative_bp = Blueprint('creative', __name__, url_prefix='/api/creative')

# Initialize creative evolution system
@creative_bp.before_app_first_request
async def initialize_creative_system():
    """Initialize the creative evolution system"""
    try:
        await creative_evolution.initialize()
        logger.info("🎨 Creative Evolution API system initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize creative evolution API: {e}")

@creative_bp.route('/start', methods=['POST'])
async def start_user_creative_evolution():
    """Start creative evolution for a user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        preferences = data.get('preferences', {})
        
        if not user_id:
            return jsonify({
                "error": "user_id is required"
            }), 400
        
        # Start creative evolution
        evolution_data = await creative_evolution.start_user_creative_evolution(user_id, preferences)
        
        return jsonify({
            "status": "success",
            "message": "Creative evolution started",
            "evolution_data": evolution_data,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to start creative evolution: {e}")
        return jsonify({
            "error": "Failed to start creative evolution",
            "details": str(e)
        }), 500

@creative_bp.route('/status/<user_id>', methods=['GET'])
async def get_creative_evolution_status(user_id):
    """Get creative evolution status for a user"""
    try:
        status = await creative_evolution.get_creative_evolution_status(user_id)
        
        if not status or "error" in status:
            return jsonify({
                "error": "No creative evolution found for user",
                "user_id": user_id
            }), 404
        
        return jsonify({
            "status": "success",
            "evolution_status": status,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to get creative evolution status: {e}")
        return jsonify({
            "error": "Failed to get creative evolution status",
            "details": str(e)
        }), 500

@creative_bp.route('/generate/autonomous', methods=['POST'])
async def generate_autonomous_content():
    """Generate autonomous creative content"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        context_hint = data.get('context_hint')  # Optional: "check_in", "celebration", etc.
        
        if not user_id:
            return jsonify({
                "error": "user_id is required"
            }), 400
        
        # Generate autonomous content
        content_result = await creative_evolution.generate_autonomous_content(user_id, context_hint)
        
        return jsonify({
            "status": "success",
            "content_result": content_result,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to generate autonomous content: {e}")
        return jsonify({
            "error": "Failed to generate autonomous content",
            "details": str(e)
        }), 500

@creative_bp.route('/evolve/personality', methods=['POST'])
async def evolve_user_personality():
    """Evolve user's creative personality"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        evolution_data = data.get('evolution_data', {})
        
        if not user_id:
            return jsonify({
                "error": "user_id is required"
            }), 400
        
        # Evolve personality
        evolution_result = await creative_evolution.evolve_creative_personality(user_id, evolution_data)
        
        return jsonify({
            "status": "success",
            "evolution_result": evolution_result,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to evolve personality: {e}")
        return jsonify({
            "error": "Failed to evolve personality",
            "details": str(e)
        }), 500

# Content Generation Endpoints
@creative_bp.route('/content/story', methods=['POST'])
async def generate_story():
    """Generate a personalized story"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        story_params = data.get('story_params', {})
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        story_result = await content_generation.generate_story(user_id, story_params)
        
        return jsonify({
            "status": "success",
            "story": story_result,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to generate story: {e}")
        return jsonify({
            "error": "Failed to generate story",
            "details": str(e)
        }), 500

@creative_bp.route('/content/poem', methods=['POST'])
async def create_poem():
    """Create a personalized poem"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        poem_params = data.get('poem_params', {})
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        poem_result = await content_generation.create_personalized_poem(user_id, poem_params)
        
        return jsonify({
            "status": "success",
            "poem": poem_result,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to create poem: {e}")
        return jsonify({
            "error": "Failed to create poem",
            "details": str(e)
        }), 500

@creative_bp.route('/content/dream', methods=['POST'])
async def generate_dream_sequence():
    """Generate a dream sequence"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        dream_params = data.get('dream_params', {})
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        dream_result = await content_generation.generate_dream_sequence(user_id, dream_params)
        
        return jsonify({
            "status": "success",
            "dream": dream_result,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to generate dream sequence: {e}")
        return jsonify({
            "error": "Failed to generate dream sequence",
            "details": str(e)
        }), 500

@creative_bp.route('/content/interactive-story', methods=['POST'])
async def create_interactive_story():
    """Create an interactive story"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        story_params = data.get('story_params', {})
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        interactive_result = await content_generation.create_interactive_story(user_id, story_params)
        
        return jsonify({
            "status": "success",
            "interactive_story": interactive_result,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to create interactive story: {e}")
        return jsonify({
            "error": "Failed to create interactive story",
            "details": str(e)
        }), 500

@creative_bp.route('/content/interactive-story/continue', methods=['POST'])
async def continue_interactive_story():
    """Continue an interactive story with user choice"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        project_id = data.get('project_id')
        user_choice = data.get('user_choice')
        
        if not all([user_id, project_id, user_choice]):
            return jsonify({
                "error": "user_id, project_id, and user_choice are required"
            }), 400
        
        continuation_result = await content_generation.continue_interactive_story(user_id, project_id, user_choice)
        
        return jsonify({
            "status": "success",
            "continuation": continuation_result,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to continue interactive story: {e}")
        return jsonify({
            "error": "Failed to continue interactive story",
            "details": str(e)
        }), 500

@creative_bp.route('/content/prompt', methods=['POST'])
async def generate_creative_prompt():
    """Generate a creative prompt for the user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        prompt_params = data.get('prompt_params', {})
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        prompt_result = await content_generation.generate_creative_prompt(user_id, prompt_params)
        
        return jsonify({
            "status": "success",
            "creative_prompt": prompt_result,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to generate creative prompt: {e}")
        return jsonify({
            "error": "Failed to generate creative prompt",
            "details": str(e)
        }), 500

@creative_bp.route('/content/comfort', methods=['POST'])
async def create_comfort_story():
    """Create a comfort story for emotional support"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        comfort_params = data.get('comfort_params', {})
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        comfort_result = await content_generation.create_comfort_story(user_id, comfort_params)
        
        return jsonify({
            "status": "success",
            "comfort_story": comfort_result,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to create comfort story: {e}")
        return jsonify({
            "error": "Failed to create comfort story",
            "details": str(e)
        }), 500

@creative_bp.route('/content/history/<user_id>', methods=['GET'])
async def get_content_history(user_id):
    """Get user's creative content history"""
    try:
        content_type = request.args.get('content_type')
        days = int(request.args.get('days', 30))
        
        if content_type:
            content_type_enum = ContentType(content_type)
            history = await content_generation.get_user_content_history(user_id, content_type_enum, days)
        else:
            history = await content_generation.get_user_content_history(user_id, None, days)
        
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "content_history": history,
            "count": len(history),
            "period_days": days,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to get content history: {e}")
        return jsonify({
            "error": "Failed to get content history",
            "details": str(e)
        }), 500

# Emotional Creativity Endpoints
@creative_bp.route('/emotional/respond', methods=['POST'])
async def create_emotional_response():
    """Create content responsive to user's emotional state"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        emotional_context = data.get('emotional_context', {})
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        response_result = await emotional_creativity.create_emotional_response_content(user_id, emotional_context)
        
        return jsonify({
            "status": "success",
            "emotional_response": response_result,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to create emotional response: {e}")
        return jsonify({
            "error": "Failed to create emotional response",
            "details": str(e)
        }), 500

@creative_bp.route('/emotional/comfort', methods=['POST'])
async def generate_emotional_comfort():
    """Generate comfort content for emotional support"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        comfort_needs = data.get('comfort_needs', {})
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        comfort_result = await emotional_creativity.generate_comfort_creation(user_id, comfort_needs)
        
        return jsonify({
            "status": "success",
            "comfort_content": comfort_result,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to generate emotional comfort: {e}")
        return jsonify({
            "error": "Failed to generate emotional comfort",
            "details": str(e)
        }), 500

@creative_bp.route('/emotional/celebration', methods=['POST'])
async def create_celebration_content():
    """Create celebratory content for positive emotions"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        celebration_context = data.get('celebration_context', {})
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        celebration_result = await emotional_creativity.create_celebration_content(user_id, celebration_context)
        
        return jsonify({
            "status": "success",
            "celebration_content": celebration_result,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to create celebration content: {e}")
        return jsonify({
            "error": "Failed to create celebration content",
            "details": str(e)
        }), 500

@creative_bp.route('/emotional/processing-prompt', methods=['POST'])
async def generate_processing_prompt():
    """Generate a prompt for emotional processing"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        processing_needs = data.get('processing_needs', {})
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        prompt_result = await emotional_creativity.generate_processing_prompt(user_id, processing_needs)
        
        return jsonify({
            "status": "success",
            "processing_prompt": prompt_result,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to generate processing prompt: {e}")
        return jsonify({
            "error": "Failed to generate processing prompt",
            "details": str(e)
        }), 500

@creative_bp.route('/emotional/healing-metaphor', methods=['POST'])
async def create_healing_metaphor():
    """Create a healing metaphor for emotional growth"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        healing_context = data.get('healing_context', {})
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        metaphor_result = await emotional_creativity.create_healing_metaphor(user_id, healing_context)
        
        return jsonify({
            "status": "success",
            "healing_metaphor": metaphor_result,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to create healing metaphor: {e}")
        return jsonify({
            "error": "Failed to create healing metaphor",
            "details": str(e)
        }), 500

# Personality Evolution Endpoints
@creative_bp.route('/personality/profile/<user_id>', methods=['GET'])
async def get_personality_profile(user_id):
    """Get user's current personality profile"""
    try:
        personality = await personality_evolution.get_user_personality(user_id)
        
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "personality_profile": personality,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to get personality profile: {e}")
        return jsonify({
            "error": "Failed to get personality profile",
            "details": str(e)
        }), 500

@creative_bp.route('/personality/adjust', methods=['POST'])
async def adjust_personality_trait():
    """Manually adjust a personality trait"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        trait = data.get('trait')
        direction = data.get('direction')
        intensity = data.get('intensity', 0.1)
        
        if not all([user_id, trait, direction]):
            return jsonify({
                "error": "user_id, trait, and direction are required"
            }), 400
        
        trait_enum = PersonalityTrait(trait)
        direction_enum = EvolutionDirection(direction)
        
        success = await personality_evolution.adjust_trait(user_id, trait_enum, direction_enum, intensity)
        
        if success:
            return jsonify({
                "status": "success",
                "message": f"Personality trait {trait} adjusted",
                "adjustment": {
                    "trait": trait,
                    "direction": direction,
                    "intensity": intensity
                },
                "timestamp": datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "error": "Failed to adjust personality trait"
            }), 400
        
    except Exception as e:
        logger.error(f"❌ Failed to adjust personality trait: {e}")
        return jsonify({
            "error": "Failed to adjust personality trait",
            "details": str(e)
        }), 500

@creative_bp.route('/personality/record-feedback', methods=['POST'])
async def record_personality_feedback():
    """Record user interaction feedback for personality learning"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        interaction_data = data.get('interaction_data', {})
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        success = await personality_evolution.record_interaction_feedback(user_id, interaction_data)
        
        if success:
            return jsonify({
                "status": "success",
                "message": "Interaction feedback recorded",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "error": "Failed to record interaction feedback"
            }), 400
        
    except Exception as e:
        logger.error(f"❌ Failed to record personality feedback: {e}")
        return jsonify({
            "error": "Failed to record personality feedback",
            "details": str(e)
        }), 500

@creative_bp.route('/personality/summary/<user_id>', methods=['GET'])
async def get_personality_summary(user_id):
    """Get comprehensive personality summary"""
    try:
        summary = await personality_evolution.generate_personality_summary(user_id)
        
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "personality_summary": summary,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to get personality summary: {e}")
        return jsonify({
            "error": "Failed to get personality summary",
            "details": str(e)
        }), 500

# Collaborative Projects
@creative_bp.route('/project/create', methods=['POST'])
async def create_collaborative_project():
    """Create a new collaborative creative project"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        project_params = data.get('project_params', {})
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        project_result = await creative_evolution.create_collaborative_project(user_id, project_params)
        
        return jsonify({
            "status": "success",
            "collaborative_project": project_result,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to create collaborative project: {e}")
        return jsonify({
            "error": "Failed to create collaborative project",
            "details": str(e)
        }), 500

@creative_bp.route('/project/continue', methods=['POST'])
async def continue_collaborative_project():
    """Continue a collaborative project with user contribution"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        project_id = data.get('project_id')
        user_contribution = data.get('user_contribution', {})
        
        if not all([user_id, project_id]):
            return jsonify({
                "error": "user_id and project_id are required"
            }), 400
        
        continuation_result = await creative_evolution.continue_collaborative_project(
            user_id, project_id, user_contribution
        )
        
        return jsonify({
            "status": "success",
            "project_continuation": continuation_result,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to continue collaborative project: {e}")
        return jsonify({
            "error": "Failed to continue collaborative project",
            "details": str(e)
        }), 500

# Development Assessment
@creative_bp.route('/assessment/<user_id>', methods=['GET'])
async def assess_creative_development(user_id):
    """Assess user's creative development and evolution progress"""
    try:
        assessment = await creative_evolution.assess_creative_development(user_id)
        
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "creative_assessment": assessment,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to assess creative development: {e}")
        return jsonify({
            "error": "Failed to assess creative development",
            "details": str(e)
        }), 500

# Configuration and Preferences
@creative_bp.route('/preferences/<user_id>', methods=['GET', 'POST'])
async def manage_creative_preferences(user_id):
    """Get or set user's creative preferences"""
    try:
        if request.method == 'GET':
            # Return available options and current preferences
            return jsonify({
                "status": "success",
                "available_options": {
                    "evolution_modes": [mode.value for mode in CreativeEvolutionMode],
                    "content_types": [content_type.value for content_type in ContentType],
                    "creative_styles": [style.value for style in CreativeStyle],
                    "emotional_states": [state.value for state in EmotionalState],
                    "personality_traits": [trait.value for trait in PersonalityTrait]
                },
                "current_preferences": {
                    "evolution_mode": "moderate",
                    "autonomous_frequency": "moderate",
                    "preferred_content_types": ["story", "poem"],
                    "therapeutic_focus": False
                },
                "timestamp": datetime.now().isoformat()
            }), 200
        
        else:  # POST
            data = request.get_json()
            preferences = data.get('preferences', {})
            
            # Set creative preferences
            success = await content_generation.set_user_creative_preferences(user_id, preferences)
            
            if success:
                return jsonify({
                    "status": "success",
                    "message": "Creative preferences updated",
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat()
                }), 200
            else:
                return jsonify({
                    "error": "Failed to update creative preferences"
                }), 400
            
    except Exception as e:
        logger.error(f"❌ Failed to manage creative preferences: {e}")
        return jsonify({
            "error": "Failed to manage creative preferences",
            "details": str(e)
        }), 500

@creative_bp.route('/health', methods=['GET'])
def creative_evolution_health():
    """Health check for creative evolution system"""
    try:
        return jsonify({
            "status": "healthy",
            "system": "creative_evolution",
            "modules": {
                "creative_orchestrator": "operational",
                "personality_evolution": "operational",
                "content_generation": "operational",
                "emotional_creativity": "operational"
            },
            "capabilities": {
                "autonomous_generation": True,
                "personality_evolution": True,
                "collaborative_projects": True,
                "emotional_responsiveness": True
            },
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Creative evolution health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# Error handlers
@creative_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        "error": "Bad request",
        "message": "Invalid request parameters"
    }), 400

@creative_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not found",
        "message": "Requested resource not found"
    }), 404

@creative_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500

# Register blueprint function
def register_creative_routes(app):
    """Register creative evolution routes with Flask app"""
    app.register_blueprint(creative_bp)
    logger.info("🎨 Creative Evolution API routes registered")

__all__ = ["creative_bp", "register_creative_routes"]
