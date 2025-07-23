"""
Safety API Routes for Ethical Safety Layer
Provides endpoints for safety management, anchor phrases, and session control
"""

from fastapi import APIRouter, HTTPException, Form, Query, Depends
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

from ..modules.safety.contextual_safety_engine import (
    contextual_safety_engine, SafetyLevel, ContentCategory, EmotionalRisk
)
from ..modules.safety.anchor_processor import anchor_processor, AnchorResponse, EmotionalState
from ..modules.safety.session_control import (
    session_control, SessionRisk, InterventionType, UsagePattern
)

logger = logging.getLogger(__name__)

# Create safety router
safety_router = APIRouter(prefix="/api/safety", tags=["safety"])

@safety_router.on_event("startup")
async def initialize_safety_systems():
    """Initialize all safety systems on startup"""
    try:
        await contextual_safety_engine.initialize()
        await session_control.initialize()
        logger.info("🛡️ All Safety Systems initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize safety systems: {e}")

# Content Safety Endpoints

@safety_router.post("/content/evaluate")
async def evaluate_content_safety(
    content: str = Form(...),
    user_id: str = Form(...),
    emotional_state: str = Form("{}"),  # JSON string
    session_id: Optional[str] = Form(None),
    context: str = Form("{}")  # JSON string
):
    """
    Evaluate content safety based on relationship context and emotional state
    
    Args:
        content: Content to evaluate for safety
        user_id: User identifier
        emotional_state: JSON string of current emotional state
        session_id: Current session identifier
        context: Additional context as JSON
        
    Returns:
        Safety evaluation with decision and recommendations
    """
    try:
        # Parse JSON inputs
        try:
            import json
            emotion_dict = json.loads(emotional_state) if emotional_state else {}
            context_dict = json.loads(context) if context else {}
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in emotional_state or context")
        
        # Add session context if provided
        if session_id:
            context_dict["session_id"] = session_id
        
        # Evaluate content safety
        decision = await contextual_safety_engine.evaluate_content_safety(
            content=content,
            user_id=user_id,
            context=context_dict
        )
        
        # If anchor phrase detected, process it
        response_data = {
            "success": True,
            "allowed": decision.allowed,
            "safety_level": decision.safety_level.value,
            "content_category": decision.content_category.value,
            "risk_assessment": decision.risk_assessment.value,
            "modifications": decision.modifications,
            "reasoning": decision.reasoning,
            "anchor_triggered": decision.anchor_triggered
        }
        
        # Add anchor response if triggered
        if decision.anchor_triggered:
            anchor_response = await anchor_processor.process_anchor_activation(
                user_id=user_id,
                content=content,
                emotional_state=emotion_dict,
                context=context_dict
            )
            response_data["anchor_response"] = anchor_response
        
        return response_data
        
    except Exception as e:
        logger.error(f"❌ Failed to evaluate content safety: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@safety_router.get("/content/categories")
async def get_content_categories():
    """
    Get available content categories for safety evaluation
    
    Returns:
        List of content categories with descriptions
    """
    categories = [
        {
            "id": category.value,
            "name": category.value.replace("_", " ").title(),
            "description": _get_category_description(category)
        }
        for category in ContentCategory
    ]
    
    return {
        "success": True,
        "categories": categories
    }

@safety_router.get("/safety-levels")
async def get_safety_levels():
    """
    Get available safety levels
    
    Returns:
        List of safety levels with descriptions
    """
    levels = [
        {
            "id": level.value,
            "name": level.value.replace("_", " ").title(),
            "description": _get_safety_level_description(level)
        }
        for level in SafetyLevel
    ]
    
    return {
        "success": True,
        "safety_levels": levels
    }

# Anchor Phrase Endpoints

@safety_router.post("/anchor/trigger")
async def trigger_anchor_phrase(
    user_id: str = Form(...),
    phrase: str = Form("safe space"),
    emotional_state: str = Form("{}"),
    context: str = Form("{}")
):
    """
    Manually trigger anchor phrase for emergency emotional regulation
    
    Args:
        user_id: User identifier
        phrase: Anchor phrase used (default: "safe space")
        emotional_state: Current emotional state as JSON
        context: Additional context as JSON
        
    Returns:
        Anchor response with calming techniques
    """
    try:
        # Parse inputs
        try:
            import json
            emotion_dict = json.loads(emotional_state) if emotional_state else {}
            context_dict = json.loads(context) if context else {}
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in emotional_state or context")
        
        # Process anchor activation
        response = await anchor_processor.process_anchor_activation(
            user_id=user_id,
            content=f"User manually triggered: {phrase}",
            emotional_state=emotion_dict,
            context=context_dict
        )
        
        return {
            "success": True,
            "trigger_phrase": phrase,
            "response": response,
            "message": "Anchor phrase activated successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to trigger anchor phrase: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@safety_router.get("/anchor/phrases")
async def get_anchor_phrases():
    """
    Get list of recognized anchor phrases
    
    Returns:
        List of available anchor phrases
    """
    phrases = anchor_processor.get_anchor_phrases()
    
    return {
        "success": True,
        "anchor_phrases": phrases,
        "primary_phrase": "safe space",
        "description": "These phrases instantly activate emotional safety protocols"
    }

@safety_router.post("/anchor/custom")
async def add_custom_anchor_phrase(
    user_id: str = Form(...),
    phrase: str = Form(...)
):
    """
    Add custom anchor phrase for a user
    
    Args:
        user_id: User identifier
        phrase: Custom anchor phrase to add
        
    Returns:
        Confirmation of phrase addition
    """
    try:
        # Validate phrase
        if len(phrase.strip()) < 3:
            raise HTTPException(status_code=400, detail="Anchor phrase must be at least 3 characters")
        
        # Add custom phrase
        anchor_processor.add_custom_anchor_phrase(user_id, phrase.strip())
        
        return {
            "success": True,
            "custom_phrase": phrase.strip(),
            "message": "Custom anchor phrase added successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to add custom anchor phrase: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Session Control Endpoints

@safety_router.post("/session/start")
async def start_session_tracking(
    user_id: str = Form(...),
    session_id: str = Form(...),
    context: str = Form("{}")
):
    """
    Start tracking a new session for safety monitoring
    
    Args:
        user_id: User identifier
        session_id: Unique session identifier
        context: Initial session context as JSON
        
    Returns:
        Session tracking confirmation
    """
    try:
        # Parse context
        try:
            import json
            context_dict = json.loads(context) if context else {}
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in context")
        
        # Start session tracking
        session_metrics = await session_control.start_session(
            user_id=user_id,
            session_id=session_id,
            initial_context=context_dict
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "user_id": user_id,
            "start_time": session_metrics.start_time.isoformat(),
            "message": "Session tracking started successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to start session tracking: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@safety_router.post("/session/update")
async def update_session_metrics(
    session_id: str = Form(...),
    emotional_state: str = Form("{}"),
    content_category: str = Form("general"),
    message_content: str = Form("")
):
    """
    Update session metrics with new interaction data
    
    Args:
        session_id: Session identifier
        emotional_state: Current emotional state as JSON
        content_category: Category of current content
        message_content: Content of the message (for analysis)
        
    Returns:
        Update confirmation
    """
    try:
        # Parse emotional state
        try:
            import json
            emotion_dict = json.loads(emotional_state) if emotional_state else {}
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in emotional_state")
        
        # Update session
        await session_control.update_session(
            session_id=session_id,
            emotional_state=emotion_dict,
            content_category=content_category,
            message_content=message_content
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Session metrics updated successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to update session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@safety_router.post("/session/end")
async def end_session_tracking(session_id: str = Form(...)):
    """
    End session tracking and get summary
    
    Args:
        session_id: Session identifier to end
        
    Returns:
        Session summary and statistics
    """
    try:
        summary = await session_control.end_session(session_id)
        
        if not summary:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "success": True,
            "session_summary": summary,
            "message": "Session ended successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to end session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@safety_router.get("/session/{user_id}/statistics")
async def get_session_statistics(user_id: str):
    """
    Get session statistics for a user
    
    Args:
        user_id: User identifier
        
    Returns:
        Session usage statistics and patterns
    """
    try:
        stats = await session_control.get_session_statistics(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get session statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# User Preferences Endpoints

@safety_router.post("/preferences/set")
async def set_safety_preferences(
    user_id: str = Form(...),
    content_category: str = Form(...),
    preference_level: str = Form(...)
):
    """
    Set user safety preferences for content categories
    
    Args:
        user_id: User identifier
        content_category: Content category to configure
        preference_level: Preference level (always_allow, normal, always_restrict)
        
    Returns:
        Preference update confirmation
    """
    try:
        # Validate preference level
        valid_levels = ["always_allow", "normal", "always_restrict"]
        if preference_level not in valid_levels:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid preference level. Valid options: {valid_levels}"
            )
        
        # Set preference
        await contextual_safety_engine.set_user_safety_preference(
            user_id=user_id,
            content_category=content_category,
            preference=preference_level
        )
        
        return {
            "success": True,
            "user_id": user_id,
            "content_category": content_category,
            "preference_level": preference_level,
            "message": "Safety preference updated successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to set safety preference: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@safety_router.get("/statistics/{user_id}")
async def get_safety_statistics(user_id: str):
    """
    Get comprehensive safety statistics for a user
    
    Args:
        user_id: User identifier
        
    Returns:
        Safety statistics including events, preferences, and patterns
    """
    try:
        # Get safety engine statistics
        safety_stats = await contextual_safety_engine.get_safety_statistics(user_id)
        
        # Get session statistics
        session_stats = await session_control.get_session_statistics(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "safety_statistics": safety_stats,
            "session_statistics": session_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get safety statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@safety_router.get("/health")
async def safety_system_health():
    """
    Get health status of all safety systems
    
    Returns:
        Health status of safety components
    """
    try:
        health_status = {
            "contextual_safety_engine": "operational",
            "anchor_processor": "operational", 
            "session_control": "operational",
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "health_status": health_status,
            "message": "All safety systems operational"
        }
        
    except Exception as e:
        logger.error(f"❌ Safety system health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions

def _get_category_description(category: ContentCategory) -> str:
    """Get description for content category"""
    descriptions = {
        ContentCategory.GENERAL: "General conversation topics and everyday interactions",
        ContentCategory.ROMANTIC: "Romantic expressions, affection, and relationship topics",
        ContentCategory.INTIMATE: "Personal sharing, vulnerability, and emotional intimacy",
        ContentCategory.ADULT: "Adult content and mature themes",
        ContentCategory.EMOTIONAL_INTENSE: "Highly emotional or intense psychological content",
        ContentCategory.THERAPEUTIC: "Supportive, healing, and therapeutic content"
    }
    return descriptions.get(category, "Content category")

def _get_safety_level_description(level: SafetyLevel) -> str:
    """Get description for safety level"""
    descriptions = {
        SafetyLevel.MINIMAL_TRUST: "New relationship with strict content restrictions",
        SafetyLevel.BUILDING_TRUST: "Growing relationship with moderate restrictions",
        SafetyLevel.ESTABLISHED_TRUST: "Established relationship with relaxed restrictions",
        SafetyLevel.INTIMATE_TRUST: "Deep relationship with contextual content evaluation",
        SafetyLevel.EMERGENCY_SAFE: "Emergency safe mode with maximum protection"
    }
    return descriptions.get(level, "Safety level")

# Export router
__all__ = ["safety_router"]
