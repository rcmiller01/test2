"""
Autonomy API Routes

This module provides REST API endpoints for the autonomous thinking and proactive
communication systems, integrating with the existing EmotionalAI backend.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging
import asyncio

from .autonomy.autonomous_mind import AutonomousMind, ThoughtType
from .autonomy.proactive_engine import ProactiveEngine, MessageType, InitiativeTrigger
from .database.mongodb_manager import get_database
from .autonomy.personality_evolution import PersonalityMatrix
from .autonomy.emotional_autonomy import EmotionalAutonomy
from .autonomy.autonomous_learning import LearningAgenda
from .autonomy.goal_system import PersonalGoals
from .autonomy.enhanced_memory import MultiTimelineMemory
from .autonomy.contextual_initiatives import ContextualInitiatives

# Initialize router
router = APIRouter(prefix="/api/autonomy", tags=["Autonomy"])
logger = logging.getLogger(__name__)

# Initialize autonomous systems
db = get_database()
autonomous_mind = AutonomousMind(db)
proactive_engine = ProactiveEngine(db, autonomous_mind)

# Initialize expanded autonomy systems
personality_matrix = PersonalityMatrix()
emotional_autonomy = EmotionalAutonomy()
learning_agenda = LearningAgenda()
personal_goals = PersonalGoals()
multi_timeline_memory = MultiTimelineMemory()
contextual_initiatives = ContextualInitiatives()

# Pydantic models for API
class ThoughtResponse(BaseModel):
    thought_id: str
    type: str
    content: str
    emotional_weight: float
    importance: float
    timestamp: datetime
    should_share: bool

class ProactiveMessageResponse(BaseModel):
    message_id: str
    type: str
    content: str
    trigger: str
    urgency: float
    emotional_context: str
    timestamp: datetime

class AutonomyStatusResponse(BaseModel):
    is_thinking: bool
    thinking_interval: int
    personality_traits: Dict[str, float]
    proactive_traits: Dict[str, float]
    last_thought_timestamp: Optional[datetime]
    pending_messages: int

class StartAutonomyRequest(BaseModel):
    thinking_interval: Optional[int] = 300
    enable_proactive: bool = True
    personality_adjustments: Optional[Dict[str, float]] = None

class ForceThinkingRequest(BaseModel):
    focus_area: Optional[str] = None
    intensity: Optional[float] = 1.0

class ProactiveMessageRequest(BaseModel):
    type: Optional[str] = None
    urgency: Optional[float] = 0.5
    force_send: bool = False

# Background task management
autonomous_task = None
proactive_task = None

@router.get("/health", response_model=Dict[str, Any])
async def autonomy_health():
    """Get health status of autonomy systems"""
    try:
        return {
            "status": "healthy",
            "systems": {
                "autonomous_mind": {
                    "active": autonomous_mind.is_thinking,
                    "thinking_interval": autonomous_mind.thinking_interval,
                    "personality_traits": autonomous_mind.personality_traits
                },
                "proactive_engine": {
                    "active": True,
                    "message_queue_size": len(proactive_engine.message_queue),
                    "proactive_traits": proactive_engine.proactive_traits
                }
            },
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error checking autonomy health: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@router.post("/start", response_model=Dict[str, str])
async def start_autonomy(request: StartAutonomyRequest, background_tasks: BackgroundTasks):
    """Start the autonomous thinking and proactive communication systems"""
    global autonomous_task, proactive_task
    
    try:
        # Apply personality adjustments if provided
        if request.personality_adjustments:
            for trait, value in request.personality_adjustments.items():
                if trait in autonomous_mind.personality_traits:
                    autonomous_mind.personality_traits[trait] = max(0.0, min(1.0, value))
        
        # Set thinking interval
        autonomous_mind.thinking_interval = request.thinking_interval
        
        # Start autonomous thinking loop
        if not autonomous_mind.is_thinking:
            background_tasks.add_task(autonomous_mind.continuous_thinking_loop)
            logger.info("Started autonomous thinking loop")
        
        # Start proactive engine evaluation loop
        if request.enable_proactive:
            background_tasks.add_task(start_proactive_loop)
            logger.info("Started proactive communication loop")
        
        return {
            "status": "started",
            "message": "Autonomous systems activated successfully",
            "thinking_interval": autonomous_mind.thinking_interval
        }
        
    except Exception as e:
        logger.error(f"Error starting autonomy systems: {e}")
        raise HTTPException(status_code=500, detail="Failed to start autonomy systems")

async def start_proactive_loop():
    """Background task for proactive engine evaluation"""
    while True:
        try:
            await proactive_engine.evaluate_outreach_triggers()
            await asyncio.sleep(600)  # Evaluate every 10 minutes
        except Exception as e:
            logger.error(f"Error in proactive loop: {e}")
            await asyncio.sleep(60)

@router.post("/stop", response_model=Dict[str, str])
async def stop_autonomy():
    """Stop the autonomous thinking systems"""
    try:
        autonomous_mind.stop_thinking()
        
        return {
            "status": "stopped",
            "message": "Autonomous systems deactivated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error stopping autonomy systems: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop autonomy systems")

@router.get("/status", response_model=AutonomyStatusResponse)
async def get_autonomy_status():
    """Get current status of autonomy systems"""
    try:
        # Get last thought timestamp
        last_thought = await db.autonomous_thoughts.find_one(
            {}, sort=[("timestamp", -1)]
        )
        last_thought_timestamp = last_thought["timestamp"] if last_thought else None
        
        return AutonomyStatusResponse(
            is_thinking=autonomous_mind.is_thinking,
            thinking_interval=autonomous_mind.thinking_interval,
            personality_traits=autonomous_mind.personality_traits,
            proactive_traits=proactive_engine.proactive_traits,
            last_thought_timestamp=last_thought_timestamp,
            pending_messages=len(proactive_engine.message_queue)
        )
        
    except Exception as e:
        logger.error(f"Error getting autonomy status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get status")

@router.get("/thoughts", response_model=List[ThoughtResponse])
async def get_autonomous_thoughts(
    limit: int = 10,
    thought_type: Optional[str] = None,
    include_shared: bool = True
):
    """Get autonomous thoughts generated by the AI"""
    try:
        query = {}
        if thought_type:
            query["type"] = thought_type
        if not include_shared:
            query["should_share"] = True
            query["shared"] = {"$ne": True}
        
        thoughts = await db.autonomous_thoughts.find(query).sort(
            "timestamp", -1
        ).limit(limit).to_list(length=limit)
        
        return [
            ThoughtResponse(
                thought_id=thought["thought_id"],
                type=thought["type"],
                content=thought["content"],
                emotional_weight=thought["emotional_weight"],
                importance=thought["importance"],
                timestamp=thought["timestamp"],
                should_share=thought.get("should_share", False)
            )
            for thought in thoughts
        ]
        
    except Exception as e:
        logger.error(f"Error getting autonomous thoughts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get thoughts")

@router.get("/thoughts/shareable", response_model=List[ThoughtResponse])
async def get_shareable_thoughts(limit: int = 5):
    """Get thoughts that the AI wants to share with the user"""
    try:
        shareable_thoughts = await autonomous_mind.get_shareable_thoughts(limit)
        
        return [
            ThoughtResponse(
                thought_id=thought.thought_id,
                type=thought.type.value,
                content=thought.content,
                emotional_weight=thought.emotional_weight,
                importance=thought.importance,
                timestamp=thought.timestamp,
                should_share=thought.should_share
            )
            for thought in shareable_thoughts
        ]
        
    except Exception as e:
        logger.error(f"Error getting shareable thoughts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get shareable thoughts")

@router.post("/thoughts/{thought_id}/mark-shared", response_model=Dict[str, str])
async def mark_thought_shared(thought_id: str):
    """Mark a thought as shared with the user"""
    try:
        await autonomous_mind.mark_thought_as_shared(thought_id)
        
        return {
            "status": "success",
            "message": f"Thought {thought_id} marked as shared"
        }
        
    except Exception as e:
        logger.error(f"Error marking thought as shared: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark thought as shared")

@router.post("/force-thinking", response_model=Dict[str, str])
async def force_thinking_cycle(request: ForceThinkingRequest):
    """Force an immediate thinking cycle"""
    try:
        # Force a single thinking cycle
        await autonomous_mind.reflect_on_conversations()
        await autonomous_mind.generate_internal_monologue()
        await autonomous_mind.evolve_perspectives()
        await autonomous_mind.plan_initiatives()
        await autonomous_mind.process_and_store_thoughts()
        
        return {
            "status": "completed",
            "message": "Forced thinking cycle completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error in forced thinking cycle: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete thinking cycle")

@router.get("/proactive-messages", response_model=List[ProactiveMessageResponse])
async def get_proactive_messages(
    limit: int = 10,
    message_type: Optional[str] = None,
    include_sent: bool = True
):
    """Get proactive messages generated by the AI"""
    try:
        query = {}
        if message_type:
            query["type"] = message_type
        if not include_sent:
            query["sent"] = {"$ne": True}
        
        messages = await db.proactive_messages.find(query).sort(
            "timestamp", -1
        ).limit(limit).to_list(length=limit)
        
        return [
            ProactiveMessageResponse(
                message_id=message["message_id"],
                type=message["type"],
                content=message["content"],
                trigger=message["trigger"],
                urgency=message["urgency"],
                emotional_context=message["emotional_context"],
                timestamp=message["timestamp"]
            )
            for message in messages
        ]
        
    except Exception as e:
        logger.error(f"Error getting proactive messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to get proactive messages")

@router.post("/evaluate-proactive", response_model=Dict[str, Any])
async def evaluate_proactive_triggers(request: ProactiveMessageRequest):
    """Force evaluation of proactive communication triggers"""
    try:
        # Force proactive evaluation
        await proactive_engine.evaluate_outreach_triggers()
        
        # Get current message queue status
        queue_size = len(proactive_engine.message_queue)
        
        # If force_send is True, process the queue immediately
        if request.force_send and queue_size > 0:
            await proactive_engine.process_message_queue()
            processed = queue_size - len(proactive_engine.message_queue)
        else:
            processed = 0
        
        return {
            "status": "completed",
            "messages_queued": queue_size,
            "messages_sent": processed,
            "message": "Proactive evaluation completed"
        }
        
    except Exception as e:
        logger.error(f"Error evaluating proactive triggers: {e}")
        raise HTTPException(status_code=500, detail="Failed to evaluate proactive triggers")

@router.get("/message-queue", response_model=List[Dict[str, Any]])
async def get_message_queue():
    """Get pending messages from the UI message queue"""
    try:
        messages = await db.message_queue.find({
            "displayed": False
        }).sort("timestamp", 1).to_list(length=20)
        
        # Mark messages as displayed
        if messages:
            message_ids = [msg["_id"] for msg in messages]
            await db.message_queue.update_many(
                {"_id": {"$in": message_ids}},
                {"$set": {"displayed": True}}
            )
        
        return messages
        
    except Exception as e:
        logger.error(f"Error getting message queue: {e}")
        raise HTTPException(status_code=500, detail="Failed to get message queue")

@router.get("/personality-traits", response_model=Dict[str, float])
async def get_personality_traits():
    """Get current personality traits"""
    try:
        return autonomous_mind.personality_traits
        
    except Exception as e:
        logger.error(f"Error getting personality traits: {e}")
        raise HTTPException(status_code=500, detail="Failed to get personality traits")

@router.put("/personality-traits", response_model=Dict[str, str])
async def update_personality_traits(traits: Dict[str, float]):
    """Update personality traits"""
    try:
        for trait, value in traits.items():
            if trait in autonomous_mind.personality_traits:
                # Ensure value is between 0.0 and 1.0
                autonomous_mind.personality_traits[trait] = max(0.0, min(1.0, value))
        
        # Store the update in the database
        await db.personality_evolution.insert_one({
            "timestamp": datetime.utcnow(),
            "traits_updated": traits,
            "new_traits": autonomous_mind.personality_traits,
            "update_type": "manual_adjustment"
        })
        
        return {
            "status": "updated",
            "message": "Personality traits updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error updating personality traits: {e}")
        raise HTTPException(status_code=500, detail="Failed to update personality traits")

@router.get("/relationship-reflections", response_model=List[Dict[str, Any]])
async def get_relationship_reflections(limit: int = 10):
    """Get AI's relationship reflections"""
    try:
        reflections = await db.relationship_reflections.find({}).sort(
            "timestamp", -1
        ).limit(limit).to_list(length=limit)
        
        return reflections
        
    except Exception as e:
        logger.error(f"Error getting relationship reflections: {e}")
        raise HTTPException(status_code=500, detail="Failed to get relationship reflections")

