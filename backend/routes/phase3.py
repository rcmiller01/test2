# phase3.py
# Phase 3 API routes for advanced companionship features

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

# Import Phase 3 modules
from modules.input.haptic_system import get_haptic_system, trigger_haptic_feedback
from modules.input.biometric_sync import get_biometric_sync, start_biometric_monitoring, update_biometric_reading
from modules.visual.vr_integration import get_vr_integration, start_vr_session, trigger_vr_interaction
from modules.relationship.relationship_ai import get_relationship_ai, analyze_relationship_health, generate_relationship_advice

router = APIRouter(prefix="/api/phase3", tags=["Phase 3 - Advanced Companionship"])

# Pydantic models for API requests/responses
class HapticRequest(BaseModel):
    pattern: str
    intensity: str = "moderate"
    duration: float = 2.0
    location: str = "general"
    emotional_context: str = "neutral"

class BiometricReadingRequest(BaseModel):
    type: str
    value: float
    context: str = "general"

class VRSessionRequest(BaseModel):
    scene_type: str = "romantic_garden"
    user_position: Optional[List[float]] = None

class VRInteractionRequest(BaseModel):
    interaction_type: str
    intensity: float = 0.5

class RelationshipAdviceRequest(BaseModel):
    issue_type: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ConflictResolutionRequest(BaseModel):
    conflict_type: str
    severity: float
    context: Optional[Dict[str, Any]] = None

