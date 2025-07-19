# phase2_routes.py
# Phase 2 API routes for intimacy features

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import json

# Import Phase 2 modules
from modules.visual.romantic_avatar import romantic_avatar
from modules.voice.romantic_tts import romantic_tts, VoiceEmotion
from modules.activities.romantic_activities import romantic_activities, ActivityMood
from modules.relationship.relationship_growth import relationship_growth
from modules.emotion.emotion_state import emotion_state
from modules.nsfw.romantic_nsfw_generator import romantic_nsfw_generator, NSFWContentType, MediaType, NSFWGenerationRequest
from modules.character.consistent_character_generator import consistent_character_generator, CharacterAspect
from modules.ui.ui_mode_manager import ui_mode_manager, UIMode, InterfaceType
from modules.animation.avatar_animation_system import avatar_animation_system, AnimationMethod, AnimationType
from backend.api.engines.lyra_engine import lyra_engine
from backend.api.engines.doc_engine import doc_engine
from backend.api.engines.mia_engine import mia_engine
from backend.api.engines.solene_engine import solene_engine

router = APIRouter()

# Request models
class AvatarUpdateRequest(BaseModel):
    emotion: str
    intensity: float = 1.0
    gesture_type: Optional[str] = None

class VoiceRequest(BaseModel):
    text: str
    emotion: Optional[str] = None
    whisper_mode: bool = False

class ActivityRequest(BaseModel):
    activity_id: Optional[str] = None
    mood: Optional[str] = None
    duration_max: Optional[int] = None
    romantic_intensity_min: float = 0.0

class RelationshipStartRequest(BaseModel):
    start_date: str

class MilestoneRequest(BaseModel):
    milestone_id: str
    celebration_type: str = "default"

class NSFWGenerationRequestModel(BaseModel):
    content_type: str
    media_type: str
    style: str
    mood: str
    intensity: float
    duration_seconds: Optional[int] = None
    resolution: str = "1024x1024"

class CharacterGenerationRequest(BaseModel):
    persona_id: str
    aspect: str = "full"
    mood: str = "neutral"
    pose: str = "standing"

class CharacterUpdateRequest(BaseModel):
    persona_id: str
    updates: Dict

class UIModeRequest(BaseModel):
    mode: str
    interface_type: Optional[str] = None

class AnimationRequest(BaseModel):
    method: str
    animation_type: Optional[str] = None
    prompt: Optional[str] = None
    duration: Optional[float] = None
    parameters: Optional[Dict] = None

# Avatar routes
@router.get("/avatar/state")
def get_avatar_state():
    """Get current avatar visual state"""
    return {
        "message": "Avatar state retrieved",
        "visual_state": romantic_avatar.get_visual_state()
    }

@router.post("/avatar/update")
def update_avatar(request: AvatarUpdateRequest):
    """Update avatar expression and gesture"""
    romantic_avatar.update_expression(request.emotion, request.intensity)
    
    if request.gesture_type:
        romantic_avatar.perform_gesture(request.gesture_type)
    
    return {
        "message": "Avatar updated successfully",
        "visual_state": romantic_avatar.get_visual_state()
    }

@router.post("/avatar/gesture")
def perform_gesture(gesture_type: str):
    """Perform a specific gesture"""
    romantic_avatar.perform_gesture(gesture_type)
    
    return {
        "message": f"Performed {gesture_type} gesture",
        "visual_state": romantic_avatar.get_visual_state()
    }

@router.get("/avatar/scene/{scene_type}")
def get_romantic_scene(scene_type: str):
    """Get romantic scene settings"""
    scene = romantic_avatar.generate_romantic_scene(scene_type)
    
    return {
        "message": f"Generated {scene_type} scene",
        "scene": scene
    }