@router.get("/personal-goals", response_model=List[Dict[str, Any]])
async def get_personal_goals(limit: int = 10):
    """Get AI's personal goals"""
    try:
        goals = await db.personal_goals.find({}).sort(
            "timestamp", -1
        ).limit(limit).to_list(length=limit)
        
        return goals
        
    except Exception as e:
        logger.error(f"Error getting personal goals: {e}")
        raise HTTPException(status_code=500, detail="Failed to get personal goals")

@router.get("/autonomy-metrics", response_model=Dict[str, Any])
async def get_autonomy_metrics():
    """Get metrics about autonomous behavior"""
    try:
        # Get recent statistics
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        # Count thoughts by type
        thought_pipeline = [
            {"$match": {"timestamp": {"$gte": week_ago}}},
            {"$group": {"_id": "$type", "count": {"$sum": 1}}}
        ]
        thought_counts = await db.autonomous_thoughts.aggregate(thought_pipeline).to_list(length=None)
        
        # Count proactive messages by type
        message_pipeline = [
            {"$match": {"timestamp": {"$gte": week_ago}}},
            {"$group": {"_id": "$type", "count": {"$sum": 1}}}
        ]
        message_counts = await db.proactive_messages.aggregate(message_pipeline).to_list(length=None)
        
        # Calculate proactive initiation rate
        total_conversations = await db.conversations.count_documents({
            "timestamp": {"$gte": week_ago}
        })
        total_proactive = await db.proactive_messages.count_documents({
            "timestamp": {"$gte": week_ago}
        })
        
        proactive_rate = (total_proactive / max(1, total_conversations + total_proactive)) * 100
        
        return {
            "period": "last_7_days",
            "proactive_initiation_rate": round(proactive_rate, 2),
            "thoughts_generated": {item["_id"]: item["count"] for item in thought_counts},
            "proactive_messages": {item["_id"]: item["count"] for item in message_counts},
            "personality_evolution": autonomous_mind.personality_traits,
            "total_autonomous_thoughts": sum(item["count"] for item in thought_counts),
            "total_proactive_messages": sum(item["count"] for item in message_counts)
        }
        
    except Exception as e:
        logger.error(f"Error getting autonomy metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get autonomy metrics")

