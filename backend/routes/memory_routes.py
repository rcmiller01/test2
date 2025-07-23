"""
Memory API Routes for Enhanced Memory System
Provides endpoints for symbolic memory and emotional arcs
"""

from fastapi import APIRouter, HTTPException, Form, Query
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

from ..modules.memory.symbolic_memory import symbolic_memory_system, SymbolType
from ..modules.memory.emotional_arcs import emotional_arcs_system, ArcType, EmotionalPhase

logger = logging.getLogger(__name__)

# Create memory router
memory_router = APIRouter(prefix="/api/memory", tags=["memory"])

@memory_router.on_event("startup")
async def initialize_memory_systems():
    """Initialize memory systems on startup"""
    try:
        await symbolic_memory_system.initialize()
        await emotional_arcs_system.initialize()
        logger.info("🧠 Enhanced Memory Systems initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize memory systems: {e}")

# Symbolic Memory Endpoints

@memory_router.post("/symbolic/store")
async def store_symbolic_memory(
    content: str = Form(...),
    symbols: str = Form(...),  # Comma-separated symbols
    emotions: str = Form(""),  # JSON string of emotion:intensity pairs
    context: str = Form("{}")  # JSON string of additional context
):
    """
    Store a new memory with symbolic associations
    
    Args:
        content: The memory content
        symbols: Comma-separated list of associated symbols
        emotions: JSON string of emotions and intensities
        context: Additional context as JSON
        
    Returns:
        Memory ID and confirmation
    """
    try:
        # Parse inputs
        symbol_list = [s.strip() for s in symbols.split(",") if s.strip()]
        
        try:
            import json
            emotion_dict = json.loads(emotions) if emotions else {}
            context_dict = json.loads(context) if context else {}
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in emotions or context")
        
        # Store memory
        memory_id = await symbolic_memory_system.store_memory(
            content=content,
            symbols=symbol_list,
            emotional_context=emotion_dict,
            user_context=context_dict
        )
        
        return {
            "success": True,
            "memory_id": memory_id,
            "symbols_stored": len(symbol_list),
            "message": "Memory stored successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to store symbolic memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@memory_router.get("/symbolic/{symbol}")
async def recall_by_symbol(
    symbol: str,
    limit: int = Query(10, ge=1, le=50),
    min_strength: float = Query(0.1, ge=0.0, le=1.0)
):
    """
    Recall memories associated with a symbol
    
    Args:
        symbol: Symbol to search for
        limit: Maximum number of memories to return
        min_strength: Minimum association strength
        
    Returns:
        List of associated memories
    """
    try:
        memories = await symbolic_memory_system.recall_by_symbol(
            symbol=symbol,
            limit=limit,
            min_strength=min_strength
        )
        
        # Convert to response format
        memory_list = []
        for memory in memories:
            memory_dict = {
                "id": memory.id,
                "symbol": memory.symbol,
                "symbol_type": memory.symbol_type.value,
                "content": memory.content,
                "emotional_weight": memory.emotional_weight,
                "association_strength": memory.association_strength,
                "created_at": memory.created_at.isoformat(),
                "last_accessed": memory.last_accessed.isoformat(),
                "access_count": memory.access_count
            }
            memory_list.append(memory_dict)
        
        return {
            "success": True,
            "symbol": symbol,
            "memories": memory_list,
            "total_found": len(memory_list)
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to recall memories by symbol: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@memory_router.get("/symbolic/emotion/{emotion}")
async def recall_by_emotion(
    emotion: str,
    intensity_threshold: float = Query(0.5, ge=0.0, le=1.0),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Recall memories by emotional context
    
    Args:
        emotion: Emotion to search for
        intensity_threshold: Minimum emotion intensity
        limit: Maximum number of memories
        
    Returns:
        List of emotionally relevant memories
    """
    try:
        memories = await symbolic_memory_system.recall_by_emotion(
            emotion=emotion,
            intensity_threshold=intensity_threshold,
            limit=limit
        )
        
        # Convert to response format
        memory_list = []
        for memory in memories:
            memory_dict = {
                "id": memory.id,
                "symbol": memory.symbol,
                "content": memory.content,
                "emotional_weight": memory.emotional_weight,
                "association_strength": memory.association_strength,
                "created_at": memory.created_at.isoformat()
            }
            memory_list.append(memory_dict)
        
        return {
            "success": True,
            "emotion": emotion,
            "memories": memory_list,
            "total_found": len(memory_list)
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to recall memories by emotion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@memory_router.get("/symbolic/connections")
async def find_symbolic_connections(
    symbols: str = Query(..., description="Comma-separated symbols to find connections for")
):
    """
    Find symbolic connections between symbols
    
    Args:
        symbols: Comma-separated list of symbols
        
    Returns:
        Map of symbol connections
    """
    try:
        symbol_list = [s.strip() for s in symbols.split(",") if s.strip()]
        
        connections = await symbolic_memory_system.find_symbolic_connections(symbol_list)
        
        return {
            "success": True,
            "input_symbols": symbol_list,
            "connections": connections
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to find symbolic connections: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@memory_router.get("/symbolic/statistics")
async def get_memory_statistics():
    """
    Get memory system statistics
    
    Returns:
        Memory usage and statistics
    """
    try:
        stats = await symbolic_memory_system.get_memory_statistics()
        
        return {
            "success": True,
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get memory statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Emotional Arcs Endpoints

@memory_router.post("/arcs/start")
async def start_emotional_arc(
    user_id: str = Form(...),
    arc_type: str = Form(...),
    context: str = Form("{}")
):
    """
    Start tracking a new emotional arc
    
    Args:
        user_id: User identifier
        arc_type: Type of arc to track
        context: Initial context as JSON
        
    Returns:
        Arc ID and confirmation
    """
    try:
        # Validate arc type
        try:
            arc_type_enum = ArcType(arc_type)
        except ValueError:
            valid_types = [t.value for t in ArcType]
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid arc type. Valid types: {valid_types}"
            )
        
        # Parse context
        try:
            import json
            context_dict = json.loads(context) if context else {}
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in context")
        
        # Start arc
        arc_id = await emotional_arcs_system.start_new_arc(
            user_id=user_id,
            arc_type=arc_type_enum,
            initial_context=context_dict
        )
        
        return {
            "success": True,
            "arc_id": arc_id,
            "arc_type": arc_type,
            "message": "Emotional arc started successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to start emotional arc: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@memory_router.post("/arcs/record")
async def record_emotional_data(
    user_id: str = Form(...),
    emotion_type: str = Form(...),
    intensity: float = Form(..., ge=0.0, le=1.0),
    valence: float = Form(..., ge=-1.0, le=1.0),
    context: str = Form("{}"),
    trigger_event: Optional[str] = Form(None)
):
    """
    Record emotional data point
    
    Args:
        user_id: User identifier
        emotion_type: Type of emotion (happy, sad, love, etc.)
        intensity: Emotion intensity (0.0 to 1.0)
        valence: Emotion valence (-1.0 negative to 1.0 positive)
        context: Additional context as JSON
        trigger_event: What triggered this emotion
        
    Returns:
        Confirmation of recording
    """
    try:
        # Parse context
        try:
            import json
            context_dict = json.loads(context) if context else {}
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in context")
        
        # Record data
        await emotional_arcs_system.record_emotional_data(
            user_id=user_id,
            emotion_type=emotion_type,
            intensity=intensity,
            valence=valence,
            context=context_dict,
            trigger_event=trigger_event
        )
        
        return {
            "success": True,
            "message": "Emotional data recorded successfully",
            "emotion": emotion_type,
            "intensity": intensity,
            "valence": valence
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to record emotional data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@memory_router.get("/arcs/{user_id}/summary")
async def get_user_arc_summary(user_id: str):
    """
    Get summary of user's emotional arcs
    
    Args:
        user_id: User identifier
        
    Returns:
        Summary of all user's emotional arcs
    """
    try:
        summary = await emotional_arcs_system.get_arc_summary(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get arc summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@memory_router.get("/arcs/types")
async def get_arc_types():
    """
    Get available emotional arc types
    
    Returns:
        List of available arc types
    """
    arc_types = [
        {
            "id": arc_type.value,
            "name": arc_type.value.replace("_", " ").title(),
            "description": _get_arc_description(arc_type)
        }
        for arc_type in ArcType
    ]
    
    return {
        "success": True,
        "arc_types": arc_types
    }

@memory_router.get("/arcs/phases")
async def get_emotional_phases():
    """
    Get available emotional phases
    
    Returns:
        List of emotional development phases
    """
    phases = [
        {
            "id": phase.value,
            "name": phase.value.replace("_", " ").title(),
            "description": _get_phase_description(phase)
        }
        for phase in EmotionalPhase
    ]
    
    return {
        "success": True,
        "phases": phases
    }

def _get_arc_description(arc_type: ArcType) -> str:
    """Get description for arc type"""
    descriptions = {
        ArcType.RELATIONSHIP_DEVELOPMENT: "Tracks the development of interpersonal relationships",
        ArcType.MOOD_PROGRESSION: "Monitors overall mood changes over time",
        ArcType.TRUST_BUILDING: "Measures the building of trust and confidence",
        ArcType.INTIMACY_GROWTH: "Tracks emotional intimacy and connection",
        ArcType.ATTACHMENT_FORMATION: "Monitors attachment and bonding processes",
        ArcType.EMOTIONAL_HEALING: "Tracks emotional recovery and healing",
        ArcType.PERSONAL_GROWTH: "Monitors personal development and growth"
    }
    return descriptions.get(arc_type, "Tracks emotional development")

def _get_phase_description(phase: EmotionalPhase) -> str:
    """Get description for emotional phase"""
    descriptions = {
        EmotionalPhase.INITIAL_CONTACT: "First interactions and impressions",
        EmotionalPhase.EXPLORATION: "Getting to know each other",
        EmotionalPhase.BUILDING_TRUST: "Developing trust and reliability",
        EmotionalPhase.DEEPENING_BOND: "Strengthening emotional connection",
        EmotionalPhase.INTIMATE_CONNECTION: "Deep emotional intimacy",
        EmotionalPhase.STABLE_RELATIONSHIP: "Established, stable connection",
        EmotionalPhase.CRISIS_RESOLUTION: "Working through challenges",
        EmotionalPhase.RENEWED_CONNECTION: "Reconnecting after difficulties"
    }
    return descriptions.get(phase, "Emotional development phase")

# Export router
__all__ = ["memory_router"]
