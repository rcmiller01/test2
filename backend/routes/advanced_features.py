# advanced_features.py
# API routes for advanced features including symbolic fusion, scene initiation, touch journal, and dynamic wake word

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
import json
import logging
from datetime import datetime

# Import the new feature engines
from symbolic.symbolic_fusion import symbolic_fusion, Symbol, TouchType, TouchLocation
from scenes.scene_initiation import scene_initiation_engine, TouchEvent
from input.touch_journal import touch_journal_engine, TouchType as JournalTouchType, TouchLocation as JournalTouchLocation
from input.dynamic_wake_word import dynamic_wake_word_engine, WakeContext, TimeContext, EnvironmentContext, WakeMode

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/advanced", tags=["Advanced Features"])

# ============================================================================
# Symbolic Fusion Routes
# ============================================================================

@router.post("/symbolic/activate")
async def activate_symbol(symbol_name: str, intensity: float = 1.0, user_id: str = "default"):
    """Activate a symbol with given intensity"""
    try:
        success = await symbolic_fusion.activate_symbol(symbol_name, intensity)
        if success:
            return {
                "status": "success",
                "message": f"Activated symbol: {symbol_name}",
                "symbol": symbol_name,
                "intensity": intensity
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to activate symbol: {symbol_name}")
    except Exception as e:
        logger.error(f"Error activating symbol: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/symbolic/deactivate")
async def deactivate_symbol(symbol_name: str, user_id: str = "default"):
    """Deactivate a symbol"""
    try:
        success = await symbolic_fusion.deactivate_symbol(symbol_name)
        if success:
            return {
                "status": "success",
                "message": f"Deactivated symbol: {symbol_name}",
                "symbol": symbol_name
            }
        else:
            return {
                "status": "warning",
                "message": f"Symbol {symbol_name} was not active"
            }
    except Exception as e:
        logger.error(f"Error deactivating symbol: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/symbolic/fusion-possibilities")
async def get_fusion_possibilities(user_id: str = "default"):
    """Get possible symbol fusions based on active symbols"""
    try:
        possibilities = await symbolic_fusion.check_fusion_possibilities()
        return {
            "status": "success",
            "possibilities": possibilities,
            "count": len(possibilities)
        }
    except Exception as e:
        logger.error(f"Error getting fusion possibilities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/symbolic/create-fusion")
async def create_fusion(symbol1: str, symbol2: str, user_id: str = "default"):
    """Create a fusion between two symbols"""
    try:
        fusion_result = await symbolic_fusion.create_fusion(symbol1, symbol2)
        if fusion_result:
            return {
                "status": "success",
                "fusion": fusion_result,
                "message": f"Created fusion: {fusion_result['name']}"
            }
        else:
            raise HTTPException(status_code=400, detail=f"No fusion rule found for {symbol1} + {symbol2}")
    except Exception as e:
        logger.error(f"Error creating fusion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/symbolic/mood-state")
async def get_mood_state(user_id: str = "default"):
    """Get current mood state based on active symbols and fusions"""
    try:
        mood_state = await symbolic_fusion.get_current_mood_state()
        return {
            "status": "success",
            "mood_state": mood_state
        }
    except Exception as e:
        logger.error(f"Error getting mood state: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/symbolic/available-symbols")
async def get_available_symbols():
    """Get all available symbols"""
    try:
        symbols = {}
        for name, symbol in symbolic_fusion.symbols.items():
            symbols[name] = {
                "name": symbol.name,
                "type": symbol.symbol_type.value,
                "emotional_weight": symbol.emotional_weight,
                "intensity": symbol.intensity,
                "associations": symbol.associations,
                "visual_representation": symbol.visual_representation
            }
        return {
            "status": "success",
            "symbols": symbols,
            "count": len(symbols)
        }
    except Exception as e:
        logger.error(f"Error getting available symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Scene Initiation Routes
# ============================================================================

@router.post("/scenes/analyze-text")
async def analyze_text_for_scene(text: str, current_persona: str = "mia", user_id: str = "default"):
    """Analyze text and determine appropriate scene response"""
    try:
        scene_prompt = await scene_initiation_engine.analyze_text_for_scene(text, current_persona)
        if scene_prompt:
            return {
                "status": "success",
                "scene_prompt": {
                    "scene_type": scene_prompt.scene_type.value,
                    "emotion_intensity": scene_prompt.emotion_intensity.value,
                    "text_prompt": scene_prompt.text_prompt,
                    "visual_elements": scene_prompt.visual_elements,
                    "audio_elements": scene_prompt.audio_elements,
                    "haptic_patterns": scene_prompt.haptic_patterns,
                    "duration_seconds": scene_prompt.duration_seconds,
                    "persona_modifications": scene_prompt.persona_modifications
                }
            }
        else:
            return {
                "status": "no_scene",
                "message": "No strong emotions detected for scene generation"
            }
    except Exception as e:
        logger.error(f"Error analyzing text for scene: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scenes/generate")
async def generate_video_scene(text: str, current_persona: str = "mia", user_id: str = "default"):
    """Generate a video scene based on text input"""
    try:
        # First analyze the text
        scene_prompt = await scene_initiation_engine.analyze_text_for_scene(text, current_persona)
        if not scene_prompt:
            raise HTTPException(status_code=400, detail="No scene could be generated from the text")
        
        # Generate the video scene
        scene_config = await scene_initiation_engine.generate_video_scene(scene_prompt, user_id)
        
        return {
            "status": "success",
            "scene_config": scene_config,
            "message": f"Scene generation started: {scene_config.get('scene_id', 'unknown')}"
        }
    except Exception as e:
        logger.error(f"Error generating video scene: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scenes/status/{scene_id}")
async def get_scene_status(scene_id: str, user_id: str = "default"):
    """Get the status of a scene generation"""
    try:
        scene_status = await scene_initiation_engine.get_scene_status(scene_id)
        if scene_status:
            return {
                "status": "success",
                "scene_status": scene_status
            }
        else:
            raise HTTPException(status_code=404, detail=f"Scene {scene_id} not found")
    except Exception as e:
        logger.error(f"Error getting scene status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scenes/user-scenes")
async def get_user_scenes(user_id: str = "default"):
    """Get all scenes for a user"""
    try:
        user_scenes = await scene_initiation_engine.get_user_scenes(user_id)
        return {
            "status": "success",
            "scenes": user_scenes,
            "count": len(user_scenes)
        }
    except Exception as e:
        logger.error(f"Error getting user scenes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scenes/create-memory/{scene_id}")
async def create_scene_memory(scene_id: str, user_id: str = "default"):
    """Create a memory entry for a generated scene"""
    try:
        memory_id = await scene_initiation_engine.create_scene_memory(scene_id, user_id)
        if memory_id:
            return {
                "status": "success",
                "memory_id": memory_id,
                "message": f"Created memory for scene: {scene_id}"
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to create memory for scene: {scene_id}")
    except Exception as e:
        logger.error(f"Error creating scene memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Touch Journal Routes
# ============================================================================

@router.post("/touch/process-event")
async def process_touch_event(
    touch_type: str,
    location: str,
    duration_ms: int,
    intensity: float,
    pressure: float,
    persona: str = "mia",
    user_id: str = "default"
):
    """Process a touch event and generate a journal entry"""
    try:
        # Convert string inputs to enums
        try:
            touch_type_enum = JournalTouchType(touch_type)
            location_enum = JournalTouchLocation(location)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid touch type or location: {e}")
        
        # Create touch event
        touch_event = TouchEvent(
            touch_type=touch_type_enum,
            location=location_enum,
            duration_ms=duration_ms,
            intensity=intensity,
            pressure=pressure,
            timestamp=datetime.now(),
            context={"user_id": user_id, "persona": persona}
        )
        
        # Process the touch event
        journal_entry = await touch_journal_engine.process_touch_event(touch_event, user_id, persona)
        
        if journal_entry:
            return {
                "status": "success",
                "journal_entry": journal_entry,
                "message": f"Created touch journal entry: {journal_entry['title']}"
            }
        else:
            return {
                "status": "no_pattern",
                "message": "No recognizable touch pattern detected"
            }
    except Exception as e:
        logger.error(f"Error processing touch event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/touch/history")
async def get_touch_history(user_id: str = "default", limit: int = 50):
    """Get touch history for a user"""
    try:
        touch_history = await touch_journal_engine.get_touch_history(user_id, limit)
        return {
            "status": "success",
            "touch_history": touch_history,
            "count": len(touch_history)
        }
    except Exception as e:
        logger.error(f"Error getting touch history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/touch/patterns")
async def get_touch_patterns(user_id: str = "default"):
    """Analyze touch patterns for a user"""
    try:
        patterns = await touch_journal_engine.get_touch_patterns(user_id)
        return {
            "status": "success",
            "patterns": patterns
        }
    except Exception as e:
        logger.error(f"Error analyzing touch patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Dynamic Wake Word Routes
# ============================================================================

@router.post("/wake-word/analyze-context")
async def analyze_wake_context(
    time_context: str,
    environment: str,
    user_mood: str,
    persona_state: str,
    trust_level: float,
    privacy_level: float,
    noise_level: float
):
    """Analyze context and determine appropriate wake mode"""
    try:
        # Convert string inputs to enums
        try:
            time_enum = TimeContext(time_context)
            env_enum = EnvironmentContext(environment)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid time context or environment: {e}")
        
        # Create wake context
        wake_context = WakeContext(
            time_context=time_enum,
            environment=env_enum,
            user_mood=user_mood,
            persona_state=persona_state,
            trust_level=trust_level,
            privacy_level=privacy_level,
            noise_level=noise_level
        )
        
        # Analyze context
        selected_mode = await dynamic_wake_word_engine.analyze_context(wake_context)
        
        return {
            "status": "success",
            "selected_mode": selected_mode.value,
            "context": {
                "time": time_context,
                "environment": environment,
                "user_mood": user_mood,
                "privacy_level": privacy_level,
                "noise_level": noise_level
            }
        }
    except Exception as e:
        logger.error(f"Error analyzing wake context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/wake-word/current-word")
async def get_current_wake_word(persona: str = "mia"):
    """Get current wake word for the active mode"""
    try:
        wake_word = await dynamic_wake_word_engine.get_wake_word(persona)
        mode_config = await dynamic_wake_word_engine.get_mode_configuration()
        
        return {
            "status": "success",
            "wake_word": wake_word,
            "mode": mode_config["mode"].value,
            "description": mode_config["description"],
            "sensitivity": mode_config["sensitivity"]
        }
    except Exception as e:
        logger.error(f"Error getting wake word: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/wake-word/mode-configuration")
async def get_mode_configuration():
    """Get current mode configuration"""
    try:
        mode_config = await dynamic_wake_word_engine.get_mode_configuration()
        return {
            "status": "success",
            "mode_configuration": mode_config
        }
    except Exception as e:
        logger.error(f"Error getting mode configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/wake-word/persona-modifications")
async def get_persona_modifications():
    """Get persona modifications for current mode"""
    try:
        modifications = await dynamic_wake_word_engine.get_persona_modifications()
        return {
            "status": "success",
            "persona_modifications": modifications
        }
    except Exception as e:
        logger.error(f"Error getting persona modifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/wake-word/check-response")
async def check_wake_word_response(wake_word: str, confidence: float):
    """Check if system should respond to wake word"""
    try:
        should_respond = await dynamic_wake_word_engine.should_respond_to_wake_word(wake_word, confidence)
        response_behavior = await dynamic_wake_word_engine.get_response_behavior()
        
        return {
            "status": "success",
            "should_respond": should_respond,
            "confidence": confidence,
            "response_behavior": response_behavior
        }
    except Exception as e:
        logger.error(f"Error checking wake word response: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/wake-word/mode-history")
async def get_mode_history(limit: int = 20):
    """Get recent mode change history"""
    try:
        history = await dynamic_wake_word_engine.get_mode_history(limit)
        return {
            "status": "success",
            "mode_history": history,
            "count": len(history)
        }
    except Exception as e:
        logger.error(f"Error getting mode history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/wake-word/force-mode")
async def force_mode_change(new_mode: str):
    """Force a mode change"""
    try:
        try:
            mode_enum = WakeMode(new_mode)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid mode: {new_mode}")
        
        success = await dynamic_wake_word_engine.force_mode_change(mode_enum)
        
        if success:
            return {
                "status": "success",
                "message": f"Forced mode change to: {new_mode}"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to change mode")
    except Exception as e:
        logger.error(f"Error forcing mode change: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Combined Advanced Features Routes
# ============================================================================

@router.get("/status")
async def get_advanced_features_status():
    """Get status of all advanced features"""
    try:
        # Get current states
        mood_state = await symbolic_fusion.get_current_mood_state()
        mode_config = await dynamic_wake_word_engine.get_mode_configuration()
        
        return {
            "status": "success",
            "advanced_features": {
                "symbolic_fusion": {
                    "active_symbols": len(symbolic_fusion.active_symbols),
                    "recent_fusions": len(mood_state.get("active_fusions", [])),
                    "current_mood": mood_state.get("mood_description", "neutral")
                },
                "scene_initiation": {
                    "active_scenes": len(scene_initiation_engine.active_scenes),
                    "status": "operational"
                },
                "touch_journal": {
                    "total_entries": len(touch_journal_engine.journal_entries),
                    "status": "operational"
                },
                "dynamic_wake_word": {
                    "current_mode": mode_config["mode"].value,
                    "mode_history_count": len(dynamic_wake_word_engine.mode_history),
                    "status": "operational"
                }
            }
        }
    except Exception as e:
        logger.error(f"Error getting advanced features status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/integrated-response")
async def integrated_response(
    text: str,
    touch_data: Optional[Dict] = None,
    context_data: Optional[Dict] = None,
    user_id: str = "default",
    persona: str = "mia"
):
    """Integrated response combining multiple advanced features"""
    try:
        response = {
            "status": "success",
            "features": {}
        }
        
        # 1. Analyze text for scene initiation
        if text:
            scene_prompt = await scene_initiation_engine.analyze_text_for_scene(text, persona)
            if scene_prompt:
                response["features"]["scene_initiation"] = {
                    "triggered": True,
                    "scene_type": scene_prompt.scene_type.value,
                    "emotion_intensity": scene_prompt.emotion_intensity.value
                }
            else:
                response["features"]["scene_initiation"] = {"triggered": False}
        
        # 2. Process touch event if provided
        if touch_data:
            try:
                touch_event = TouchEvent(
                    touch_type=JournalTouchType(touch_data["type"]),
                    location=JournalTouchLocation(touch_data["location"]),
                    duration_ms=touch_data["duration_ms"],
                    intensity=touch_data["intensity"],
                    pressure=touch_data["pressure"],
                    timestamp=datetime.now(),
                    context={"user_id": user_id, "persona": persona}
                )
                
                journal_entry = await touch_journal_engine.process_touch_event(touch_event, user_id, persona)
                response["features"]["touch_journal"] = {
                    "processed": True,
                    "entry_created": journal_entry is not None
                }
            except Exception as e:
                response["features"]["touch_journal"] = {
                    "processed": False,
                    "error": str(e)
                }
        
        # 3. Update wake word context if provided
        if context_data:
            try:
                wake_context = WakeContext(
                    time_context=TimeContext(context_data["time_context"]),
                    environment=EnvironmentContext(context_data["environment"]),
                    user_mood=context_data["user_mood"],
                    persona_state=context_data["persona_state"],
                    trust_level=context_data["trust_level"],
                    privacy_level=context_data["privacy_level"],
                    noise_level=context_data["noise_level"]
                )
                
                selected_mode = await dynamic_wake_word_engine.analyze_context(wake_context)
                response["features"]["dynamic_wake_word"] = {
                    "mode_updated": True,
                    "selected_mode": selected_mode.value
                }
            except Exception as e:
                response["features"]["dynamic_wake_word"] = {
                    "mode_updated": False,
                    "error": str(e)
                }
        
        # 4. Get current mood state
        mood_state = await symbolic_fusion.get_current_mood_state()
        response["features"]["symbolic_fusion"] = {
            "current_mood": mood_state.get("mood_description", "neutral"),
            "active_symbols": len(symbolic_fusion.active_symbols)
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error in integrated response: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 