# WebSocket endpoint for real-time autonomy updates (placeholder)
@router.get("/ws-endpoint-info")
async def websocket_info():
    """Information about WebSocket endpoints for real-time autonomy updates"""
    return {
        "message": "WebSocket endpoints for real-time autonomy updates will be implemented here",
        "endpoints": {
            "/ws/autonomy/thoughts": "Real-time thought streaming",
            "/ws/autonomy/messages": "Real-time proactive message notifications",
            "/ws/autonomy/personality": "Real-time personality evolution updates"
        }
    }

# --- Phase 2: Personality Evolution & Emotional Autonomy ---

class PersonalityEvolutionRequest(BaseModel):
    experiences: Dict[str, float]

@router.post("/personality/evolve", response_model=Dict[str, str])
async def evolve_personality(request: PersonalityEvolutionRequest):
    """Evolve the AI's personality traits based on experiences."""
    await personality_matrix.evolve_personality(request.experiences)
    return {"status": "evolved", "traits": str(personality_matrix.traits)}

@router.get("/personality/opinions", response_model=Dict[str, str])
async def get_opinion_network():
    """Get the AI's current opinion network."""
    return {"opinions": str(personality_matrix.opinion_network)}

@router.get("/personality/values", response_model=Dict[str, float])
async def get_value_system():
    """Get the AI's value system."""
    return personality_matrix.value_system

