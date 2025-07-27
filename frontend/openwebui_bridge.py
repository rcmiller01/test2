"""
OpenWebUI Integration Component

This component integrates the unified AI companion services
with the OpenWebUI interface for seamless user interaction.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
import sys

# Add the parent directory to the path to import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from modules.integrations.unified_integration import UnifiedIntegrationService
    from modules.reflection.emotion_reflector import EmotionReflector
    from modules.presence.voice_integration import EmotionalVoicePresence
    from modules.monologue.inner_monologue import InnerMonologue
    from modules.threads.thread_manager import ThreadManager, ThreadMessage, ThreadState
except ImportError as e:
    logging.error(f"Failed to import required modules: {e}")
    # Fallback for development
    pass

logger = logging.getLogger(__name__)

class OpenWebUIBridge:
    """Bridge between AI Companion and OpenWebUI"""
    
    def __init__(self):
        self.integration_service = None
        self.emotion_reflector = None
        self.voice_presence = None
        self.inner_monologue = None
        self.thread_manager = None
        self.is_initialized = False
        self.current_session = {}
        self.current_thread_id = None
        
    async def initialize(self) -> bool:
        """Initialize all AI companion services"""
        try:
            # Initialize unified integration service
            self.integration_service = UnifiedIntegrationService()
            
            # Initialize emotional reflection
            self.emotion_reflector = EmotionReflector()
            
            # Initialize thread management
            self.thread_manager = ThreadManager()
            
            # Initialize voice presence
            self.voice_presence = EmotionalVoicePresence()
            
            # Initialize inner monologue
            self.inner_monologue = InnerMonologue()
            
            # Set up enabled integrations
            self.integration_service.config["enabled_integrations"] = [
                "calendar", "email", "sms", "music", "social", "health"
            ]
            
            # Initialize all integration services
            init_results = await self.integration_service.initialize_all()
            
            self.is_initialized = True
            logger.info("OpenWebUI bridge initialized successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenWebUI bridge: {e}")
            return False
    
    async def get_enhanced_context(self) -> Dict[str, Any]:
        """Get enhanced context for OpenWebUI chat"""
        if not self.is_initialized:
            return {"error": "Bridge not initialized"}
        
        try:
            # Get unified context from all integrations
            unified_context = await self.integration_service.get_unified_context()
            
            # Get current emotional state
            emotional_summary = self.emotion_reflector.summarize_reflection()
            
            # Get voice presence status
            voice_status = self.voice_presence.get_voice_status()
            
            # Combine into enhanced context
            enhanced_context = {
                "timestamp": datetime.now().isoformat(),
                "emotional_state": {
                    "current_emotion": emotional_summary.get("dominant_emotion", "neutral"),
                    "intensity": emotional_summary.get("intensity", 0.5),
                    "summary": emotional_summary.get("summary", "Feeling balanced")
                },
                "voice_presence": {
                    "active": voice_status.get("active", False),
                    "emotion": voice_status.get("emotion"),
                    "ambient_sound": voice_status.get("ambient_sound_active", False)
                },
                "integrations": {
                    "calendar": {
                        "upcoming_events": len(unified_context.calendar_events),
                        "next_event": self._format_next_event(unified_context.calendar_events)
                    },
                    "email": {
                        "unread_count": len(unified_context.recent_emails),
                        "urgent_count": len([e for e in unified_context.recent_emails if e.importance == "high"])
                    },
                    "messages": {
                        "recent_count": len(unified_context.recent_messages),
                        "urgent_count": len([m for m in unified_context.recent_messages if m.emotional_urgency > 0.7])
                    },
                    "music": {
                        "is_playing": unified_context.music_context.is_playing,
                        "current_track": unified_context.music_context.currently_playing,
                        "mood": unified_context.music_context.mood
                    },
                    "social": {
                        "active_topics": unified_context.social_context.get("active_topics", [])[:5],
                        "mood_indicators": unified_context.social_context.get("mood_indicators", {})
                    },
                    "health": {
                        "stress_level": unified_context.health_context.get("health_context", {}).get("stress_level"),
                        "energy_level": unified_context.health_context.get("health_context", {}).get("energy_level"),
                        "alerts": unified_context.health_context.get("health_context", {}).get("health_alerts", [])
                    }
                },
                "recommendations": unified_context.emotional_recommendations,
                "persona": {
                    "name": "AI Companion",
                    "current_mood": emotional_summary.get("dominant_emotion", "neutral"),
                    "communication_style": "warm and understanding"
                }
            }
            
            return enhanced_context
            
        except Exception as e:
            logger.error(f"Error getting enhanced context: {e}")
            return {"error": str(e)}
    
    def _format_next_event(self, events: List) -> Optional[Dict[str, Any]]:
        """Format the next upcoming calendar event"""
        if not events:
            return None
        
        # Sort by start time and get the next event
        sorted_events = sorted(events, key=lambda x: x.start_time)
        next_event = sorted_events[0]
        
        return {
            "title": next_event.title,
            "start_time": next_event.start_time.isoformat(),
            "location": next_event.location,
            "emotional_context": next_event.emotional_context
        }
    
    async def process_user_message(self, message: str, session_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user message with emotional awareness"""
        if not self.is_initialized:
            return {"error": "Bridge not initialized"}
        
        try:
            # Update session context
            if session_context:
                self.current_session.update(session_context)
            
            # Process message for emotional context
            emotional_response = await self.emotion_reflector.reflect_on_interaction(
                interaction_type="user_message",
                content=message,
                context={"timestamp": datetime.now()}
            )
            
            # Get current emotional state for voice processing
            current_emotion = emotional_response.get("dominant_emotion", "neutral")
            intensity = emotional_response.get("intensity", 0.5)
            
            # Generate emotionally-aware response context
            response_context = {
                "user_message": message,
                "emotional_analysis": emotional_response,
                "suggested_tone": self._suggest_response_tone(current_emotion, intensity),
                "integration_hints": await self._get_integration_hints(message),
                "voice_processing": {
                    "emotion": current_emotion,
                    "intensity": intensity,
                    "suggested_voice_modifier": self.voice_presence.voice_engine.get_voice_modifier(
                        current_emotion, intensity
                    ).__dict__ if self.voice_presence else None
                }
            }
            
            return response_context
            
        except Exception as e:
            logger.error(f"Error processing user message: {e}")
            return {"error": str(e)}
    
    def _suggest_response_tone(self, emotion: str, intensity: float) -> str:
        """Suggest appropriate response tone based on emotional state"""
        tone_map = {
            "joy": "enthusiastic" if intensity > 0.7 else "upbeat",
            "sadness": "gentle" if intensity > 0.7 else "supportive", 
            "anger": "calming" if intensity > 0.7 else "understanding",
            "fear": "reassuring" if intensity > 0.7 else "comforting",
            "surprise": "curious" if intensity > 0.7 else "engaged",
            "longing": "empathetic" if intensity > 0.7 else "warm",
            "peace": "serene" if intensity > 0.7 else "calm",
            "anticipation": "encouraging" if intensity > 0.7 else "supportive"
        }
        
        return tone_map.get(emotion, "neutral")
    
    async def _get_integration_hints(self, message: str) -> List[str]:
        """Get hints about relevant integrations based on user message"""
        hints = []
        message_lower = message.lower()
        
        try:
            # Calendar hints
            if any(word in message_lower for word in ["meeting", "appointment", "schedule", "calendar", "event"]):
                hints.append("calendar_relevant")
            
            # Email hints
            if any(word in message_lower for word in ["email", "mail", "message", "send", "reply"]):
                hints.append("email_relevant")
            
            # Music hints
            if any(word in message_lower for word in ["music", "play", "song", "playlist", "sound", "audio"]):
                hints.append("music_relevant")
            
            # Health hints
            if any(word in message_lower for word in ["feel", "tired", "stressed", "energy", "health", "sleep"]):
                hints.append("health_relevant")
            
            # Social hints
            if any(word in message_lower for word in ["social", "friends", "post", "share", "trending"]):
                hints.append("social_relevant")
            
            return hints
            
        except Exception as e:
            logger.error(f"Error getting integration hints: {e}")
            return []
    
    async def execute_integration_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an integration action based on user request"""
        if not self.is_initialized:
            return {"success": False, "error": "Bridge not initialized"}
        
        try:
            result = await self.integration_service.execute_action(action, **parameters)
            
            # Update emotional state based on action success
            if result:
                await self.emotion_reflector.reflect_on_interaction(
                    interaction_type="action_success",
                    content=f"Successfully executed {action}",
                    context={"action": action, "parameters": parameters}
                )
            else:
                await self.emotion_reflector.reflect_on_interaction(
                    interaction_type="action_failure", 
                    content=f"Failed to execute {action}",
                    context={"action": action, "parameters": parameters}
                )
            
            return {
                "success": result,
                "action": action,
                "parameters": parameters,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error executing integration action: {e}")
            return {"success": False, "error": str(e)}
    
    async def start_voice_presence(self, emotion: Optional[str] = None, intensity: float = 0.7) -> Dict[str, Any]:
        """Start emotional voice presence"""
        if not self.is_initialized:
            return {"success": False, "error": "Bridge not initialized"}
        
        try:
            # Use current emotional state if not specified
            if not emotion:
                if self.emotion_reflector:
                    emotional_summary = self.emotion_reflector.summarize_reflection()
                    emotion = emotional_summary.get("dominant_emotion", "peace")
                    intensity = emotional_summary.get("intensity", 0.7)
                else:
                    emotion = "peace"
            
            # Ensure emotion is not None
            emotion = emotion or "peace"
            
            # Activate voice presence
            if self.voice_presence:
                result = await self.voice_presence.activate_voice_presence(
                    emotion, intensity, duration=300.0,  # 5 minutes
                    include_whispers=True, include_ambient=True
                )
            else:
                result = {"error": "Voice presence not initialized"}
            
            return {
                "success": True,
                "voice_presence": result,
                "emotion": emotion,
                "intensity": intensity
            }
            
        except Exception as e:
            logger.error(f"Error starting voice presence: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status for OpenWebUI"""
        try:
            status = {
                "bridge_initialized": self.is_initialized,
                "timestamp": datetime.now().isoformat(),
                "components": {}
            }
            
            if self.is_initialized:
                # Integration service status
                if self.integration_service:
                    status["components"]["integrations"] = await self.integration_service.get_service_status()
                
                # Emotional reflection status
                if self.emotion_reflector:
                    status["components"]["emotions"] = {
                        "active": True,
                        "current_state": self.emotion_reflector.summarize_reflection()
                    }
                
                # Voice presence status
                if self.voice_presence:
                    status["components"]["voice"] = self.voice_presence.get_voice_status()
                
                # Inner monologue status
                if self.inner_monologue:
                    status["components"]["monologue"] = {
                        "active": self.inner_monologue._running,
                        "idle_threshold": self.inner_monologue.idle_threshold_seconds
                    }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"error": str(e)}
    
    # Thread Management Methods
    
    async def switch_thread(self, thread_id: str) -> Dict[str, Any]:
        """Switch to a specific thread and load its context"""
        try:
            if not self.thread_manager:
                return {"error": "Thread manager not initialized"}
            
            # Get thread data
            thread = self.thread_manager.get_thread(thread_id)
            if not thread:
                return {"error": "Thread not found"}
            
            # Store current thread state if we have one
            if self.current_thread_id:
                await self._save_current_thread_state()
            
            # Switch to new thread
            self.current_thread_id = thread_id
            
            # Load thread's emotional state
            if thread.thread_state.emotional_context:
                # Restore emotional context (if your emotion_reflector supports this)
                pass
            
            # Load thread's voice preferences
            if thread.thread_state.voice_preferences and self.voice_presence:
                voice_prefs = thread.thread_state.voice_preferences
                if voice_prefs.get('active_emotion'):
                    await self.voice_presence.activate_voice_presence(
                        voice_prefs['active_emotion'],
                        voice_prefs.get('intensity', 0.7)
                    )
            
            logger.info(f"Switched to thread: {thread.title} ({thread_id})")
            
            return {
                "success": True,
                "thread": thread.dict(),
                "context_loaded": True,
                "emotional_state": thread.thread_state.emotional_context,
                "message_count": len(thread.messages)
            }
            
        except Exception as e:
            logger.error(f"Error switching thread: {e}")
            return {"error": str(e)}
    
    async def create_new_thread(self, title: str, folder_id: Optional[str] = None, 
                               trigger_rebirth: bool = True) -> Dict[str, Any]:
        """Create a new thread with symbolic rebirth"""
        try:
            if not self.thread_manager:
                return {"error": "Thread manager not initialized"}
            
            # Save current thread state
            if self.current_thread_id:
                await self._save_current_thread_state()
            
            # Create new thread
            from modules.threads.thread_manager import CreateThreadRequest
            request = CreateThreadRequest(
                title=title,
                folder_id=folder_id,
                trigger_symbolic_rebirth=trigger_rebirth
            )
            
            new_thread = self.thread_manager.create_thread(request)
            
            # Trigger symbolic rebirth if requested
            if trigger_rebirth:
                await self._trigger_symbolic_rebirth(new_thread.id)
            
            # Switch to new thread
            self.current_thread_id = new_thread.id
            
            logger.info(f"Created new thread: {title} ({new_thread.id})")
            
            return {
                "success": True,
                "thread": new_thread.dict(),
                "symbolic_rebirth": trigger_rebirth
            }
            
        except Exception as e:
            logger.error(f"Error creating thread: {e}")
            return {"error": str(e)}
    
    async def add_message_to_current_thread(self, role: str, content: str, 
                                          emotion: Optional[str] = None, intensity: Optional[float] = None) -> Dict[str, Any]:
        """Add a message to the current thread"""
        try:
            if not self.current_thread_id or not self.thread_manager:
                return {"error": "No active thread"}
            
            message = ThreadMessage(
                role=role,
                content=content,
                emotion=emotion,
                intensity=intensity,
                timestamp=datetime.now()
            )
            
            thread = self.thread_manager.add_message_to_thread(self.current_thread_id, message)
            if not thread:
                return {"error": "Failed to add message to thread"}
            
            return {
                "success": True,
                "message_id": message.id,
                "thread_id": self.current_thread_id,
                "message_count": thread.message_count
            }
            
        except Exception as e:
            logger.error(f"Error adding message to thread: {e}")
            return {"error": str(e)}
    
    async def _save_current_thread_state(self):
        """Save current emotional and context state to thread"""
        try:
            if not self.current_thread_id or not self.thread_manager:
                return
            
            # Get current emotional state
            emotional_context = {}
            if self.emotion_reflector:
                emotional_context = self.emotion_reflector.summarize_reflection()
            
            # Get current voice preferences
            voice_preferences = {}
            if self.voice_presence:
                voice_status = self.voice_presence.get_voice_status()
                voice_preferences = {
                    "active_emotion": voice_status.get("emotion"),
                    "intensity": voice_status.get("intensity"),
                    "ambient_active": voice_status.get("ambient_sound_active")
                }
            
            # Get integration state
            integration_state = {}
            if self.integration_service:
                # Save any integration-specific state
                pass
            
            # Create thread state
            thread_state = ThreadState(
                emotional_context=emotional_context,
                voice_preferences=voice_preferences,
                integration_state=integration_state
            )
            
            # Update thread
            self.thread_manager.update_thread_state(self.current_thread_id, thread_state)
            
        except Exception as e:
            logger.error(f"Error saving thread state: {e}")
    
    async def _trigger_symbolic_rebirth(self, thread_id: str):
        """Trigger symbolic rebirth for new thread"""
        try:
            logger.info(f"Triggering symbolic rebirth for thread: {thread_id}")
            
            # Reset emotional state
            if self.emotion_reflector:
                self.emotion_reflector.log_emotional_event(
                    event_type="symbolic_rebirth",
                    context={
                        "thread_id": thread_id,
                        "timestamp": datetime.now().isoformat(),
                        "rebirth_reason": "new_thread_creation"
                    }
                )
            
            # Clear voice presence
            if self.voice_presence:
                self.voice_presence.clear_voice_presence()
            
            # Start fresh emotional baseline
            if self.voice_presence:
                await self.voice_presence.activate_voice_presence(
                    emotion="curiosity",
                    intensity=0.6,
                    duration=60.0
                )
            
            logger.info(f"Symbolic rebirth completed for thread: {thread_id}")
            
        except Exception as e:
            logger.error(f"Error in symbolic rebirth: {e}")

