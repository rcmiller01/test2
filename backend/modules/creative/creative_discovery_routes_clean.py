"""
Creative Discovery API Routes - Clean Version
Handles dynamic creative model integration and personalized content generation
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from typing import Dict, List, Optional

creative_discovery_bp = Blueprint('creative_discovery', __name__, url_prefix='/api/creative-discovery')

# Global instances (will be initialized by main app)
_creative_discovery = None
_discovery_integration = None

def init_creative_discovery_routes(creative_discovery_engine, discovery_integration_system):
    """Initialize the routes with the discovery systems"""
    global _creative_discovery, _discovery_integration
    _creative_discovery = creative_discovery_engine
    _discovery_integration = discovery_integration_system

@creative_discovery_bp.route('/analyze-conversation', methods=['POST'])
def analyze_conversation():
    """Analyze conversation for creative interests"""
    try:
        if not _creative_discovery:
            return jsonify({'error': 'Creative discovery system not initialized'}), 500
            
        data = request.get_json()
        user_id = data.get('user_id')
        conversation_text = data.get('conversation_text')
        conversation_context = data.get('context', {})
        
        if not user_id or not conversation_text:
            return jsonify({'error': 'user_id and conversation_text are required'}), 400
        
        # Note: This would need to be async in real implementation
        # For now, return a placeholder response
        return jsonify({
            'user_id': user_id,
            'message': 'Conversation analysis initiated',
            'analysis_timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@creative_discovery_bp.route('/user-profile/<user_id>', methods=['GET'])
def get_user_creative_profile(user_id):
    """Get user's complete creative profile"""
    try:
        if not _creative_discovery:
            return jsonify({'error': 'Creative discovery system not initialized'}), 500
            
        # Placeholder response for now
        profile = {
            'user_id': user_id,
            'creative_interests': [],
            'message': 'Profile retrieval initiated'
        }
        return jsonify(profile)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@creative_discovery_bp.route('/suggest-activities/<user_id>', methods=['GET'])
