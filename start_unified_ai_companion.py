#!/usr/bin/env python3
"""
AI Companion Unified Startup Script

This script initializes all integration services and starts the complete
AI companion system with emotional awareness, voice presence, and
unified integrations for calendar, email, SMS, music, social media, and health.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from datetime import datetime

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import our modules
try:
    from modules.integrations.unified_integration import UnifiedIntegrationService
    from modules.reflection.emotion_reflector import EmotionReflector
    from modules.presence.voice_integration import EmotionalVoicePresence
    from modules.monologue.inner_monologue import InnerMonologue
    from frontend.openwebui_bridge import OpenWebUIBridge
except ImportError as e:
    print(f"❌ Failed to import required modules: {e}")
    print("Please ensure all dependencies are installed:")
    print("pip install -r requirements_integrations.txt")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ai_companion.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class AICompanionSystem:
    """Main AI Companion System Controller"""
    
    def __init__(self):
        self.integration_service = None
        self.emotion_reflector = None
        self.voice_presence = None
        self.inner_monologue = None
        self.webui_bridge = None
        self.is_running = False
        
    async def initialize(self) -> bool:
        """Initialize all AI companion services"""
        try:
            logger.info("🚀 Starting AI Companion System initialization...")
            
            # Create logs directory
            os.makedirs('logs', exist_ok=True)
            os.makedirs('data', exist_ok=True)
            
            # Initialize core emotional system
            logger.info("📭 Initializing Emotion Reflector...")
            self.emotion_reflector = EmotionReflector()
            
            # Initialize voice presence
            logger.info("🎤 Initializing Voice Presence...")
            self.voice_presence = EmotionalVoicePresence()
            
            # Initialize inner monologue
            logger.info("🧠 Initializing Inner Monologue...")
            self.inner_monologue = InnerMonologue(idle_threshold_seconds=300)  # 5 minutes
            
            # Initialize unified integrations
            logger.info("🔗 Initializing Unified Integrations...")
            self.integration_service = UnifiedIntegrationService()
            
            # Configure enabled integrations
            self.integration_service.config["enabled_integrations"] = [
                "calendar", "email", "sms", "music", "social", "health"
            ]
            
            # Set up unified persona
            self.integration_service.config["unified_persona"] = {
                "name": "AI Companion",
                "personality_traits": [
                    "empathetic", "supportive", "intelligent", "adaptive", 
                    "emotionally aware", "caring", "intuitive"
                ],
                "communication_style": "warm, understanding, and emotionally responsive",
                "emotional_depth": True,
                "voice_modulation": True,
                "contextual_awareness": True
            }
            
            # Initialize all integration services
            logger.info("🌐 Connecting to external services...")
            init_results = await self.integration_service.initialize_all()
            
            # Log initialization results
            successful_integrations = []
            failed_integrations = []
            
            for service, results in init_results.items():
                if isinstance(results, dict):
                    for provider, success in results.items():
                        if success:
                            successful_integrations.append(f"{service}:{provider}")
                        else:
                            failed_integrations.append(f"{service}:{provider}")
                else:
                    if results:
                        successful_integrations.append(service)
                    else:
                        failed_integrations.append(service)
            
            logger.info(f"✅ Successfully initialized: {', '.join(successful_integrations)}")
            if failed_integrations:
                logger.warning(f"⚠️ Failed to initialize: {', '.join(failed_integrations)}")
            
            # Initialize OpenWebUI bridge
            logger.info("🌉 Initializing OpenWebUI Bridge...")
            self.webui_bridge = OpenWebUIBridge()
            await self.webui_bridge.initialize()
            
            # Set up thread management API routes
            logger.info("🔗 Setting up thread management API routes...")
            self._setup_thread_api_routes()
            
            # Start inner monologue
            logger.info("💭 Starting Inner Monologue...")
            self.inner_monologue.start()
            
            # Initial emotional reflection
            logger.info("💝 Setting initial emotional state...")
            self.emotion_reflector.log_emotional_event(
                event_type="system_startup",
                context={
                    "timestamp": datetime.now().isoformat(),
                    "successful_integrations": len(successful_integrations),
                    "total_integrations": len(successful_integrations) + len(failed_integrations)
                }
            )
            
            # Get initial emotional state
            emotional_summary = self.emotion_reflector.summarize_reflection()
            initial_emotion = emotional_summary.get("dominant_emotion", "contentment")
            
            # Start voice presence with initial emotion
            logger.info(f"🎵 Starting Voice Presence ({initial_emotion})...")
            await self.voice_presence.activate_voice_presence(
                emotion=initial_emotion,
                intensity=0.6,
                duration=3600.0,  # 1 hour
                include_whispers=True,
                include_ambient=True
            )
            
            self.is_running = True
            logger.info("✨ AI Companion System initialized successfully!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI Companion System: {e}")
            return False
    
    async def run_system_loop(self):
        """Main system loop"""
        logger.info("🔄 Starting main system loop...")
        
        try:
            while self.is_running:
                # Check for whispers
                if self.voice_presence:
                    whisper = await self.voice_presence.check_whisper_queue()
                    if whisper:
                        logger.debug(f"🤫 Processing whisper: {whisper['original_text']}")
                
                # Update emotional context from integrations
                if self.integration_service:
                    context = await self.integration_service.get_unified_context()
                    
                    # Reflect on any urgent items
                    urgent_emails = [e for e in context.recent_emails if e.importance == "high"]
                    urgent_messages = [m for m in context.recent_messages if m.emotional_urgency > 0.7]
                    
                    if urgent_emails or urgent_messages:
                        if self.emotion_reflector:
                            self.emotion_reflector.log_emotional_event(
                                event_type="urgent_communications",
                                context={
                                    "timestamp": datetime.now().isoformat(),
                                    "urgent_count": len(urgent_emails) + len(urgent_messages)
                                }
                            )
                
                # Check for health alerts
                if context.health_context:
                    health_alerts = context.health_context.get("health_context", {}).get("health_alerts", [])
                    if health_alerts:
                        if self.emotion_reflector:
                            self.emotion_reflector.log_emotional_event(
                                event_type="health_alert",
                                context={
                                    "timestamp": datetime.now().isoformat(), 
                                    "alerts": health_alerts,
                                    "content": f"Health alerts detected: {', '.join(health_alerts)}"
                                }
                            )
                
                # Inner monologue processing happens automatically
                
                # Sleep for a short interval
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except KeyboardInterrupt:
            logger.info("📴 Received shutdown signal...")
        except Exception as e:
            logger.error(f"❌ Error in system loop: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Gracefully shutdown all services"""
        logger.info("📴 Shutting down AI Companion System...")
        
        try:
            # Stop inner monologue
            if self.inner_monologue and self.inner_monologue._running:
                self.inner_monologue.stop()
                logger.info("💭 Inner monologue stopped")
            
            # Clear voice presence
            if self.voice_presence:
                self.voice_presence.clear_voice_presence()
                logger.info("🎵 Voice presence cleared")
            
            # Final emotional reflection
            if self.emotion_reflector:
                self.emotion_reflector.log_emotional_event(
                    event_type="system_shutdown",
                    context={
                        "timestamp": datetime.now().isoformat(),
                        "content": "AI Companion system shutting down gracefully"
                    }
                )
                logger.info("💝 Final emotional reflection completed")
            
            self.is_running = False
            logger.info("✨ AI Companion System shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")
    
    def _setup_thread_api_routes(self):
        """Set up thread management API routes"""
        try:
            from modules.threads.thread_manager import setup_thread_routes
            from fastapi import FastAPI
            
            # Create FastAPI app if not exists
            if not hasattr(self, 'api_app'):
                self.api_app = FastAPI(title="AI Companion API")
            
            # Set up thread routes
            setup_thread_routes(self.api_app)
            
            # Set up integration routes
            self._setup_integration_api_routes()
            
            logger.info("✅ Thread management API routes configured")
            
        except Exception as e:
            logger.error(f"❌ Error setting up thread API routes: {e}")
    
    def _setup_integration_api_routes(self):
        """Set up integration API routes"""
        try:
            from fastapi import FastAPI, HTTPException
            from fastapi.middleware.cors import CORSMiddleware
            
            # Create FastAPI app if not exists
            if not hasattr(self, 'api_app'):
                self.api_app = FastAPI(title="AI Companion API")
                
                # Add CORS middleware
                self.api_app.add_middleware(
                    CORSMiddleware,
                    allow_origins=["*"],  # Configure appropriately for production
                    allow_credentials=True,
                    allow_methods=["*"],
                    allow_headers=["*"],
                )
            
            # Integration status endpoint
            @self.api_app.get("/api/integrations/status")
            async def get_integration_status():
                if not self.integration_service:
                    return {"error": "Integration service not initialized"}
                
                return {
                    "calendar": {"active": True, "providers": ["google", "outlook", "apple"]},
                    "email": {"active": True, "providers": ["gmail", "outlook"]},
                    "sms": {"active": True, "provider": "twilio"},
                    "music": {"active": True, "provider": "apple_music"},
                    "social": {"active": True, "platforms": ["reddit", "twitter", "facebook"]},
                    "health": {"active": True, "provider": "apple_health"}
                }
            
            # Unified context endpoint
            @self.api_app.get("/api/integrations/context")
            async def get_unified_context():
                if not self.integration_service:
                    raise HTTPException(status_code=503, detail="Integration service not available")
                
                try:
                    context = await self.integration_service.get_unified_context()
                    return context
                except Exception as e:
                    logger.error(f"Error getting unified context: {e}")
                    raise HTTPException(status_code=500, detail=str(e))
            
            # Integration action endpoint
            @self.api_app.post("/api/integrations/action")
            async def execute_integration_action(request: dict):
                if not self.integration_service:
                    raise HTTPException(status_code=503, detail="Integration service not available")
                
                integration = request.get("integration")
                action = request.get("action")
                params = request.get("params", {})
                
                try:
                    # Route to appropriate integration service
                    if integration == "calendar":
                        return await self._handle_calendar_action(action, params)
                    elif integration == "email":
                        return await self._handle_email_action(action, params)
                    elif integration == "sms":
                        return await self._handle_sms_action(action, params)
                    elif integration == "music":
                        return await self._handle_music_action(action, params)
                    elif integration == "social":
                        return await self._handle_social_action(action, params)
                    elif integration == "health":
                        return await self._handle_health_action(action, params)
                    else:
                        raise HTTPException(status_code=400, detail=f"Unknown integration: {integration}")
                        
                except Exception as e:
                    logger.error(f"Error executing integration action: {e}")
                    raise HTTPException(status_code=500, detail=str(e))
            
            # Calendar endpoints
            @self.api_app.get("/api/integrations/calendar/events")
            async def get_calendar_events(days: int = 7):
                if not self.integration_service:
                    raise HTTPException(status_code=503, detail="Integration service not available")
                return await self.integration_service.calendar.get_upcoming_events(days)
            
            # Email endpoints
            @self.api_app.get("/api/integrations/email/unread")
            async def get_unread_emails(limit: int = 10):
                if not self.integration_service:
                    raise HTTPException(status_code=503, detail="Integration service not available")
                return await self.integration_service.email.get_recent_emails(limit)
            
            # Health endpoints
            @self.api_app.get("/api/integrations/health/biometrics")
            async def get_current_biometrics():
                if not self.integration_service:
                    raise HTTPException(status_code=503, detail="Integration service not available")
                return await self.integration_service.health.get_real_time_biometrics()
            
            logger.info("✅ Integration API routes configured")
            
        except Exception as e:
            logger.error(f"❌ Error setting up integration API routes: {e}")
    
    async def _handle_calendar_action(self, action: str, params: dict):
        """Handle calendar integration actions"""
        calendar = self.integration_service.calendar
        
        if action == "get_events":
            return await calendar.get_upcoming_events(params.get("days", 7))
        elif action == "create_event":
            return await calendar.create_event(params)
        elif action == "update_event":
            return await calendar.update_event(params["event_id"], params["updates"])
        elif action == "delete_event":
            return await calendar.delete_event(params["event_id"])
        else:
            raise ValueError(f"Unknown calendar action: {action}")
    
    async def _handle_email_action(self, action: str, params: dict):
        """Handle email integration actions"""
        email = self.integration_service.email
        
        if action == "get_unread":
            return await email.get_recent_emails(params.get("limit", 10))
        elif action == "send":
            # Method not implemented yet - return placeholder
            return {"status": "not_implemented", "message": "Email sending not yet implemented"}
        elif action == "mark_read":
            # Method not implemented yet - return placeholder  
            return {"status": "not_implemented", "message": "Mark as read not yet implemented"}
        else:
            raise ValueError(f"Unknown email action: {action}")
    
    async def _handle_sms_action(self, action: str, params: dict):
        """Handle SMS integration actions"""
        sms = self.integration_service.sms
        
        if action == "get_messages":
            return await sms.get_recent_messages(params.get("limit", 10))
        elif action == "send":
            # Method not implemented yet - return placeholder
            return {"status": "not_implemented", "message": "SMS sending not yet implemented"}
        else:
            raise ValueError(f"Unknown SMS action: {action}")
    
    async def _handle_music_action(self, action: str, params: dict):
        """Handle music integration actions"""
        music = self.integration_service.music
        
        if action == "current_track":
            context = await music.get_music_context()
            return {"current_track": context.current_track if context else None}
        elif action == "control":
            return await music.control_playback(params["command"])
        elif action == "recommendations":
            # Use mood-based music playing for recommendations
            await music._play_mood_based_music(params["emotion"])
            return {"status": "playing_mood_music", "emotion": params["emotion"]}
        else:
            raise ValueError(f"Unknown music action: {action}")
    
    async def _handle_social_action(self, action: str, params: dict):
        """Handle social media integration actions"""
        social = self.integration_service.social
        
        if action == "get_feed":
            context = await social.get_social_context()
            return {"posts": context.recent_posts if context else []}
        elif action == "post":
            # Method not implemented yet - return placeholder
            return {"status": "not_implemented", "message": "Social posting not yet implemented"}
        elif action == "notifications":
            # Method not implemented yet - return placeholder
            return {"status": "not_implemented", "message": "Social notifications not yet implemented"}
        else:
            raise ValueError(f"Unknown social action: {action}")
    
    async def _handle_health_action(self, action: str, params: dict):
        """Handle health integration actions"""
        health = self.integration_service.health
        
        if action == "biometrics":
            return await health.get_real_time_biometrics()
        elif action == "summary":
            return await health.get_emotional_health_context()
        elif action == "log_data":
            # Method not implemented yet - return placeholder
            return {"status": "not_implemented", "message": "Manual health logging not yet implemented"}
        else:
            raise ValueError(f"Unknown health action: {action}")
    
    async def get_status(self) -> dict:
        """Get comprehensive system status"""
        try:
            status = {
                "system_running": self.is_running,
                "timestamp": datetime.now().isoformat(),
                "components": {}
            }
            
            if self.emotion_reflector:
                emotional_summary = self.emotion_reflector.summarize_reflection()
                status["components"]["emotions"] = {
                    "active": True,
                    "current_emotion": emotional_summary.get("dominant_emotion"),
                    "intensity": emotional_summary.get("intensity"),
                    "summary": emotional_summary.get("summary")
                }
            
            if self.voice_presence:
                status["components"]["voice"] = self.voice_presence.get_voice_status()
            
            if self.inner_monologue:
                status["components"]["monologue"] = {
                    "active": self.inner_monologue._running,
                    "idle_threshold": self.inner_monologue.idle_threshold_seconds
                }
            
            if self.integration_service:
                status["components"]["integrations"] = await self.integration_service.get_service_status()
            
            if self.webui_bridge:
                bridge_status = await self.webui_bridge.get_system_status()
                status["components"]["webui_bridge"] = bridge_status
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"error": str(e)}

