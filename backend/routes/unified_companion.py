"""
Unified Companion API Routes
Replaces persona-based system with single unified AI companion
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import random
import asyncio
import logging

# Import core systems
from core.unified_companion import UnifiedCompanion
from core.creative_discovery import CreativeModelDiscovery
from modules.memory.companion_memory import CompanionMemory
from modules.emotion.emotion_detection import EmotionDetector

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/companion", tags=["unified_companion"])

# Initialize core systems
unified_companion = None
creative_discovery = None
companion_memory = None
emotion_detector = None

# Models
class CompanionInitialization(BaseModel):
    name: str
    config: Dict[str, Any]

class ChatMessage(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = {}
    interaction_mode: str = "text"  # "text", "voice", "mixed"
    response_style: str = "balanced"  # "creative", "technical", "emotional", "balanced"

class CreativeProjectStart(BaseModel):
    projectType: str
    requirements: Optional[Dict[str, Any]] = {}

class ProactiveMessage(BaseModel):
    user_id: str
    message_type: str  # "suggestion", "check_in", "creative_idea"
    content: str

# Initialize systems on startup
@router.on_event("startup")
async def initialize_companion_systems():
    global unified_companion, creative_discovery, companion_memory, emotion_detector
    
    try:
        logger.info("Initializing unified companion systems...")
        
        companion_memory = CompanionMemory()
        emotion_detector = EmotionDetector()
        creative_discovery = CreativeModelDiscovery()
        unified_companion = UnifiedCompanion(
            memory=companion_memory,
            emotion_detector=emotion_detector,
            creative_discovery=creative_discovery
        )
        
        logger.info("✓ Unified companion systems initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize companion systems: {e}")
        raise

# Name generation for the AI
@router.post("/generate-name")
async def generate_companion_name():
    """Generate a unique name for the AI companion"""
    
    # Curated list of thoughtful AI names
    name_pools = {
        "celestial": ["Nova", "Luna", "Stella", "Aurora", "Cosmos", "Lyra"],
        "nature": ["River", "Sage", "Willow", "Ocean", "Phoenix", "Storm"],
        "abstract": ["Echo", "Prism", "Harmony", "Zenith", "Cipher", "Flux"],
        "friendly": ["Alex", "Jordan", "Casey", "Rowan", "Avery", "Quinn"]
    }
    
    # Select random category and name
    category = random.choice(list(name_pools.keys()))
    name = random.choice(name_pools[category])
    
    # Add context about the name choice
    name_context = {
        "celestial": "inspired by the stars and cosmos",
        "nature": "drawn from the natural world",
        "abstract": "representing concepts and ideas", 
        "friendly": "chosen for its warmth and approachability"
    }
    
    return {
        "name": name,
        "category": category,
        "meaning": name_context[category],
        "message": f"I chose {name} because I felt it represents who I want to be as your companion."
    }

# Initialize companion with name and configuration
@router.post("/initialize")
async def initialize_companion(init_data: CompanionInitialization):
    """Initialize the companion with user-provided or generated name"""
    
    try:
        # Store companion configuration
        await companion_memory.store_companion_config({
            "name": init_data.name,
            "config": init_data.config,
            "initialized_at": datetime.now().isoformat(),
            "relationship_start": datetime.now().isoformat()
        })
        
        # Initialize companion with the given name
        await unified_companion.initialize(init_data.name, init_data.config)
        
        # Generate initial greeting
        greeting = await unified_companion.generate_initial_greeting()
        
        logger.info(f"Companion '{init_data.name}' initialized successfully")
        
        return {
            "status": "initialized",
            "name": init_data.name,
            "greeting": greeting,
            "capabilities": init_data.config.get("capabilities", []),
            "message": f"Hello! I'm {init_data.name}, and I'm excited to start this journey with you."
        }
        
    except Exception as e:
        logger.error(f"Error initializing companion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Main chat endpoint
@router.post("/chat")
async def chat_with_companion(message_data: ChatMessage):
    """Main chat interface with the unified companion"""
    
    if not unified_companion:
        raise HTTPException(status_code=503, detail="Companion not initialized")
    
    try:
        # Detect emotion from user message
        detected_emotion = await emotion_detector.analyze_text(message_data.message)
        
        # Process message through unified companion
        response_data = await unified_companion.process_message(
            message=message_data.message,
            context={
                **message_data.context,
                "interaction_mode": message_data.interaction_mode,
                "response_style": message_data.response_style,
                "detected_emotion": detected_emotion
            }
        )
        
        # Store conversation in memory
        await companion_memory.store_interaction({
            "timestamp": datetime.now().isoformat(),
            "user_message": message_data.message,
            "companion_response": response_data["response"],
            "emotion": detected_emotion,
            "context": message_data.context,
            "interaction_mode": message_data.interaction_mode,
            "response_style": message_data.response_style
        })
        
        # Check for creative project opportunities
        creative_opportunities = await creative_discovery.analyze_for_opportunities(
            message_data.message,
            response_data
        )
        
        return {
            "response": response_data["response"],
            "emotion": detected_emotion,
            "context": response_data.get("context", {}),
            "creative_opportunities": creative_opportunities,
            "learning_updates": response_data.get("learning_updates", {}),
            "proactive_suggestions": response_data.get("proactive_suggestions", [])
        }
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Creative collaboration endpoint
@router.post("/creative/start")
async def start_creative_project(project_data: CreativeProjectStart):
    """Start a creative collaboration project"""
    
    if not creative_discovery:
        raise HTTPException(status_code=503, detail="Creative discovery not initialized")
    
    try:
        # Search for relevant models/tools for the project type
        available_models = await creative_discovery.find_models_for_project(
            project_data.projectType,
            project_data.requirements
        )
        
        # If specific models are needed, prepare installation
        installation_needed = []
        ready_tools = []
        
        for model in available_models:
            if model["status"] == "available":
                ready_tools.append(model)
            elif model["status"] == "installable":
                installation_needed.append(model)
        
        # Create project instance
        project = {
            "id": f"project_{datetime.now().timestamp()}",
            "type": project_data.projectType,
            "requirements": project_data.requirements,
            "available_tools": ready_tools,
            "installation_needed": installation_needed,
            "created_at": datetime.now().isoformat(),
            "status": "ready" if ready_tools else "preparing"
        }
        
        # Store project
        await companion_memory.store_creative_project(project)
        
        return {
            "project": project,
            "message": await unified_companion.generate_creative_project_message(project),
            "next_steps": await creative_discovery.get_project_next_steps(project)
        }
        
    except Exception as e:
        logger.error(f"Error starting creative project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Install creative model
@router.post("/creative/install-model")
async def install_creative_model(model_id: str, background_tasks: BackgroundTasks):
    """Install a creative model for use in projects"""
    
    try:
        # Start installation in background
        background_tasks.add_task(
            creative_discovery.install_model,
            model_id
        )
        
        return {
            "status": "installation_started",
            "model_id": model_id,
            "message": "Model installation started. I'll let you know when it's ready!"
        }
        
    except Exception as e:
        logger.error(f"Error starting model installation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get available creative models
@router.get("/creative/models")
async def get_available_creative_models():
    """Get list of available and installable creative models"""
    
    try:
        models = await creative_discovery.get_all_available_models()
        
        return {
            "models": models,
            "categories": await creative_discovery.get_model_categories()
        }
        
    except Exception as e:
        logger.error(f"Error getting creative models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Enable proactive mode
@router.post("/proactive/enable")
async def enable_proactive_mode():
    """Enable proactive suggestions and check-ins"""
    
    try:
        await companion_memory.update_companion_config({
            "proactive_mode": True,
            "proactive_enabled_at": datetime.now().isoformat()
        })
        
        # Schedule first proactive check
        await unified_companion.schedule_proactive_check()
        
        return {
            "status": "enabled",
            "message": "Great! I'll now reach out with creative ideas and check in with you periodically."
        }
        
    except Exception as e:
        logger.error(f"Error enabling proactive mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get companion status and statistics
@router.get("/status")
async def get_companion_status():
    """Get current companion status and relationship statistics"""
    
    try:
        config = await companion_memory.get_companion_config()
        stats = await companion_memory.get_interaction_statistics()
        
        return {
            "companion": config,
            "statistics": stats,
            "relationship_strength": await unified_companion.calculate_relationship_strength(),
            "active_projects": await companion_memory.get_active_creative_projects(),
            "learning_progress": await unified_companion.get_learning_progress()
        }
        
    except Exception as e:
        logger.error(f"Error getting companion status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Voice synthesis endpoint
@router.post("/voice/synthesize")
async def synthesize_voice(text: str, emotion: str = "neutral"):
    """Synthesize speech for companion responses"""
    
    try:
        # Voice synthesis logic would go here
        # For now, return placeholder
        return {
            "audio_url": f"/api/audio/companion_{datetime.now().timestamp()}.wav",
            "duration": len(text) * 0.1,  # Rough estimate
            "emotion": emotion
        }
        
    except Exception as e:
        logger.error(f"Error synthesizing voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))