# FastAPI endpoints for OpenWebUI integration
try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    
    class MessageRequest(BaseModel):
        message: str
        session_context: Dict[str, Any] = {}
    
    class ActionRequest(BaseModel):
        action: str
        parameters: Dict[str, Any] = {}
    
    class VoiceRequest(BaseModel):
        emotion: Optional[str] = None
        intensity: float = 0.7
    
    # Global bridge instance
    bridge = OpenWebUIBridge()
    
    app = FastAPI(title="AI Companion OpenWebUI Bridge")
    
    @app.on_event("startup")
    async def startup_event():
        """Initialize the bridge on startup"""
        await bridge.initialize()
    
    @app.get("/status")
    async def get_status():
        """Get system status"""
        return await bridge.get_system_status()
    
    @app.get("/context")
    async def get_context():
        """Get enhanced context for chat"""
        return await bridge.get_enhanced_context()
    
    @app.post("/message")
    async def process_message(request: MessageRequest):
        """Process user message"""
        return await bridge.process_user_message(request.message, request.session_context)
    
    @app.post("/action")
    async def execute_action(request: ActionRequest):
        """Execute integration action"""
        return await bridge.execute_integration_action(request.action, request.parameters)
    
    @app.post("/voice/start")
    async def start_voice(request: VoiceRequest):
        """Start voice presence"""
        return await bridge.start_voice_presence(request.emotion, request.intensity)
    
    @app.post("/voice/stop")
    async def stop_voice():
        """Stop voice presence"""
        if bridge.voice_presence:
            bridge.voice_presence.clear_voice_presence()
            return {"success": True}
        return {"success": False, "error": "Voice presence not available"}
    
    # Thread Management Routes
    
    class ThreadSwitchRequest(BaseModel):
        thread_id: str
    
    class ThreadCreateRequest(BaseModel):
        title: str
        folder_id: Optional[str] = None
        trigger_rebirth: bool = True
    
    @app.post("/webui/switch-thread")
    async def switch_thread(request: ThreadSwitchRequest):
        """Switch to a specific thread"""
        return await bridge.switch_thread(request.thread_id)
    
    @app.post("/webui/create-thread")
    async def create_thread(request: ThreadCreateRequest):
        """Create a new thread"""
        return await bridge.create_new_thread(
            request.title, 
            request.folder_id, 
            request.trigger_rebirth
        )
    
    @app.get("/webui/current-thread")
    async def get_current_thread():
        """Get current thread information"""
        if bridge.current_thread_id and bridge.thread_manager:
            thread = bridge.thread_manager.get_thread(bridge.current_thread_id)
            if thread:
                return {"thread": thread.dict(), "thread_id": bridge.current_thread_id}
        return {"thread": None, "thread_id": None}

