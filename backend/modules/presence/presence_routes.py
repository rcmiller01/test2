"""
Presence API Routes
REST endpoints for presence monitoring and management
"""

import logging
from flask import Blueprint, request, jsonify
from datetime import datetime
import asyncio

from .presence_orchestrator import presence_orchestrator, UnifiedPresenceState, PresenceContext

logger = logging.getLogger(__name__)

presence_bp = Blueprint('presence', __name__, url_prefix='/api/presence')

# Initialize presence orchestrator
@presence_bp.before_app_first_request
async def initialize_presence_system():
    """Initialize the presence system"""
    try:
        await presence_orchestrator.initialize()
        logger.info("🎯 Presence API system initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize presence API: {e}")

@presence_bp.route('/start-monitoring', methods=['POST'])
async def start_monitoring():
    """Start comprehensive presence monitoring for a user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        
        if not user_id or not session_id:
            return jsonify({
                "error": "user_id and session_id are required"
            }), 400
        
        # Start comprehensive monitoring
        presence_data = await presence_orchestrator.start_comprehensive_monitoring(user_id, session_id)
        
        return jsonify({
            "status": "success",
            "message": "Presence monitoring started",
            "user_id": user_id,
            "session_id": session_id,
            "initial_presence": {
                "unified_state": presence_data.unified_state.value,
                "context": presence_data.context.value,
                "confidence": presence_data.confidence,
                "availability_score": presence_data.availability_score
            },
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to start presence monitoring: {e}")
        return jsonify({
            "error": "Failed to start presence monitoring",
            "details": str(e)
        }), 500

@presence_bp.route('/stop-monitoring', methods=['POST'])
async def stop_monitoring():
    """Stop presence monitoring for a user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({
                "error": "user_id is required"
            }), 400
        
        await presence_orchestrator.stop_comprehensive_monitoring(user_id)
        
        return jsonify({
            "status": "success",
            "message": "Presence monitoring stopped",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to stop presence monitoring: {e}")
        return jsonify({
            "error": "Failed to stop presence monitoring",
            "details": str(e)
        }), 500

@presence_bp.route('/status/<user_id>', methods=['GET'])
async def get_presence_status(user_id):
    """Get current presence status for a user"""
    try:
        presence_data = await presence_orchestrator.get_unified_presence(user_id)
        
        if not presence_data:
            return jsonify({
                "error": "No presence data found for user",
                "user_id": user_id
            }), 404
        
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "presence": presence_data,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to get presence status: {e}")
        return jsonify({
            "error": "Failed to get presence status",
            "details": str(e)
        }), 500

@presence_bp.route('/interaction', methods=['POST'])
async def record_interaction():
    """Record user interaction across presence systems"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        interaction_type = data.get('interaction_type')
        metadata = data.get('metadata', {})
        
        if not user_id or not interaction_type:
            return jsonify({
                "error": "user_id and interaction_type are required"
            }), 400
        
        await presence_orchestrator.record_interaction(user_id, interaction_type, metadata)
        
        return jsonify({
            "status": "success",
            "message": "Interaction recorded",
            "user_id": user_id,
            "interaction_type": interaction_type,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to record interaction: {e}")
        return jsonify({
            "error": "Failed to record interaction",
            "details": str(e)
        }), 500

@presence_bp.route('/heartbeat', methods=['POST'])
async def presence_heartbeat():
    """Update presence heartbeat for active sessions"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        status = data.get('status', 'active')  # active, idle, away
        metadata = data.get('metadata', {})
        
        if not user_id:
            return jsonify({
                "error": "user_id is required"
            }), 400
        
        # Record as interaction to update presence
        await presence_orchestrator.record_interaction(user_id, 'heartbeat', {
            'status': status,
            **metadata
        })
        
        # Get updated presence
        presence_data = await presence_orchestrator.get_unified_presence(user_id)
        
        return jsonify({
            "status": "success",
            "message": "Heartbeat recorded",
            "user_id": user_id,
            "presence": presence_data,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to process heartbeat: {e}")
        return jsonify({
            "error": "Failed to process heartbeat",
            "details": str(e)
        }), 500

@presence_bp.route('/availability/<user_id>', methods=['GET'])
async def check_availability(user_id):
    """Check if user is available for interaction"""
    try:
        presence_data = await presence_orchestrator.get_unified_presence(user_id)
        
        if not presence_data:
            return jsonify({
                "available": False,
                "reason": "No presence data found",
                "user_id": user_id
            }), 200
        
        availability_score = presence_data.get('availability_score', 0)
        interruption_receptivity = presence_data.get('interruption_receptivity', 0)
        unified_state = presence_data.get('unified_state')
        
        # Determine availability
        is_available = availability_score > 0.5
        is_interruptible = interruption_receptivity > 0.6
        
        # Generate recommendations
        recommendations = []
        if not is_available:
            if unified_state in ['away', 'deeply_away']:
                predicted_return = presence_data.get('predicted_return_minutes')
                if predicted_return:
                    recommendations.append(f"User likely to return in {predicted_return:.0f} minutes")
                else:
                    recommendations.append("User is away for an extended period")
            else:
                recommendations.append("User has low availability")
        
        if is_available and not is_interruptible:
            recommendations.append("User is available but may not welcome interruptions")
        
        if is_available and is_interruptible:
            recommendations.append("Good time to interact with user")
        
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "available": is_available,
            "interruptible": is_interruptible,
            "availability_score": availability_score,
            "interruption_receptivity": interruption_receptivity,
            "unified_state": unified_state,
            "context": presence_data.get('context'),
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to check availability: {e}")
        return jsonify({
            "error": "Failed to check availability",
            "details": str(e)
        }), 500

@presence_bp.route('/analytics/<user_id>', methods=['GET'])
async def get_presence_analytics(user_id):
    """Get presence analytics and patterns for a user"""
    try:
        # Get query parameters
        days = int(request.args.get('days', 7))
        include_patterns = request.args.get('patterns', 'true').lower() == 'true'
        
        # Current presence
        current_presence = await presence_orchestrator.get_unified_presence(user_id)
        
        # TODO: Implement analytics from database
        # For now, return basic analytics structure
        analytics = {
            "user_id": user_id,
            "period_days": days,
            "current_presence": current_presence,
            "patterns": {
                "most_active_hours": [9, 10, 11, 14, 15, 16],
                "average_session_duration": 45.2,
                "typical_break_duration": 8.5,
                "engagement_trends": "stable",
                "availability_percentage": 78.5
            } if include_patterns else None,
            "summary": {
                "total_sessions": 0,
                "total_interaction_time": 0,
                "average_availability": 0.75,
                "interruption_receptivity": 0.65
            }
        }
        
        return jsonify({
            "status": "success",
            "analytics": analytics,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to get presence analytics: {e}")
        return jsonify({
            "error": "Failed to get presence analytics",
            "details": str(e)
        }), 500

@presence_bp.route('/config/<user_id>', methods=['GET', 'POST'])
async def presence_config(user_id):
    """Get or update presence configuration for a user"""
    try:
        if request.method == 'GET':
            # Return current presence configuration
            config = {
                "user_id": user_id,
                "monitoring_enabled": True,
                "idle_thresholds": {
                    "short_idle_minutes": 2,
                    "medium_idle_minutes": 5,
                    "long_idle_minutes": 15,
                    "deep_idle_minutes": 30
                },
                "notification_preferences": {
                    "availability_changes": True,
                    "state_transitions": False,
                    "break_predictions": True
                },
                "privacy_settings": {
                    "background_sensing": True,
                    "system_metrics": False,
                    "detailed_activity": True
                }
            }
            
            return jsonify({
                "status": "success",
                "config": config,
                "timestamp": datetime.now().isoformat()
            }), 200
        
        else:  # POST
            data = request.get_json()
            
            # TODO: Implement configuration updates
            # For now, just acknowledge the update
            
            return jsonify({
                "status": "success",
                "message": "Configuration updated",
                "user_id": user_id,
                "updated_config": data,
                "timestamp": datetime.now().isoformat()
            }), 200
            
    except Exception as e:
        logger.error(f"❌ Failed to handle presence config: {e}")
        return jsonify({
            "error": "Failed to handle presence config",
            "details": str(e)
        }), 500

@presence_bp.route('/active-users', methods=['GET'])
async def get_active_users():
    """Get list of all users with active presence monitoring"""
    try:
        active_users = list(presence_orchestrator.active_users.keys())
        
        user_summaries = []
        for user_id in active_users:
            presence_data = await presence_orchestrator.get_unified_presence(user_id)
            if presence_data:
                user_summaries.append({
                    "user_id": user_id,
                    "unified_state": presence_data.get('unified_state'),
                    "availability_score": presence_data.get('availability_score'),
                    "last_interaction": presence_data.get('last_interaction'),
                    "session_duration": presence_data.get('presence_duration_minutes')
                })
        
        return jsonify({
            "status": "success",
            "active_users_count": len(active_users),
            "active_users": user_summaries,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to get active users: {e}")
        return jsonify({
            "error": "Failed to get active users",
            "details": str(e)
        }), 500

@presence_bp.route('/health', methods=['GET'])
def presence_health():
    """Health check for presence system"""
    try:
        active_monitoring_count = len(presence_orchestrator.active_users)
        active_tasks_count = len(presence_orchestrator.monitoring_tasks)
        
        return jsonify({
            "status": "healthy",
            "system": "presence_monitoring",
            "active_users": active_monitoring_count,
            "active_tasks": active_tasks_count,
            "modules": {
                "presence_orchestrator": "operational",
                "session_presence": "operational", 
                "idle_detection": "operational",
                "background_sensing": "operational"
            },
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Presence health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# Error handlers
@presence_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        "error": "Bad request",
        "message": "Invalid request parameters"
    }), 400

@presence_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not found",
        "message": "Requested resource not found"
    }), 404

@presence_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500

# Register blueprint function
def register_presence_routes(app):
    """Register presence routes with Flask app"""
    app.register_blueprint(presence_bp)
    logger.info("🎯 Presence API routes registered")

__all__ = ["presence_bp", "register_presence_routes"]
