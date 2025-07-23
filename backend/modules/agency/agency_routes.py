"""
Narrative Agency API Routes
REST endpoints for proactive character interactions and agency management
"""

import logging
from flask import Blueprint, request, jsonify
from datetime import datetime, time
import asyncio

from .agency_orchestrator import narrative_agency, DeliveryChannel
from .proactive_triggers import proactive_triggers, TriggerType, TriggerPriority, InteractionTone
from .sms_integration import sms_integration, SMSType
from .scheduled_interactions import scheduled_interactions, ScheduleType, RecurrencePattern
from .emotional_prompts import emotional_prompts, EmotionalTrigger, InterventionType

logger = logging.getLogger(__name__)

agency_bp = Blueprint('agency', __name__, url_prefix='/api/agency')

# Initialize agency system
@agency_bp.before_app_first_request
async def initialize_agency_system():
    """Initialize the narrative agency system"""
    try:
        await narrative_agency.initialize()
        logger.info("🎭 Narrative Agency API system initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize agency API: {e}")

@agency_bp.route('/start', methods=['POST'])
async def start_user_agency():
    """Start narrative agency for a user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        preferences = data.get('preferences', {})
        
        if not user_id or not session_id:
            return jsonify({
                "error": "user_id and session_id are required"
            }), 400
        
        # Start comprehensive agency
        agency_data = await narrative_agency.start_user_agency(user_id, session_id, preferences)
        
        return jsonify({
            "status": "success",
            "message": "Narrative agency started",
            "agency_data": agency_data,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to start user agency: {e}")
        return jsonify({
            "error": "Failed to start narrative agency",
            "details": str(e)
        }), 500

@agency_bp.route('/stop', methods=['POST'])
async def stop_user_agency():
    """Stop narrative agency for a user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({
                "error": "user_id is required"
            }), 400
        
        await narrative_agency.stop_user_agency(user_id)
        
        return jsonify({
            "status": "success",
            "message": "Narrative agency stopped",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to stop user agency: {e}")
        return jsonify({
            "error": "Failed to stop narrative agency",
            "details": str(e)
        }), 500

@agency_bp.route('/status/<user_id>', methods=['GET'])
async def get_agency_status(user_id):
    """Get agency status for a user"""
    try:
        status = await narrative_agency.get_user_agency_status(user_id)
        
        if not status:
            return jsonify({
                "error": "No active agency found for user",
                "user_id": user_id
            }), 404
        
        return jsonify({
            "status": "success",
            "agency_status": status,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to get agency status: {e}")
        return jsonify({
            "error": "Failed to get agency status",
            "details": str(e)
        }), 500

@agency_bp.route('/interaction', methods=['POST'])
async def record_user_interaction():
    """Record user interaction with emotional context"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        interaction_type = data.get('interaction_type')
        emotional_data = data.get('emotional_data')
        
        if not user_id or not interaction_type:
            return jsonify({
                "error": "user_id and interaction_type are required"
            }), 400
        
        await narrative_agency.record_user_interaction(user_id, interaction_type, emotional_data)
        
        return jsonify({
            "status": "success",
            "message": "User interaction recorded",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to record user interaction: {e}")
        return jsonify({
            "error": "Failed to record user interaction",
            "details": str(e)
        }), 500

# Proactive Triggers Management
@agency_bp.route('/triggers/evaluate/<user_id>', methods=['POST'])
async def evaluate_triggers():
    """Manually evaluate triggers for a user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({
                "error": "user_id is required"
            }), 400
        
        trigger_events = await proactive_triggers.evaluate_triggers_for_user(user_id)
        
        events_data = [
            {
                "event_id": event.event_id,
                "trigger_type": event.trigger.trigger_type.value,
                "priority": event.trigger.priority.value,
                "tone": event.trigger.tone.value,
                "content": event.generated_content,
                "confidence": event.confidence,
                "delivery_method": event.delivery_method
            }
            for event in trigger_events
        ]
        
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "trigger_events": events_data,
            "count": len(events_data),
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to evaluate triggers: {e}")
        return jsonify({
            "error": "Failed to evaluate triggers",
            "details": str(e)
        }), 500

@agency_bp.route('/triggers/preferences', methods=['GET', 'POST'])
async def manage_trigger_preferences():
    """Get or update trigger preferences for a user"""
    try:
        if request.method == 'GET':
            user_id = request.args.get('user_id')
            if not user_id:
                return jsonify({"error": "user_id is required"}), 400
            
            # Return available trigger types and current preferences
            available_types = [trigger_type.value for trigger_type in TriggerType]
            priorities = [priority.value for priority in TriggerPriority]
            tones = [tone.value for tone in InteractionTone]
            
            return jsonify({
                "status": "success",
                "available_trigger_types": available_types,
                "available_priorities": priorities,
                "available_tones": tones,
                "current_preferences": {
                    "enabled_types": available_types,  # Default: all enabled
                    "frequency": "normal",
                    "preferred_tone": "caring"
                },
                "timestamp": datetime.now().isoformat()
            }), 200
        
        else:  # POST
            data = request.get_json()
            user_id = data.get('user_id')
            trigger_type = data.get('trigger_type')
            preferences = data.get('preferences', {})
            
            if not user_id or not trigger_type:
                return jsonify({
                    "error": "user_id and trigger_type are required"
                }), 400
            
            await proactive_triggers.update_user_trigger_preferences(user_id, trigger_type, preferences)
            
            return jsonify({
                "status": "success",
                "message": "Trigger preferences updated",
                "user_id": user_id,
                "trigger_type": trigger_type,
                "timestamp": datetime.now().isoformat()
            }), 200
            
    except Exception as e:
        logger.error(f"❌ Failed to manage trigger preferences: {e}")
        return jsonify({
            "error": "Failed to manage trigger preferences",
            "details": str(e)
        }), 500

# SMS Integration
@agency_bp.route('/sms/send', methods=['POST'])
async def send_proactive_sms():
    """Send proactive SMS to user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        content = data.get('content')
        sms_type = data.get('sms_type', SMSType.PROACTIVE_CHECKIN.value)
        priority = data.get('priority', 'normal')
        
        if not user_id or not content:
            return jsonify({
                "error": "user_id and content are required"
            }), 400
        
        if not sms_integration.enabled:
            return jsonify({
                "error": "SMS integration is not enabled"
            }), 503
        
        message_id = await sms_integration.send_proactive_sms(
            user_id=user_id,
            content=content,
            sms_type=SMSType(sms_type),
            priority=priority
        )
        
        if message_id:
            return jsonify({
                "status": "success",
                "message": "SMS sent successfully",
                "message_id": message_id,
                "timestamp": datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "error": "Failed to send SMS",
                "details": "Check SMS configuration and user preferences"
            }), 400
        
    except Exception as e:
        logger.error(f"❌ Failed to send proactive SMS: {e}")
        return jsonify({
            "error": "Failed to send SMS",
            "details": str(e)
        }), 500

@agency_bp.route('/sms/preferences', methods=['GET', 'POST'])
async def manage_sms_preferences():
    """Get or update SMS preferences for a user"""
    try:
        if request.method == 'GET':
            user_id = request.args.get('user_id')
            if not user_id:
                return jsonify({"error": "user_id is required"}), 400
            
            # Return SMS configuration options
            return jsonify({
                "status": "success",
                "sms_enabled": sms_integration.enabled,
                "available_types": [sms_type.value for sms_type in SMSType],
                "default_preferences": {
                    "enabled": False,
                    "phone_number": "",
                    "allowed_types": [SMSType.PROACTIVE_CHECKIN.value, SMSType.CARING_MESSAGE.value],
                    "quiet_hours_start": "22:00",
                    "quiet_hours_end": "08:00",
                    "max_daily_messages": 3
                },
                "timestamp": datetime.now().isoformat()
            }), 200
        
        else:  # POST
            data = request.get_json()
            user_id = data.get('user_id')
            phone_number = data.get('phone_number')
            enabled = data.get('enabled', True)
            allowed_types = data.get('allowed_types', [])
            quiet_hours_start = data.get('quiet_hours_start')
            quiet_hours_end = data.get('quiet_hours_end')
            max_daily_messages = data.get('max_daily_messages', 3)
            
            if not user_id:
                return jsonify({"error": "user_id is required"}), 400
            
            await sms_integration.set_user_sms_preferences(
                user_id=user_id,
                phone_number=phone_number,
                enabled=enabled,
                allowed_types=allowed_types,
                quiet_hours_start=quiet_hours_start,
                quiet_hours_end=quiet_hours_end,
                max_daily_messages=max_daily_messages
            )
            
            return jsonify({
                "status": "success",
                "message": "SMS preferences updated",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }), 200
            
    except Exception as e:
        logger.error(f"❌ Failed to manage SMS preferences: {e}")
        return jsonify({
            "error": "Failed to manage SMS preferences",
            "details": str(e)
        }), 500

@agency_bp.route('/sms/history/<user_id>', methods=['GET'])
async def get_sms_history(user_id):
    """Get SMS history for user"""
    try:
        days = int(request.args.get('days', 30))
        
        history = await sms_integration.get_sms_history(user_id, days)
        
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "history": history,
            "count": len(history),
            "period_days": days,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to get SMS history: {e}")
        return jsonify({
            "error": "Failed to get SMS history",
            "details": str(e)
        }), 500

# Scheduled Interactions
@agency_bp.route('/schedule/create', methods=['POST'])
async def create_scheduled_interaction():
    """Create a new scheduled interaction"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        schedule_type = data.get('schedule_type')
        title = data.get('title')
        content_template = data.get('content_template')
        recurrence = data.get('recurrence')
        execution_time = data.get('execution_time')  # HH:MM format
        days_of_week = data.get('days_of_week', [])  # For weekly recurrence
        day_of_month = data.get('day_of_month')  # For monthly recurrence
        description = data.get('description')
        
        if not all([user_id, schedule_type, title, content_template, recurrence, execution_time]):
            return jsonify({
                "error": "Missing required fields: user_id, schedule_type, title, content_template, recurrence, execution_time"
            }), 400
        
        # Parse execution time
        exec_time = time.fromisoformat(execution_time)
        
        schedule_id = await scheduled_interactions.create_scheduled_interaction(
            user_id=user_id,
            schedule_type=ScheduleType(schedule_type),
            title=title,
            content_template=content_template,
            recurrence=RecurrencePattern(recurrence),
            execution_time=exec_time,
            days_of_week=days_of_week,
            day_of_month=day_of_month,
            description=description
        )
        
        return jsonify({
            "status": "success",
            "message": "Scheduled interaction created",
            "schedule_id": schedule_id,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to create scheduled interaction: {e}")
        return jsonify({
            "error": "Failed to create scheduled interaction",
            "details": str(e)
        }), 500

@agency_bp.route('/schedule/list/<user_id>', methods=['GET'])
async def list_user_schedules(user_id):
    """List all scheduled interactions for a user"""
    try:
        schedules = await scheduled_interactions.get_user_schedules(user_id)
        
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "schedules": schedules,
            "count": len(schedules),
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to list user schedules: {e}")
        return jsonify({
            "error": "Failed to list user schedules",
            "details": str(e)
        }), 500

@agency_bp.route('/schedule/toggle', methods=['POST'])
async def toggle_schedule():
    """Enable or disable a scheduled interaction"""
    try:
        data = request.get_json()
        schedule_id = data.get('schedule_id')
        enabled = data.get('enabled')
        
        if schedule_id is None or enabled is None:
            return jsonify({
                "error": "schedule_id and enabled are required"
            }), 400
        
        await scheduled_interactions.update_schedule_status(schedule_id, enabled)
        
        return jsonify({
            "status": "success",
            "message": f"Schedule {'enabled' if enabled else 'disabled'}",
            "schedule_id": schedule_id,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to toggle schedule: {e}")
        return jsonify({
            "error": "Failed to toggle schedule",
            "details": str(e)
        }), 500

# Emotional Prompts
@agency_bp.route('/emotional/record', methods=['POST'])
async def record_emotional_data():
    """Record emotional data for analysis"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        emotion_type = data.get('emotion_type')
        intensity = data.get('intensity')
        context = data.get('context', {})
        
        if not user_id or not emotion_type or intensity is None:
            return jsonify({
                "error": "user_id, emotion_type, and intensity are required"
            }), 400
        
        if not (0.0 <= intensity <= 1.0):
            return jsonify({
                "error": "intensity must be between 0.0 and 1.0"
            }), 400
        
        await emotional_prompts.record_emotional_data(user_id, emotion_type, intensity, context)
        
        return jsonify({
            "status": "success",
            "message": "Emotional data recorded",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to record emotional data: {e}")
        return jsonify({
            "error": "Failed to record emotional data",
            "details": str(e)
        }), 500

@agency_bp.route('/emotional/triggers', methods=['GET'])
def get_emotional_triggers():
    """Get available emotional triggers and intervention types"""
    try:
        return jsonify({
            "status": "success",
            "emotional_triggers": [trigger.value for trigger in EmotionalTrigger],
            "intervention_types": [intervention.value for intervention in InterventionType],
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to get emotional triggers: {e}")
        return jsonify({
            "error": "Failed to get emotional triggers",
            "details": str(e)
        }), 500

# Analytics and Reporting
@agency_bp.route('/analytics/<user_id>', methods=['GET'])
async def get_agency_analytics(user_id):
    """Get agency analytics for a user"""
    try:
        days = int(request.args.get('days', 7))
        
        # Get analytics from various systems
        analytics = {
            "user_id": user_id,
            "period_days": days,
            "summary": {
                "total_proactive_events": 0,
                "sms_messages_sent": 0,
                "scheduled_interactions": 0,
                "emotional_interventions": 0
            },
            "engagement_metrics": {
                "response_rate": 0.75,  # Placeholder
                "average_response_time": "5 minutes",  # Placeholder
                "user_satisfaction": 0.85  # Placeholder
            },
            "preferences": {
                "most_effective_channel": "in_app_message",
                "preferred_interaction_tone": "caring",
                "optimal_timing": "morning"
            }
        }
        
        return jsonify({
            "status": "success",
            "analytics": analytics,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to get agency analytics: {e}")
        return jsonify({
            "error": "Failed to get agency analytics",
            "details": str(e)
        }), 500

@agency_bp.route('/health', methods=['GET'])
def agency_health():
    """Health check for agency system"""
    try:
        return jsonify({
            "status": "healthy",
            "system": "narrative_agency",
            "modules": {
                "agency_orchestrator": "operational",
                "proactive_triggers": "operational",
                "sms_integration": "operational" if sms_integration.enabled else "disabled",
                "scheduled_interactions": "operational",
                "emotional_prompts": "operational"
            },
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Agency health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# Error handlers
@agency_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        "error": "Bad request",
        "message": "Invalid request parameters"
    }), 400

@agency_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not found",
        "message": "Requested resource not found"
    }), 404

@agency_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500

# Register blueprint function
def register_agency_routes(app):
    """Register agency routes with Flask app"""
    app.register_blueprint(agency_bp)
    logger.info("🎭 Narrative Agency API routes registered")

__all__ = ["agency_bp", "register_agency_routes"]
