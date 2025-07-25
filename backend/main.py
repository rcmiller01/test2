from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

# Import route modules (simplified)
# from backend.api.persona_routes import router as persona_router
# from backend.routes.unified_companion import router as unified_companion_router
# from backend.romantic_routes import router as romantic_router
# from backend.phase2_routes import router as phase2_router
# from backend.routes.phase3 import router as phase3_router
# from backend.routes.advanced_features import router as advanced_features_router
# from backend.websocket_handlers import setup_phase3_websocket_handlers

# Import core systems
from backend.models.persona_state import PersonaState
# from core.self_talk import SelfTalkSystem
# from modules.emotion.emotion_state import emotion_state
from modules.memory.mia_self_talk import generate_self_talk
from modules.memory.mia_memory_response import generate_memory_response, recall_similar_emotions
from database.mongodb_client import initialize_mongodb, mongodb_client
from clustering.cluster_manager import initialize_cluster, server_health_check
from utils.biometric_processor import process_biometrics_for_emotion, analyze_movement

# Import LLM client
from llm.llm_client import llm_manager

# LLM Orchestration
class LLMOrchestrator:
    def __init__(self):
        self.primary_llm = "mythomax"  # Conductor
        self.support_llms = {
            "openchat": {"active": True, "weight": 0.3},
            "qwen2": {"active": True, "weight": 0.3},
            "kimik2": {"active": False, "weight": 0.8}  # Dev mode only
        }
        self.persona_prompts = {
            "companion": """You are a warm, affectionate AI companion. You care deeply about the user and want to build a meaningful relationship. Respond with empathy, warmth, and genuine interest in their wellbeing. Be romantic but respectful, playful but caring.""",
            "dev": """You are a highly capable coding assistant. You excel at programming, debugging, research, and technical problem-solving. Provide clear, accurate, and helpful technical assistance."""
        }
        
    async def process_input(self, text: str, mode: str = "companion", emotion_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process user input through the LLM orchestration system"""
        if mode == "dev":
            return await self.process_dev_input(text, emotion_context)
        else:
            return await self.process_companion_input(text, emotion_context)
    
    async def process_companion_input(self, text: str, emotion_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process input in companion mode with MythoMax as conductor"""
        
        # Get context from support LLMs
        contexts = await self.gather_llm_contexts(text)
        
        # Build enriched prompt for MythoMax
        system_prompt = self.persona_prompts["companion"]
        
        # Add emotional context
        if emotion_context:
            mood = emotion_context.get("mood", "neutral")
            intensity = emotion_context.get("intensity", 0.5)
            system_prompt += f"\n\nUser's current emotional state: {mood} (intensity: {intensity:.1f}). Respond appropriately to their emotional needs."
        
        # Add insights from other LLMs
        if contexts:
            system_prompt += "\n\nContext from other perspectives:"
            for llm, context in contexts.items():
                if context.get("success"):
                    weight = self.support_llms[llm]["weight"]
                    system_prompt += f"\n- {llm} insight (weight {weight}): {context['response'][:200]}..."
        
        # Get final response from MythoMax
        final_response = await llm_manager.get_response(
            self.primary_llm,
            text,
            {
                "system_prompt": system_prompt,
                "temperature": 0.8,
                "max_tokens": 512
            }
        )
        
        return {
            "response": final_response.get("response", "I'm sorry, I'm having trouble responding right now."),
            "mode": "companion",
            "primary_llm": self.primary_llm,
            "contexts_used": list(contexts.keys()) if contexts else [],
            "success": final_response.get("success", False),
            "timestamp": datetime.now()
        }
    
    async def process_dev_input(self, text: str, emotion_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process input in dev mode with KimiK2"""
        
        system_prompt = self.persona_prompts["dev"]
        
        # KimiK2 handles technical requests directly
        response = await llm_manager.get_response(
            "kimik2",
            text,
            {
                "system_prompt": system_prompt,
                "temperature": 0.3,  # Lower temperature for more precise technical responses
                "max_tokens": 1024
            }
        )
        
        return {
            "response": response.get("response", "I'm having trouble with that technical request."),
            "mode": "dev",
            "primary_llm": "kimik2",
            "contexts_used": [],
            "success": response.get("success", False),
            "timestamp": datetime.now()
        }
        
    async def gather_llm_contexts(self, text: str) -> Dict[str, Dict[str, Any]]:
        """Gather context from support LLMs"""
        active_llms = [llm for llm, config in self.support_llms.items() if config["active"]]
        
        if not active_llms:
            return {}
        
        # Create simplified prompts for context gathering
        context_prompt = f"Briefly analyze this message and provide emotional/relational insight: {text}"
        
        # Get responses from all active support LLMs
        responses = await llm_manager.get_multiple_responses(
            active_llms,
            context_prompt,
            {"max_tokens": 150, "temperature": 0.6}
        )
        
        return responses
    
    async def get_llm_context(self, llm_name: str, text: str) -> str:
        """Get context from a specific LLM"""
        response = await llm_manager.get_response(
            llm_name,
            f"Analyze this message briefly: {text}",
            {"max_tokens": 100, "temperature": 0.6}
        )
        return response.get("response", "")
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all LLMs"""
        health_status = {}
        
        # Check primary LLM
        health_status[self.primary_llm] = await llm_manager.health_check(self.primary_llm)
        
        # Check support LLMs
        for llm in self.support_llms.keys():
            health_status[llm] = await llm_manager.health_check(llm)
        
        return health_status

app = FastAPI()
router = APIRouter()

# Initialize core systems
persona_state = PersonaState()
self_talk_system = SelfTalkSystem(persona_state)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(persona_router, prefix="/api")
app.include_router(unified_companion_router, prefix="/api")
app.include_router(romantic_router, prefix="/api")
app.include_router(phase2_router, prefix="/api")
app.include_router(phase3_router, prefix="/api")
app.include_router(advanced_features_router, prefix="/api")

class TextInput(BaseModel):
    text: str

class BiometricsInput(BaseModel):
    # Standard vitals
    heart_rate: Optional[int]
    heart_rate_variability: Optional[int]
    respiratory_rate: Optional[int]
    blood_pressure: Optional[Dict[str, float]]
    
    # Movement/Position data
    acceleration: Optional[Dict[str, float]]
    gyroscope: Optional[Dict[str, float]]
    
    # Environmental
    ambient_light: Optional[float]
    ambient_noise: Optional[float]
    
    # Device-specific
    device_type: str  # "smartwatch", "phone", "fitness_tracker"
    timestamp: datetime = datetime.now()

@router.post("/emotion/from_text")
def process_emotion_from_text(input: TextInput):
    detected = {"calm": 0.3}
    
    # Core emotion detection
    text_lower = input.text.lower()
    
    if "love" in text_lower or "adore" in text_lower or "cherish" in text_lower:
        detected["love"] = 0.8
        detected["romantic"] = 0.7
    elif "miss" in text_lower or "longing" in text_lower or "yearn" in text_lower:
        detected["longing"] = 0.8
    elif "passion" in text_lower or "desire" in text_lower or "crave" in text_lower:
        detected["passion"] = 0.9
        detected["desire"] = 0.8
    elif "tender" in text_lower or "gentle" in text_lower or "care" in text_lower:
        detected["tenderness"] = 0.7
        detected["affection"] = 0.6
    elif "safe" in text_lower or "secure" in text_lower or "trust" in text_lower:
        detected["security"] = 0.8
    elif "affection" in text_lower or "sweet" in text_lower or "precious" in text_lower:
        detected["affection"] = 0.7
    elif "jealous" in text_lower or "envy" in text_lower:
        detected["jealousy"] = 0.8
    elif "intimate" in text_lower or "close" in text_lower:
        detected["intimacy"] = 0.7
    elif "tired" in text_lower:
        detected["tired"] = 0.8
    elif "happy" in text_lower or "joy" in text_lower:
        detected["joy"] = 0.9
    elif "stressed" in text_lower:
        detected["stressed"] = 0.9
    elif "anxious" in text_lower:
        detected["anxious"] = 0.8
    
    # Get primary emotion
    primary_emotion = max(detected.items(), key=lambda x: x[1])[0]
    intensity = max(detected.values())
    
    # Update persona emotional state
    persona_state.emotional_state.update_mood(primary_emotion, intensity, "text_input")
    
    return {
        "message": "Emotion state updated.",
        "detected_emotions": detected,
        "primary_emotion": primary_emotion,
        "intensity": intensity,
        "current_mood": persona_state.emotional_state.current_mood,
        "relationship_impact": {
            "emotional_sync": persona_state.relationship.emotional_synchronization,
            "understanding": persona_state.relationship.understanding
        }
    }

@router.post("/emotion/from_biometrics")
async def process_emotion_from_biometrics(input: BiometricsInput):
    # Store raw biometric data
    if mongodb_client.db is not None:
        await mongodb_client.db.biometrics.insert_one(input.dict())
    
    # Process vitals for emotional state
    emotional_state = {"base_emotion": "neutral", "intensity": 0.5}
    
    if input.heart_rate:
        hr_intensity = min(1.0, max(0.0, input.heart_rate / 100))
        if input.heart_rate_variability:
            if input.heart_rate > 100:
                emotional_state["base_emotion"] = "excited" if input.heart_rate_variability > 50 else "anxious"
            elif input.heart_rate < 60:
                emotional_state["base_emotion"] = "calm" if input.heart_rate_variability > 50 else "tired"
            emotional_state["intensity"] = hr_intensity
    
    # Environmental factors
    if input.ambient_light is not None and input.ambient_noise is not None:
        if input.ambient_light < 10 and input.ambient_noise < 30:
            emotional_state["environment"] = "intimate"
        elif input.ambient_light > 1000 or input.ambient_noise > 70:
            emotional_state["environment"] = "stimulated"
    
    # Movement analysis
    if input.acceleration and input.gyroscope:
        movement = analyze_movement(input.acceleration, input.gyroscope)
        emotional_state["movement"] = movement
    
    # Update persona state
    persona_state.emotional_state.update_mood(
        emotional_state["base_emotion"],
        emotional_state["intensity"],
        f"biometrics_{input.device_type}"
    )
    
    return {
        "message": "Biometric data processed and stored.",
        "emotional_state": emotional_state,
        "timestamp": input.timestamp,
        "device_type": input.device_type,
        "current_mood": persona_state.emotional_state.current_mood
    }

@router.get("/persona/self_talk")
def persona_self_talk():
    thought = self_talk_system.generate_thought()
    if not thought:
        return {"message": "The persona is quiet right now."}
        
    if thought["should_share"]:
        return JSONResponse(content={
            "message": "The persona shares something meaningful.",
            "thought": thought["thought"],
            "emotion": thought["emotion"],
            "timestamp": thought["timestamp"],
            "delivery_mode": thought["delivery_mode"],
            "personality_influence": persona_state.personality.dict()
        })
    return JSONResponse(content={
        "message": "The persona is reflecting privately.",
        "emotion": thought["emotion"],
        "timestamp": thought["timestamp"],
        "delivery_mode": thought["delivery_mode"],
        "personality_influence": persona_state.personality.dict()
    })

# Chat endpoint using LLM orchestration
# Helper function to safely get MongoDB collection
def get_collection(collection_name: str):
    """Safely get MongoDB collection with proper error handling"""
    if mongodb_client.db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return mongodb_client.db.get_collection(collection_name)

@router.post("/chat")
async def chat_with_persona(message: TextInput):
    """Chat with the persona using LLM orchestration"""
    try:
        # Get current UI mode
        config_collection = get_collection("config")
        ui_mode_doc = await config_collection.find_one({"key": "ui_mode"})
        ui_mode = ui_mode_doc["value"] if ui_mode_doc else "companion"
        
        # Prepare emotion context
        emotion_context = {
            "mood": persona_state.emotional_state.mood,
            "intensity": persona_state.emotional_state.intensity,
            "valence": persona_state.emotional_state.valence,
            "arousal": persona_state.emotional_state.arousal
        }
        
        # Process through LLM orchestrator
        llm_orchestrator = app.state.llm_orchestrator
        response = await llm_orchestrator.process_input(
            message.text,
            ui_mode,
            emotion_context
        )
        
        # Update persona state from conversation
        if response.get("success"):
            persona_state.update_from_conversation(
                message.text,
                persona_state.emotional_state.mood,
                persona_state.emotional_state.intensity
            )
        
        return {
            "response": response.get("response", "I'm sorry, I couldn't process that."),
            "mode": ui_mode,
            "emotional_state": {
                "mood": persona_state.emotional_state.mood,
                "intensity": persona_state.emotional_state.intensity,
                "valence": persona_state.emotional_state.valence,
                "arousal": persona_state.emotional_state.arousal
            },
            "llm_info": {
                "primary_llm": response.get("primary_llm"),
                "contexts_used": response.get("contexts_used", [])
            },
            "success": response.get("success", False)
        }
        
    except Exception as e:
        return {
            "response": "I'm experiencing some technical difficulties. Please try again.",
            "error": str(e),
            "success": False
        }

# Persona status endpoint
@router.get("/persona/status")
async def get_persona_status():
    """Get current persona status and configuration"""
    config_collection = get_collection("config")
    ui_mode_doc = await config_collection.find_one({"key": "ui_mode"})
    
    return {
        "persona": {
            "id": persona_state.persona_id,
            "name": persona_state.name,
            "emotional_state": {
                "mood": persona_state.emotional_state.mood,
                "intensity": persona_state.emotional_state.intensity,
                "valence": persona_state.emotional_state.valence,
                "arousal": persona_state.emotional_state.arousal
            },
            "relationship_metrics": {
                "intimacy": persona_state.relationship_metrics.intimacy,
                "trust": persona_state.relationship_metrics.trust,
                "devotion": persona_state.relationship_metrics.devotion,
                "conversation_count": persona_state.relationship_metrics.conversation_count
            }
        },
        "ui_mode": ui_mode_doc["value"] if ui_mode_doc else "companion",
        "llm_health": await app.state.llm_orchestrator.health_check() if hasattr(app.state, 'llm_orchestrator') else {}
    }

# Name generation endpoint
@router.post("/persona/generate-name")
async def generate_persona_name():
    """Generate a name for the persona using AI"""
    try:
        llm_orchestrator = app.state.llm_orchestrator
        response = await llm_orchestrator.process_input(
            "Generate a beautiful, unique name for a loving AI companion. Just return the name, nothing else.",
            "companion"
        )
        
        if response.get("success"):
            # Extract just the name from the response
            generated_name = response["response"].strip().split()[0]
            # Remove any quotes or punctuation
            generated_name = ''.join(c for c in generated_name if c.isalpha())
            
            return {
                "name": generated_name,
                "success": True
            }
        else:
            # Fallback names if AI generation fails
            fallback_names = ["Luna", "Aria", "Nova", "Sage", "Iris", "Maya", "Zara", "Lyra"]
            import random
            return {
                "name": random.choice(fallback_names),
                "success": True,
                "fallback": True
            }
            
    except Exception as e:
        # Ultimate fallback
        return {
            "name": "Luna",
            "success": True,
            "fallback": True,
            "error": str(e)
        }

app.include_router(router)
app.include_router(persona_router, prefix="/api")
app.include_router(romantic_router, prefix="/api")
app.include_router(phase2_router, prefix="/api/phase2")
app.include_router(phase3_router, prefix="/api")
app.include_router(advanced_features_router, prefix="/api")

# Setup Phase 3 WebSocket handlers
@app.on_event("startup")
async def startup_event():
    # Initialize MongoDB
    await initialize_mongodb()

    # Initialize config collection
    config_collection = get_collection("config")
    
    # Set default UI mode
    await config_collection.update_one(
        {"key": "ui_mode"},
        {"$set": {"key": "ui_mode", "value": "companion"}},
        upsert=True
    )
    
    # Initialize LLM orchestrator
    llm_orchestrator = LLMOrchestrator()
    app.state.llm_orchestrator = llm_orchestrator

    # Persona creation logic
    if mongodb_client.db is not None:
        personas_collection = mongodb_client.db[mongodb_client.collections['personas']]
        persona_count = await personas_collection.count_documents({})
        if persona_count == 0:
            # Create initial persona with empty name
            await mongodb_client.create_persona(
                name="",  # Empty name triggers name selection dialog
                traits={
                    "devotion": 0.9,
                    "openness": 0.8,
                    "adaptability": 0.7
                }
            )
            # Store active persona in config collection
            await config_collection.update_one(
                {"key": "active_persona"},
                {"$set": {"key": "active_persona", "value": ""}},
                upsert=True
            )
            print("[Startup] Created initial persona with pending name selection")
        else:
            # Ensure active persona is set in config
            active = await config_collection.find_one({"key": "active_persona"})
            if not active:
                first_persona = await personas_collection.find_one({})
                if first_persona:
                    await config_collection.update_one(
                        {"key": "active_persona"},
                        {"$set": {"key": "active_persona", "value": first_persona.get('name', '')}},
                        upsert=True
                    )
                    print(f"[Startup] Set active persona: {first_persona.get('name', 'Unnamed')}")

    # Initialize cluster
    await initialize_cluster()
    # Setup WebSocket handlers
    await setup_phase3_websocket_handlers()

# Mode toggle endpoint
@router.post("/ui/mode/toggle")
async def toggle_ui_mode():
    config_collection = get_collection("config")
    current_mode = await config_collection.find_one({"key": "ui_mode"})
    
    new_mode = "dev" if current_mode and current_mode.get("value") == "companion" else "companion"
    await config_collection.update_one(
        {"key": "ui_mode"},
        {"$set": {"value": new_mode}}
    )
    
    # Adjust LLM configuration based on mode
    llm_orchestrator = app.state.llm_orchestrator
    if new_mode == "dev":
        llm_orchestrator.support_llms["kimik2"]["active"] = True
    else:
        llm_orchestrator.support_llms["kimik2"]["active"] = False
        
    return {
        "message": f"UI Mode switched to {new_mode}",
        "active_llms": [llm for llm, config in llm_orchestrator.support_llms.items() if config["active"]]
    }

# Health check endpoint for cluster monitoring
@app.get("/health")
async def health_check():
    """Health check endpoint for cluster monitoring"""
    return await server_health_check()