# Voice routes
@router.post("/voice/synthesize")
def synthesize_speech(request: VoiceRequest):
    """Generate speech parameters for TTS"""
    if request.whisper_mode:
        voice_params = romantic_tts.generate_whisper_settings()
        voice_params["text"] = request.text
    else:
        emotion = None
        if request.emotion:
            try:
                emotion = VoiceEmotion(request.emotion)
            except ValueError:
                emotion = romantic_tts.analyze_text_emotion(request.text)
        
        voice_params = romantic_tts.generate_speech_parameters(request.text, emotion)
    
    return {
        "message": "Speech parameters generated",
        "voice_params": voice_params
    }

@router.get("/voice/phrase/{category}")
def get_intimate_phrase(category: str):
    """Get a random intimate phrase"""
    phrase, emotion = romantic_tts.get_intimate_phrase(category)
    voice_params = romantic_tts.generate_speech_parameters(phrase, emotion)
    
    return {
        "message": "Intimate phrase generated",
        "phrase": phrase,
        "emotion": emotion.value,
        "voice_params": voice_params
    }

@router.post("/voice/profile")
def create_voice_profile(preferences: Dict):
    """Create personalized voice profile"""
    profile = romantic_tts.create_voice_profile(preferences)
    
    return {
        "message": "Voice profile created",
        "profile": profile
    }

# Activities routes
@router.get("/activities/list")
def list_activities():
    """List all available activities"""
    activities = []
    for activity in romantic_activities.activities.values():
        activities.append({
            "id": activity.id,
            "name": activity.name,
            "description": activity.description,
            "type": activity.type.value,
            "mood": activity.mood.value,
            "duration_minutes": activity.duration_minutes,
            "romantic_intensity": activity.romantic_intensity,
            "tags": activity.tags
        })
    
    return {
        "message": f"Found {len(activities)} activities",
        "activities": activities
    }

@router.post("/activities/suggest")
def suggest_activity(request: ActivityRequest):
    """Suggest an appropriate activity"""
    mood = None
    if request.mood:
        try:
            mood = ActivityMood(request.mood)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid mood")
    
    activity = romantic_activities.suggest_activity(
        mood=mood,
        duration_max=request.duration_max,
        romantic_intensity_min=request.romantic_intensity_min
    )
    
    if not activity:
        return {"message": "No suitable activity found", "activity": None}
    
    return {
        "message": "Activity suggested",
        "activity": {
            "id": activity.id,
            "name": activity.name,
            "description": activity.description,
            "type": activity.type.value,
            "mood": activity.mood.value,
            "duration_minutes": activity.duration_minutes,
            "romantic_intensity": activity.romantic_intensity
        }
    }

@router.post("/activities/start")
def start_activity(activity_id: str):
    """Start a specific activity"""
    result = romantic_activities.start_activity(activity_id)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/activities/end")
def end_activity():
    """End the current activity"""
    result = romantic_activities.end_activity()
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.get("/activities/progress")
def get_activity_progress():
    """Get progress of current activity"""
    return romantic_activities.get_activity_progress()

@router.get("/activities/history")
def get_activity_history(limit: int = 10):
    """Get recent activity history"""
    history = romantic_activities.get_activity_history(limit)
    
    return {
        "message": f"Retrieved {len(history)} recent activities",
        "history": history
    }