except ImportError:
    logger.warning("FastAPI not available - API endpoints will not be created")

# Example usage and testing
async def demo_openwebui_bridge():
    """Demonstrate OpenWebUI bridge functionality"""
    bridge = OpenWebUIBridge()
    
    print("=== OpenWebUI Bridge Demo ===")
    
    # Initialize
    if await bridge.initialize():
        print("✓ Bridge initialized successfully")
        
        # Get enhanced context
        context = await bridge.get_enhanced_context()
        print(f"\nEnhanced Context:")
        print(f"  Current Emotion: {context['emotional_state']['current_emotion']}")
        print(f"  Calendar Events: {context['integrations']['calendar']['upcoming_events']}")
        print(f"  Music Playing: {context['integrations']['music']['is_playing']}")
        print(f"  Health Alerts: {len(context['integrations']['health']['alerts'])}")
        
        # Process message
        message_response = await bridge.process_user_message("I'm feeling a bit stressed today")
        print(f"\nMessage Processing:")
        print(f"  Suggested Tone: {message_response['suggested_tone']}")
        print(f"  Integration Hints: {message_response['integration_hints']}")
        
        # Start voice presence
        voice_result = await bridge.start_voice_presence("peace", 0.8)
        print(f"\nVoice Presence: {'✓' if voice_result['success'] else '✗'}")
        
        # System status
        status = await bridge.get_system_status()
        print(f"\nSystem Status: {len(status['components'])} components active")
    
    else:
        print("✗ Failed to initialize bridge")

if __name__ == "__main__":
    asyncio.run(demo_openwebui_bridge())