async def start_api_server():
    """Start the FastAPI server for OpenWebUI integration"""
    try:
        import uvicorn
        from frontend.openwebui_bridge import app
        
        logger.info("🌐 Starting FastAPI server for OpenWebUI integration...")
        
        # Run the server
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        await server.serve()
        
    except ImportError:
        logger.warning("⚠️ FastAPI/Uvicorn not available - API server not started")
    except Exception as e:
        logger.error(f"❌ Failed to start API server: {e}")

async def main():
    """Main entry point"""
    print("🤖 AI Companion System with Unified Integrations")
    print("=" * 50)
    
    # Initialize system
    companion_system = AICompanionSystem()
    
    if not await companion_system.initialize():
        logger.error("❌ Failed to initialize system")
        return 1
    
    # Display startup status
    status = await companion_system.get_status()
    print(f"\n✨ System Status:")
    print(f"   Current Emotion: {status['components']['emotions']['current_emotion']}")
    print(f"   Voice Active: {status['components']['voice']['active']}")
    print(f"   Integrations: {len(status['components']['integrations']['initialized_services'])}")
    print(f"   Inner Monologue: {status['components']['monologue']['active']}")
    
    print(f"\n🌐 Available Services:")
    print(f"   • Calendar Integration")
    print(f"   • Email Monitoring") 
    print(f"   • SMS Integration")
    print(f"   • Apple Music Control")
    print(f"   • Social Media Monitoring")
    print(f"   • Health Data Integration")
    print(f"   • Emotional Voice Presence")
    print(f"   • Inner Monologue System")
    
    print(f"\n🎯 Unified Persona: {status['components']['integrations']['unified_persona']['name']}")
    print(f"   Communication Style: {status['components']['integrations']['unified_persona']['communication_style']}")
    
    print(f"\n🚀 System ready! Press Ctrl+C to shutdown gracefully")
    print(f"📡 API server will be available at http://localhost:8000")
    print("=" * 50)
    
    # Start API server and main loop concurrently
    try:
        await asyncio.gather(
            start_api_server(),
            companion_system.run_system_loop()
        )
    except KeyboardInterrupt:
        logger.info("📴 Shutdown requested by user")
    finally:
        await companion_system.shutdown()
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n📴 Shutdown requested")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