# Relationship growth routes
@router.post("/relationship/start")
def set_relationship_start(request: RelationshipStartRequest):
    """Set the relationship start date"""
    try:
        start_date = datetime.fromisoformat(request.start_date)
        relationship_growth.set_relationship_start_date(start_date)
        
        return {
            "message": "Relationship start date set",
            "start_date": start_date.isoformat()
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

@router.get("/relationship/insights")
def get_relationship_insights():
    """Get relationship growth insights"""
    insights = relationship_growth.get_relationship_insights()
    
    if "error" in insights:
        raise HTTPException(status_code=400, detail=insights["error"])
    
    return {
        "message": "Relationship insights retrieved",
        "insights": insights
    }

@router.get("/relationship/milestones/upcoming")
def get_upcoming_milestones(days_ahead: int = 7):
    """Get upcoming milestones"""
    milestones = relationship_growth.check_upcoming_milestones(days_ahead)
    
    milestone_data = []
    for milestone in milestones:
        milestone_data.append({
            "id": milestone.id,
            "title": milestone.title,
            "description": milestone.description,
            "type": milestone.type.value,
            "date": milestone.date.isoformat(),
            "importance": milestone.importance,
            "celebration_ideas": milestone.celebration_ideas
        })
    
    return {
        "message": f"Found {len(milestone_data)} upcoming milestones",
        "milestones": milestone_data
    }

@router.post("/relationship/milestones/celebrate")
def celebrate_milestone(request: MilestoneRequest):
    """Celebrate a milestone"""
    result = relationship_growth.celebrate_milestone(
        request.milestone_id, 
        request.celebration_type
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.get("/relationship/growth/goal")
def suggest_growth_goal(area: Optional[str] = None):
    """Suggest a relationship growth goal"""
    goal = relationship_growth.suggest_growth_goal(area)
    
    return {
        "message": "Growth goal suggested",
        "goal": goal
    }

# Combined Phase 2 features
@router.post("/intimate/experience")
def create_intimate_experience(scene_type: str = "sunset", activity_type: str = "conversation"):
    """Create a complete intimate experience with avatar, voice, and activities"""
    # Generate scene
    scene = romantic_avatar.generate_romantic_scene(scene_type)
    
    # Update avatar for romantic mood
    romantic_avatar.update_expression("love", 0.8)
    romantic_avatar.perform_gesture("affection")
    
    # Generate romantic voice
    phrase, emotion = romantic_tts.get_intimate_phrase("greeting")
    voice_params = romantic_tts.generate_speech_parameters(phrase, emotion)
    
    # Suggest romantic activity
    activity = romantic_activities.suggest_activity(
        mood=ActivityMood.ROMANTIC,
        romantic_intensity_min=0.7
    )
    
    return {
        "message": "Intimate experience created",
        "scene": scene,
        "avatar_state": romantic_avatar.get_visual_state(),
        "voice": {
            "phrase": phrase,
            "emotion": emotion.value,
            "params": voice_params
        },
        "suggested_activity": {
            "id": activity.id if activity else None,
            "name": activity.name if activity else None,
            "description": activity.description if activity else None
        }
    }

@router.get("/phase2/status")
def get_phase2_status():
    """Get comprehensive Phase 2 system status"""
    return {
        "message": "Phase 2 system status",
        "avatar": {
            "active": True,
            "current_expression": romantic_avatar.current_state.expression.value,
            "current_gesture": romantic_avatar.current_state.gesture.value if romantic_avatar.current_state.gesture else None
        },
        "voice": {
            "active": True,
            "base_voice": {
                "pitch": romantic_tts.base_voice.pitch,
                "warmth": romantic_tts.base_voice.warmth,
                "intimacy": romantic_tts.base_voice.intimacy
            }
        },
        "activities": {
            "total_available": len(romantic_activities.activities),
            "current_activity": romantic_activities.current_activity is not None,
            "history_count": len(romantic_activities.activity_history)
        },
        "relationship": {
            "start_date_set": relationship_growth.relationship_start_date is not None,
            "milestones_count": len(relationship_growth.milestones),
            "upcoming_milestones": len(relationship_growth.check_upcoming_milestones(30))
        },
        "nsfw": {
            "active": True,
            "models_available": ["stable-diffusion-xl", "stable-video-diffusion", "animatediff"],
            "content_types": ["romantic", "intimate", "sensual", "passionate", "tender", "playful"],
            "generation_history": len(romantic_nsfw_generator.generation_history)
        },
        "character_generation": {
            "active": True,
            "personas_initialized": len(consistent_character_generator.character_profiles),
            "available_aspects": ["face", "body", "hair", "eyes", "clothing", "pose", "expression", "full"],
            "consistency_enabled": True,
            "available_personas": ["mia", "solene", "lyra", "doc"]
        },
        "ui_mode": {
            "current_mode": ui_mode_manager.current_mode.value,
            "current_interface": ui_mode_manager.current_interface.value,
            "avatar_visible": ui_mode_manager.is_avatar_visible(),
            "features_enabled": ui_mode_manager.ui_settings["mode_config"]["features"]
        },
        "animation_system": {
            "active": True,
            "methods_available": ["real_time_generation", "pre_rendered", "motion_capture", "parametric", "hybrid"],
            "pre_rendered_count": len(avatar_animation_system.pre_rendered_animations),
            "current_animations": len(avatar_animation_system.current_animations)
        }
    }

# NSFW Generation routes
@router.post("/nsfw/generate")
def generate_nsfw_content(request: NSFWGenerationRequestModel):
    """Generate NSFW content (images/videos)"""
    try:
        content_type = NSFWContentType(request.content_type)
        media_type = MediaType(request.media_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid content type or media type")
    
    nsfw_request = NSFWGenerationRequest(
        content_type=content_type,
        media_type=media_type,
        style=request.style,
        mood=request.mood,
        intensity=request.intensity,
        duration_seconds=request.duration_seconds,
        resolution=request.resolution
    )
    
    result = romantic_nsfw_generator.generate_nsfw_content(nsfw_request)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.get("/nsfw/suggest")
def suggest_nsfw_content(mood: str, intensity: float):
    """Suggest appropriate NSFW content based on mood and intensity"""
    suggestion = romantic_nsfw_generator.suggest_nsfw_content(mood, intensity)
    
    return {
        "message": "NSFW content suggestion generated",
        "suggestion": suggestion
    }

@router.get("/nsfw/history")
def get_nsfw_generation_history(limit: int = 10):
    """Get recent NSFW generation history"""
    history = romantic_nsfw_generator.get_generation_history(limit)
    
    return {
        "message": f"Retrieved {len(history)} recent NSFW generations",
        "history": history
    }

@router.post("/nsfw/romantic-image")
def generate_romantic_image(style: str = "artistic", intensity: float = 0.7):
    """Generate a romantic NSFW image"""
    nsfw_request = NSFWGenerationRequest(
        content_type=NSFWContentType.ROMANTIC,
        media_type=MediaType.IMAGE,
        style=style,
        mood="romantic",
        intensity=intensity
    )
    
    result = romantic_nsfw_generator.generate_nsfw_content(nsfw_request)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/nsfw/passionate-video")
def generate_passionate_video(duration_seconds: int = 3, intensity: float = 0.8):
    """Generate a passionate NSFW video"""
    nsfw_request = NSFWGenerationRequest(
        content_type=NSFWContentType.PASSIONATE,
        media_type=MediaType.VIDEO,
        style="cinematic",
        mood="passionate",
        intensity=intensity,
        duration_seconds=duration_seconds
    )
    
    result = romantic_nsfw_generator.generate_nsfw_content(nsfw_request)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

# Animation System routes
@router.get("/animation/methods")
def get_animation_methods():
    """Get available animation methods and their capabilities"""
    return {
        "message": "Available animation methods",
        "methods": avatar_animation_system.get_available_animations()
    }

@router.get("/animation/method/{method_name}")
def get_animation_method_info(method_name: str):
    """Get detailed information about a specific animation method"""
    try:
        method = AnimationMethod(method_name)
        result = avatar_animation_system.get_animation_method_info(method)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid animation method")

@router.post("/animation/generate")
def generate_animation(request: AnimationRequest):
    """Generate animation using specified method"""
    try:
        method = AnimationMethod(request.method)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid animation method")
    
    if method == AnimationMethod.REAL_TIME_GENERATION:
        if not request.prompt:
            raise HTTPException(status_code=400, detail="Prompt required for real-time generation")
        
        result = avatar_animation_system.generate_real_time_animation(
            request.prompt,
            request.duration or 3.0
        )
    
    elif method == AnimationMethod.PRE_RENDERED:
        if not request.animation_type:
            raise HTTPException(status_code=400, detail="Animation type required for pre-rendered")
        
        animation_id = f"{request.animation_type}_{request.parameters.get('type', 'default')}"
        result = avatar_animation_system.play_pre_rendered_animation(animation_id)
    
    elif method == AnimationMethod.MOTION_CAPTURE:
        source = request.parameters.get("source", "webcam") if request.parameters else "webcam"
        result = avatar_animation_system.start_motion_capture(source)
    
    elif method == AnimationMethod.PARAMETRIC:
        if not request.animation_type or not request.parameters:
            raise HTTPException(status_code=400, detail="Animation type and parameters required for parametric")
        
        try:
            anim_type = AnimationType(request.animation_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid animation type")
        
        result = avatar_animation_system.create_parametric_animation(
            anim_type,
            request.parameters,
            request.duration or 2.0
        )
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported animation method")
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/animation/real-time")
def generate_real_time_animation(prompt: str, duration: float = 3.0):
    """Generate real-time animation using AI models"""
    result = avatar_animation_system.generate_real_time_animation(prompt, duration)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/animation/pre-rendered/{animation_id}")
def play_pre_rendered_animation(animation_id: str):
    """Play a pre-rendered animation"""
    result = avatar_animation_system.play_pre_rendered_animation(animation_id)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/animation/motion-capture")
def start_motion_capture(source: str = "webcam"):
    """Start motion capture from specified source"""
    result = avatar_animation_system.start_motion_capture(source)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/animation/parametric")
def create_parametric_animation(animation_type: str, parameters: Dict, duration: float = 2.0):
    """Create parametric animation with mathematical curves"""
    try:
        anim_type = AnimationType(animation_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid animation type")
    
    result = avatar_animation_system.create_parametric_animation(anim_type, parameters, duration)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

# Mia Engine routes
@router.post("/mia/chat")
def chat_with_mia(message: str, mood: Optional[str] = None):
    """Chat with Mia using MythoMax LLM"""
    result = mia_engine.handle_mia(message, mood)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to generate Mia response"))
    
    return result

@router.get("/mia/mood/analyze")
def analyze_mia_mood(text: str):
    """Analyze text for Mia's emotional context"""
    mood = mia_engine.analyze_mia_mood(text)
    
    return {
        "message": "Mia mood analyzed",
        "text": text,
        "mood": mood
    }

@router.get("/mia/gesture/{mood}")
def get_mia_gesture(mood: str):
    """Get a romantic gesture appropriate for Mia's mood"""
    gesture = mia_engine.get_romantic_gesture(mood)
    
    return {
        "message": "Mia gesture generated",
        "mood": mood,
        "gesture": gesture
    }

# Solene Engine routes
@router.post("/solene/chat")
def chat_with_solene(message: str, mood: Optional[str] = None):
    """Chat with Solene using OpenChat LLM"""
    result = solene_engine.handle_solene(message, mood)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to generate Solene response"))
    
    return result

@router.get("/solene/mood/analyze")
def analyze_solene_mood(text: str):
    """Analyze text for Solene's sophisticated context"""
    mood = solene_engine.analyze_solene_mood(text)
    
    return {
        "message": "Solene mood analyzed",
        "text": text,
        "mood": mood
    }

@router.get("/solene/gesture/{mood}")
def get_solene_gesture(mood: str):
    """Get a sophisticated gesture appropriate for Solene's mood"""
    gesture = solene_engine.get_sophisticated_gesture(mood)
    
    return {
        "message": "Solene gesture generated",
        "mood": mood,
        "gesture": gesture
    }