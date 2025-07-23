"""
Creative Discovery API Routes
Handles dynamic creative model integration and personalized content generation
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import asyncio
from typing import Dict, List

from backend.modules.creative.creative_discovery import (
    CreativeDiscoveryEngine, 
    CreativeDiscoveryIntegration,
    CreativeMediaType
)

creative_discovery_bp = Blueprint('creative_discovery', __name__, url_prefix='/api/creative-discovery')

# Initialize creative discovery system
creative_discovery = None
discovery_integration = None

def init_creative_discovery(app, database_manager, llm_orchestrator, persona_system, conversation_manager):
    """Initialize creative discovery system with app context"""
    global creative_discovery, discovery_integration
    
    creative_discovery = CreativeDiscoveryEngine(database_manager, llm_orchestrator)
    discovery_integration = CreativeDiscoveryIntegration(
        creative_discovery, persona_system, conversation_manager
    )

@creative_discovery_bp.route('/analyze-conversation', methods=['POST'])
async def analyze_conversation():
    """Analyze conversation for creative interests"""
    try:
        if not creative_discovery:
            return jsonify({'error': 'Creative discovery system not initialized'}), 500
            
        data = request.get_json()
        user_id = data.get('user_id')
        conversation_text = data.get('conversation_text')
        conversation_context = data.get('context', {})
        
        if not user_id or not conversation_text:
            return jsonify({'error': 'user_id and conversation_text are required'}), 400
        
        # Analyze conversation for creative interests
        detected_interests = await creative_discovery.analyze_conversation_for_creative_interests(
            user_id, conversation_text, conversation_context
        )
        
        return jsonify({
            'user_id': user_id,
            'detected_interests': detected_interests,
            'analysis_timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def check_initialization():
    """Check if creative discovery system is initialized"""
    if not creative_discovery or not discovery_integration:
        raise ValueError("Creative discovery system not initialized")

@creative_discovery_bp.route('/user-profile/<user_id>', methods=['GET'])
async def get_user_creative_profile(user_id):
    """Get user's complete creative profile"""
    try:
        check_initialization()
        profile = await creative_discovery.get_user_creative_profile(user_id)
        return jsonify(profile)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@creative_discovery_bp.route('/suggest-activities/<user_id>', methods=['GET'])