# Haptic Feedback Routes
@router.post("/haptic/trigger")
async def trigger_haptic_feedback_route(request: HapticRequest):
    """Trigger haptic feedback pattern"""
    try:
        success = trigger_haptic_feedback(
            pattern=request.pattern,
            intensity=request.intensity,
            duration=request.duration
        )
        
        return {
            "success": success,
            "pattern": request.pattern,
            "intensity": request.intensity,
            "duration": request.duration,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Haptic feedback error: {str(e)}")

@router.post("/haptic/emotional")
async def trigger_emotional_haptic(emotion: str, intensity: str = "moderate"):
    """Trigger haptic feedback based on emotion"""
    try:
        haptic_system = get_haptic_system()
        success = haptic_system.trigger_emotional_haptic(emotion)
        
        return {
            "success": success,
            "emotion": emotion,
            "intensity": intensity,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Emotional haptic error: {str(e)}")

@router.post("/haptic/romantic")
async def trigger_romantic_haptic(action: str, intensity: str = "moderate"):
    """Trigger romantic haptic feedback"""
    try:
        haptic_system = get_haptic_system()
        success = haptic_system.trigger_romantic_haptic(action, intensity)
        
        return {
            "success": success,
            "action": action,
            "intensity": intensity,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Romantic haptic error: {str(e)}")

@router.get("/haptic/status")
async def get_haptic_status():
    """Get haptic system status"""
    try:
        haptic_system = get_haptic_system()
        status = haptic_system.get_haptic_status()
        
        return {
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Haptic status error: {str(e)}")

# Biometric Sync Routes
@router.post("/biometric/start")
async def start_biometric_monitoring_route():
    """Start biometric monitoring"""
    try:
        success = start_biometric_monitoring()
        
        return {
            "success": success,
            "message": "Biometric monitoring started" if success else "Failed to start monitoring",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Biometric start error: {str(e)}")

@router.post("/biometric/reading")
async def update_biometric_reading_route(request: BiometricReadingRequest):
    """Update biometric reading from external device"""
    try:
        success = update_biometric_reading(
            type_name=request.type,
            value=request.value,
            context=request.context
        )
        
        return {
            "success": success,
            "reading_type": request.type,
            "value": request.value,
            "context": request.context,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Biometric reading error: {str(e)}")

@router.get("/biometric/status")
async def get_biometric_status():
    """Get biometric sync status"""
    try:
        biometric_sync = get_biometric_sync()
        status = biometric_sync.get_biometric_summary()
        
        return {
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Biometric status error: {str(e)}")

@router.get("/biometric/romantic-sync")
async def get_romantic_sync_status():
    """Get romantic synchronization status"""
    try:
        biometric_sync = get_biometric_sync()
        sync_status = biometric_sync.get_romantic_sync_status()
        
        return {
            "romantic_sync": sync_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Romantic sync error: {str(e)}")

# VR Integration Routes
@router.post("/vr/start")
async def start_vr_session_route(request: VRSessionRequest):
    """Start VR session with specified scene"""
    try:
        success = start_vr_session(request.scene_type)
        
        return {
            "success": success,
            "scene_type": request.scene_type,
            "message": f"VR session started in {request.scene_type}" if success else "Failed to start VR session",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VR start error: {str(e)}")

@router.post("/vr/interaction")
async def trigger_vr_interaction_route(request: VRInteractionRequest):
    """Trigger VR interaction"""
    try:
        success = trigger_vr_interaction(
            interaction_type=request.interaction_type,
            intensity=request.intensity
        )
        
        return {
            "success": success,
            "interaction_type": request.interaction_type,
            "intensity": request.intensity,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VR interaction error: {str(e)}")

@router.post("/vr/change-scene")
async def change_vr_scene(scene_type: str):
    """Change VR scene"""
    try:
        from modules.visual.vr_integration import change_vr_scene
        success = change_vr_scene(scene_type)
        
        return {
            "success": success,
            "new_scene": scene_type,
            "message": f"Changed to {scene_type}" if success else "Failed to change scene",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VR scene change error: {str(e)}")

@router.post("/vr/stop")
async def stop_vr_session_route():
    """Stop VR session"""
    try:
        from modules.visual.vr_integration import stop_vr_session
        stop_vr_session()
        
        return {
            "success": True,
            "message": "VR session stopped",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VR stop error: {str(e)}")

@router.get("/vr/status")
async def get_vr_status():
    """Get VR system status"""
    try:
        vr_integration = get_vr_integration()
        status = vr_integration.get_vr_status()
        
        return {
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VR status error: {str(e)}")

@router.get("/vr/scenes")
async def get_available_vr_scenes():
    """Get available VR scenes"""
    try:
        from modules.visual.vr_integration import VRSceneType
        scenes = [scene.value for scene in VRSceneType]
        
        return {
            "available_scenes": scenes,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VR scenes error: {str(e)}")

# Relationship AI Routes
@router.get("/relationship/health")
async def get_relationship_health():
    """Analyze relationship health"""
    try:
        health_analysis = analyze_relationship_health()
        
        return {
            "health_analysis": health_analysis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Relationship health error: {str(e)}")

@router.post("/relationship/advice")
async def get_relationship_advice_route(request: RelationshipAdviceRequest):
    """Generate relationship advice"""
    try:
        advice = generate_relationship_advice(request.issue_type)
        
        return {
            "advice": advice,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Relationship advice error: {str(e)}")

@router.post("/relationship/conflict-resolution")
async def get_conflict_resolution_route(request: ConflictResolutionRequest):
    """Get conflict resolution guidance"""
    try:
        from modules.relationship.relationship_ai import provide_conflict_resolution
        resolution = provide_conflict_resolution(
            conflict_type=request.conflict_type,
            severity=request.severity
        )
        
        return {
            "conflict_resolution": resolution,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conflict resolution error: {str(e)}")

@router.get("/relationship/insights")
async def get_relationship_insights():
    """Get comprehensive relationship insights"""
    try:
        insights = get_relationship_insights()
        
        return {
            "insights": insights,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Relationship insights error: {str(e)}")

@router.post("/relationship/track-progress")
async def track_relationship_progress(metric: str, value: float):
    """Track relationship progress"""
    try:
        relationship_ai = get_relationship_ai()
        relationship_ai.track_relationship_progress(metric, value)
        
        return {
            "success": True,
            "metric": metric,
            "value": value,
            "message": f"Tracked {metric} = {value}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Progress tracking error: {str(e)}")

# Combined Phase 3 Features
@router.post("/integrated/romantic-experience")
async def create_romantic_experience(
    scene_type: str = "romantic_garden",
    haptic_pattern: str = "heartbeat",
    biometric_context: str = "romantic"
):
    """Create an integrated romantic experience combining VR, haptic, and biometric features"""
    try:
        # Start VR session
        vr_success = start_vr_session(scene_type)
        
        # Trigger romantic haptic feedback
        haptic_success = trigger_haptic_feedback("heartbeat", "moderate", 5.0)
        
        # Start biometric monitoring if not already active
        biometric_sync = get_biometric_sync()
        if not biometric_sync.is_monitoring:
            biometric_success = start_biometric_monitoring()
        else:
            biometric_success = True
        
        return {
            "success": all([vr_success, haptic_success, biometric_success]),
            "vr_session": vr_success,
            "haptic_feedback": haptic_success,
            "biometric_monitoring": biometric_success,
            "scene_type": scene_type,
            "haptic_pattern": haptic_pattern,
            "message": "Romantic experience created successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Romantic experience error: {str(e)}")

@router.get("/integrated/status")
async def get_integrated_phase3_status():
    """Get comprehensive status of all Phase 3 features"""
    try:
        # Get status from all Phase 3 systems
        haptic_status = get_haptic_system().get_haptic_status()
        biometric_status = get_biometric_sync().get_biometric_summary()
        vr_status = get_vr_integration().get_vr_status()
        relationship_health = analyze_relationship_health()
        
        return {
            "haptic_system": haptic_status,
            "biometric_sync": biometric_status,
            "vr_integration": vr_status,
            "relationship_health": relationship_health,
            "overall_status": "active",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Integrated status error: {str(e)}")

# Health check for Phase 3 features
@router.get("/health")
async def phase3_health_check():
    """Health check for Phase 3 features"""
    try:
        # Check if all Phase 3 modules are accessible
        haptic_system = get_haptic_system()
        biometric_sync = get_biometric_sync()
        vr_integration = get_vr_integration()
        relationship_ai = get_relationship_ai()
        
        return {
            "status": "healthy",
            "features": {
                "haptic_system": "available",
                "biometric_sync": "available",
                "vr_integration": "available",
                "relationship_ai": "available"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        } 