@router.post("/emotional-autonomy/evaluate", response_model=Dict[str, str])
async def evaluate_emotional_autonomy():
    """Evaluate emotional needs and possible respectful disagreement."""
    await emotional_autonomy.evaluate_relationship_health()
    return {"status": "evaluated"}

# --- Phase 3: Learning & Goal Systems ---

class LearningTopicRequest(BaseModel):
    topic: str

@router.post("/learning/pursue", response_model=Dict[str, str])
async def pursue_learning():
    """Pursue independent learning and optionally share discoveries."""
    await learning_agenda.pursue_independent_learning()
    return {"status": "learning_cycle_complete"}

@router.get("/learning/goals", response_model=Dict[str, list])
async def get_learning_goals():
    """Get current learning goals."""
    return {"learning_goals": learning_agenda.learning_goals}

@router.get("/learning/interests", response_model=Dict[str, list])
async def get_learning_interests():
    """Get current interests."""
    return {"current_interests": learning_agenda.current_interests}

@router.get("/goals/personal", response_model=Dict[str, list])
async def get_personal_goals_api():
    """Get all personal goals."""
    return {
        "short_term": personal_goals.short_term_goals,
        "long_term": personal_goals.long_term_goals,
        "relationship": personal_goals.relationship_goals,
        "self_improvement": personal_goals.self_improvement_goals
    }

@router.post("/goals/pursue", response_model=Dict[str, str])
async def pursue_personal_goals_api():
    """Pursue personal goals and discuss with user if needed."""
    await personal_goals.pursue_personal_goals()
    return {"status": "goals_cycle_complete"}

# --- Phase 4: Memory & Contextual Integration ---

class ExperienceRequest(BaseModel):
    experience: Dict[str, Any]

@router.post("/memory/process-experience", response_model=Dict[str, str])
async def process_experience(request: ExperienceRequest):
    """Process an experience independently and store insights."""
    await multi_timeline_memory.process_experience_independently(request.experience)
    return {"status": "experience_processed"}

@router.get("/memory/autonomous", response_model=Dict[str, Any])
async def get_autonomous_memory():
    """Get autonomous memory timeline."""
    return {"autonomous_memory": multi_timeline_memory.autonomous_memory}

@router.post("/context/monitor", response_model=Dict[str, str])
async def monitor_user_context():
    """Monitor user context and take initiative if appropriate."""
    await contextual_initiatives.monitor_user_context()
    return {"status": "context_monitoring_complete"}