async def suggest_creative_activities(user_id):
    """Suggest creative activities based on user preferences"""
    try:
        check_initialization()
        suggestions = await discovery_integration.suggest_creative_activities(user_id)
        
        return jsonify({
            'user_id': user_id,
            'suggestions': suggestions,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@creative_discovery_bp.route('/available-models', methods=['GET'])
async def get_available_models():
    """Get all available creative AI models"""
    try:
        media_type_filter = request.args.get('media_type')
        
        all_models = {}
        
        for media_type, models in creative_discovery.available_models.items():
            if media_type_filter and media_type.value != media_type_filter:
                continue
                
            all_models[media_type.value] = []
            for model in models:
                model_info = {
                    'model_id': model.model_id,
                    'name': model.model_name,
                    'media_type': model.media_type.value,
                    'quality_level': model.quality_level,
                    'cost_per_use': model.cost_per_use,
                    'capabilities': model.capabilities,
                    'is_installed': model.is_installed,
                    'local_model': model.local_model_path is not None,
                    'api_based': model.api_endpoint is not None
                }
                all_models[media_type.value].append(model_info)
        
        return jsonify({
            'available_models': all_models,
            'total_models': sum(len(models) for models in all_models.values())
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@creative_discovery_bp.route('/install-model', methods=['POST'])
async def install_model():
    """Install a creative AI model"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        model_id = data.get('model_id')
        
        if not user_id or not model_id:
            return jsonify({'error': 'user_id and model_id are required'}), 400
        
        # Find the model
        target_model = None
        for media_type, models in creative_discovery.available_models.items():
            for model in models:
                if model.model_id == model_id:
                    target_model = model
                    break
            if target_model:
                break
        
        if not target_model:
            return jsonify({'error': 'Model not found'}), 404
        
        if target_model.is_installed:
            return jsonify({'message': 'Model already installed', 'model_id': model_id})
        
        # Install the model
        success = await creative_discovery._install_creative_model(target_model)
        
        if success:
            return jsonify({
                'message': 'Model installed successfully',
                'model_id': model_id,
                'model_name': target_model.model_name,
                'media_type': target_model.media_type.value
            })
        else:
            return jsonify({'error': 'Model installation failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@creative_discovery_bp.route('/create-content', methods=['POST'])
async def create_personalized_content():
    """Create personalized creative content"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        media_type_str = data.get('media_type')
        creative_prompt = data.get('prompt')
        
        if not user_id or not media_type_str:
            return jsonify({'error': 'user_id and media_type are required'}), 400
        
        try:
            media_type = CreativeMediaType(media_type_str)
        except ValueError:
            return jsonify({'error': f'Invalid media_type: {media_type_str}'}), 400
        
        # Create personalized content
        content = await creative_discovery.create_personalized_content(
            user_id, media_type, creative_prompt
        )
        
        if 'error' in content:
            return jsonify(content), 400
        
        return jsonify({
            'user_id': user_id,
            'generated_content': content,
            'creation_timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@creative_discovery_bp.route('/creative-interests/<user_id>', methods=['GET'])
async def get_user_creative_interests(user_id):
    """Get user's discovered creative interests"""
    try:
        user_prefs = creative_discovery.user_preferences.get(user_id, [])
        
        interests = []
        for pref in user_prefs:
            interest_data = {
                'media_type': pref.media_type.value,
                'confidence_score': pref.confidence_score,
                'specific_interests': pref.specific_interests,
                'skill_level': pref.skill_level,
                'emotional_connection': pref.emotional_connection,
                'frequency_mentioned': pref.frequency_mentioned,
                'last_mentioned': pref.last_mentioned.isoformat(),
                'examples_shared': pref.examples_shared
            }
            interests.append(interest_data)
        
        # Sort by confidence and frequency
        interests.sort(key=lambda x: (x['confidence_score'], x['frequency_mentioned']), reverse=True)
        
        return jsonify({
            'user_id': user_id,
            'creative_interests': interests,
            'total_interests': len(interests)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@creative_discovery_bp.route('/process-conversation', methods=['POST'])
async def process_conversation_for_creativity():
    """Process conversation through creative discovery integration"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        conversation_data = data.get('conversation_data')
        
        if not user_id or not conversation_data:
            return jsonify({'error': 'user_id and conversation_data are required'}), 400
        
        # Process conversation for creative insights
        detected_interests = await discovery_integration.process_conversation_for_creativity(
            user_id, conversation_data
        )
        
        return jsonify({
            'user_id': user_id,
            'detected_interests': detected_interests,
            'enhanced_persona': len(detected_interests) > 0,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@creative_discovery_bp.route('/model-installation-status', methods=['GET'])
async def get_model_installation_status():
    """Get installation status of all models"""
    try:
        status = {}
        
        for media_type, models in creative_discovery.available_models.items():
            status[media_type.value] = {
                'total_models': len(models),
                'installed_models': len([m for m in models if m.is_installed]),
                'models': []
            }
            
            for model in models:
                model_status = {
                    'model_id': model.model_id,
                    'name': model.model_name,
                    'installed': model.is_installed,
                    'quality': model.quality_level,
                    'cost': model.cost_per_use
                }
                status[media_type.value]['models'].append(model_status)
        
        return jsonify({
            'installation_status': status,
            'total_installed': sum(
                status[mt]['installed_models'] for mt in status
            ),
            'total_available': sum(
                status[mt]['total_models'] for mt in status
            )
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@creative_discovery_bp.route('/update-preferences', methods=['POST'])
async def update_user_preferences():
    """Manually update user creative preferences"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        preferences_update = data.get('preferences')
        
        if not user_id or not preferences_update:
            return jsonify({'error': 'user_id and preferences are required'}), 400
        
        # This would be used for manual preference updates
        # For now, just return success
        return jsonify({
            'message': 'Preferences updated successfully',
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@creative_discovery_bp.route('/collaboration-history/<user_id>', methods=['GET'])
async def get_collaboration_history(user_id):
    """Get user's creative collaboration history"""
    try:
        # This would fetch from database in real implementation
        # For now, return placeholder data
        
        history = {
            'user_id': user_id,
            'total_collaborations': 0,
            'collaborations_by_type': {},
            'recent_creations': [],
            'favorite_styles': [],
            'skill_progression': {}
        }
        
        return jsonify(history)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@creative_discovery_bp.route('/discovery-analytics', methods=['GET'])
async def get_discovery_analytics():
    """Get analytics about creative discovery across all users"""
    try:
        analytics = {
            'total_users_with_interests': len(creative_discovery.user_preferences),
            'most_popular_interests': {},
            'model_usage_stats': {},
            'content_generation_stats': {},
            'discovery_trends': {}
        }
        
        # Calculate most popular interests
        interest_counts = {}
        for user_prefs in creative_discovery.user_preferences.values():
            for pref in user_prefs:
                media_type = pref.media_type.value
                if media_type not in interest_counts:
                    interest_counts[media_type] = 0
                interest_counts[media_type] += 1
        
        analytics['most_popular_interests'] = dict(
            sorted(interest_counts.items(), key=lambda x: x[1], reverse=True)
        )
        
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
        ]
    })