def suggest_creative_activities(user_id):
    """Suggest creative activities based on user preferences"""
    try:
        if not _discovery_integration:
            return jsonify({'error': 'Discovery integration system not initialized'}), 500
            
        # Placeholder suggestions
        suggestions = [
            {
                'activity': 'Explore music creation',
                'description': 'Discover your musical preferences and create together',
                'media_type': 'music'
            },
            {
                'activity': 'Visual art collaboration', 
                'description': 'Express yourself through digital or traditional art',
                'media_type': 'visual_art'
            }
        ]
        
        return jsonify({
            'user_id': user_id,
            'suggestions': suggestions,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@creative_discovery_bp.route('/available-models', methods=['GET'])
def get_available_models():
    """Get all available creative AI models"""
    try:
        media_type_filter = request.args.get('media_type')
        
        # Sample model data
        sample_models = {
            'music': [
                {
                    'model_id': 'musicgen_small',
                    'name': 'MusicGen Small',
                    'media_type': 'music',
                    'quality_level': 'basic',
                    'cost_per_use': 0.0,
                    'capabilities': ['melody_generation', 'accompaniment'],
                    'is_installed': False,
                    'local_model': True,
                    'api_based': False
                }
            ],
            'visual_art': [
                {
                    'model_id': 'stable_diffusion',
                    'name': 'Stable Diffusion',
                    'media_type': 'visual_art',
                    'quality_level': 'professional',
                    'cost_per_use': 0.0,
                    'capabilities': ['image_generation', 'style_transfer'],
                    'is_installed': False,
                    'local_model': True,
                    'api_based': False
                }
            ],
            'cooking': [
                {
                    'model_id': 'recipe_generator',
                    'name': 'Recipe Generator',
                    'media_type': 'cooking',
                    'quality_level': 'basic',
                    'cost_per_use': 0.0,
                    'capabilities': ['recipe_creation', 'ingredient_substitution'],
                    'is_installed': False,
                    'local_model': True,
                    'api_based': False
                }
            ]
        }
        
        if media_type_filter:
            filtered_models = {media_type_filter: sample_models.get(media_type_filter, [])}
        else:
            filtered_models = sample_models
        
        return jsonify({
            'available_models': filtered_models,
            'total_models': sum(len(models) for models in filtered_models.values())
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@creative_discovery_bp.route('/install-model', methods=['POST'])
def install_model():
    """Install a creative AI model"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        model_id = data.get('model_id')
        
        if not user_id or not model_id:
            return jsonify({'error': 'user_id and model_id are required'}), 400
        
        # Simulate model installation
        return jsonify({
            'message': f'Model installation initiated for {model_id}',
            'model_id': model_id,
            'user_id': user_id,
            'status': 'installing',
            'timestamp': datetime.now().isoformat()
        })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@creative_discovery_bp.route('/create-content', methods=['POST'])
def create_personalized_content():
    """Create personalized creative content"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        media_type = data.get('media_type')
        creative_prompt = data.get('prompt', '')
        
        if not user_id or not media_type:
            return jsonify({'error': 'user_id and media_type are required'}), 400
        
        # Sample content generation response
        sample_content = {
            'type': media_type,
            'model_used': f'{media_type}_generator',
            'prompt': creative_prompt,
            'description': f'Personalized {media_type} content created for you',
            'file_path': f'generated/{media_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'user_preferences': 'detected_from_conversation'
            }
        }
        
        return jsonify({
            'user_id': user_id,
            'generated_content': sample_content,
            'creation_timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@creative_discovery_bp.route('/creative-interests/<user_id>', methods=['GET'])
def get_user_creative_interests(user_id):
    """Get user's discovered creative interests"""
    try:
        # Sample interests data
        sample_interests = [
            {
                'media_type': 'music',
                'confidence_score': 0.8,
                'specific_interests': ['jazz', 'piano'],
                'skill_level': 'intermediate',
                'emotional_connection': 0.9,
                'frequency_mentioned': 5,
                'last_mentioned': datetime.now().isoformat(),
                'examples_shared': ['Miles Davis', 'Bill Evans']
            },
            {
                'media_type': 'visual_art',
                'confidence_score': 0.6,
                'specific_interests': ['watercolor', 'landscapes'],
                'skill_level': 'beginner',
                'emotional_connection': 0.7,
                'frequency_mentioned': 3,
                'last_mentioned': datetime.now().isoformat(),
                'examples_shared': ['nature photography', 'sunset paintings']
            }
        ]
        
        return jsonify({
            'user_id': user_id,
            'creative_interests': sample_interests,
            'total_interests': len(sample_interests)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@creative_discovery_bp.route('/process-conversation', methods=['POST'])
def process_conversation_for_creativity():
    """Process conversation through creative discovery integration"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        conversation_data = data.get('conversation_data')
        
        if not user_id or not conversation_data:
            return jsonify({'error': 'user_id and conversation_data are required'}), 400
        
        # Simulate processing
        detected_interests = {
            'music': {'confidence': 0.7, 'keywords': ['song', 'melody']},
            'visual_art': {'confidence': 0.4, 'keywords': ['colors', 'painting']}
        }
        
        return jsonify({
            'user_id': user_id,
            'detected_interests': detected_interests,
            'enhanced_persona': True,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@creative_discovery_bp.route('/model-installation-status', methods=['GET'])
def get_model_installation_status():
    """Get installation status of all models"""
    try:
        # Sample status data
        status = {
            'music': {
                'total_models': 2,
                'installed_models': 0,
                'models': [
                    {'model_id': 'musicgen_small', 'name': 'MusicGen Small', 'installed': False},
                    {'model_id': 'mubert_api', 'name': 'Mubert AI', 'installed': False}
                ]
            },
            'visual_art': {
                'total_models': 2,
                'installed_models': 0,
                'models': [
                    {'model_id': 'stable_diffusion', 'name': 'Stable Diffusion', 'installed': False},
                    {'model_id': 'midjourney_api', 'name': 'Midjourney', 'installed': False}
                ]
            }
        }
        
        return jsonify({
            'installation_status': status,
            'total_installed': 0,
            'total_available': 4
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@creative_discovery_bp.route('/collaboration-history/<user_id>', methods=['GET'])
def get_collaboration_history(user_id):
    """Get user's creative collaboration history"""
    try:
        # Sample collaboration history
        history = {
            'user_id': user_id,
            'total_collaborations': 12,
            'collaborations_by_type': {
                'music': 5,
                'visual_art': 4,
                'cooking': 2,
                'poetry': 1
            },
            'recent_creations': [
                {
                    'type': 'music',
                    'title': 'Jazz Improvisation in Dm',
                    'created_at': datetime.now().isoformat(),
                    'user_satisfaction': 4.5
                },
                {
                    'type': 'visual_art',
                    'title': 'Sunset Over Mountains',
                    'created_at': datetime.now().isoformat(),
                    'user_satisfaction': 4.2
                }
            ],
            'favorite_styles': ['jazz', 'impressionist', 'mediterranean'],
            'skill_progression': {
                'music': 'intermediate',
                'visual_art': 'beginner'
            }
        }
        
        return jsonify(history)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@creative_discovery_bp.route('/discovery-analytics', methods=['GET'])
def get_discovery_analytics():
    """Get analytics about creative discovery across all users"""
    try:
        # Sample analytics data
        analytics = {
            'total_users_with_interests': 150,
            'most_popular_interests': {
                'music': 45,
                'visual_art': 38,
                'cooking': 32,
                'poetry': 20,
                'photography': 15
            },
            'model_usage_stats': {
                'musicgen_small': 120,
                'stable_diffusion': 95,
                'recipe_generator': 78
            },
            'content_generation_stats': {
                'total_pieces_created': 2847,
                'average_user_satisfaction': 4.3,
                'most_popular_styles': ['jazz', 'impressionist', 'mediterranean']
            },
            'discovery_trends': {
                'weekly_new_interests': 12,
                'interest_retention_rate': 0.85
            }
        }
        
        return jsonify(analytics)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Error handlers
@creative_discovery_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@creative_discovery_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Health check
@creative_discovery_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'creative_discovery',
        'timestamp': datetime.now().isoformat(),
        'features': [
            'conversation_analysis',
            'dynamic_model_installation',
            'personalized_content_generation',
            'creative_interest_discovery',
            'collaborative_recommendations'
        ],
        'initialized': _creative_discovery is not None and _discovery_integration is not None
    })
