#!/usr/bin/env python3
"""
Dolphin Backend - AI Orchestration Server v2.0

Enhanced multi-server architecture with:
- Personality System: User-selectable AI personas
- Memory System: Session & long-term memory with sentiment analysis
- Analytics Logging: Comprehensive routing transparency & performance tracking
- Agent Awareness: Real-time status monitoring

Architecture:
- Dolphin handles general conversation and routing decisions
- Heavy coding tasks → OpenRouter (GPT-4/Claude)
- Utilities (email/calendar) → n8n agents
- Analytics fallback → Kimi K2 (when OpenRouter unavailable)

Usage:
    python dolphin_backend.py
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from persona_filter import apply_persona_filter

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Using system environment variables only.")
import aiohttp
import uvicorn
import os
from pathlib import Path

# Import our enhanced systems
from personality_system import PersonalitySystem
from memory_system import MemorySystem
from analytics_logger import AnalyticsLogger
from handler_registry import handler_registry, HandlerState
from fallback_personas import get as get_fallback_persona
from judge_agent import JudgeAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dolphin_backend.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Import advanced v2.1 features after logger is configured
try:
    from reflection_engine import ReflectionEngine
    from connectivity_manager import ConnectivityManager
    from private_memory import PrivateMemoryManager
    from persona_instruction_manager import PersonaInstructionManager
    from mirror_mode import MirrorModeManager
    from system_metrics import MetricsCollector
    ADVANCED_FEATURES_AVAILABLE = True
    logger.info("✅ Advanced v2.1 features imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Some advanced features unavailable: {e}")
    ADVANCED_FEATURES_AVAILABLE = False

# Enhanced Pydantic models
class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    persona: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    handler: str
    reasoning: str
    metadata: Dict[str, Any]
    timestamp: str
    session_id: str
    persona_used: str
    judgment: Optional[Dict[str, Any]] = None

class TaskRoute(BaseModel):
    task_type: str
    confidence: float
    reasoning: str
    handler: str

# FastAPI app
app = FastAPI(title="Dolphin AI Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DolphinOrchestrator:
    """
    Enhanced Dolphin orchestrator with personality, memory, and analytics
    """
    
    def __init__(self):
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.openrouter_key = os.getenv('OPENROUTER_KEY')
        self.n8n_url = os.getenv('N8N_URL', 'http://localhost:5678')
        
        # Model configuration
        self.primary_model = os.getenv('PRIMARY_MODEL', 'llama2-uncensored')
        self.fallback_model = os.getenv('FALLBACK_MODEL', 'mistral:7b-instruct-q4_K_M')
        
        # Initialize enhanced systems
        self.personality_system = PersonalitySystem()
        self.memory_system = MemorySystem()
        self.analytics_logger = AnalyticsLogger()
        
        # Initialize advanced features v2.1
        self.reflection_engine = None
        self.connectivity_manager = None
        self.private_memory_manager = None
        self.persona_instruction_manager = None
        self.mirror_mode_manager = None
        self.metrics_collector = None
        
        # Advanced features initialization will be called in startup
        logger.info("🐬 Enhanced Dolphin Orchestrator v2.1 initialized - advanced features pending startup")
    
    async def initialize_advanced_features(self):
        """Initialize all advanced v2.1 features"""
        if not ADVANCED_FEATURES_AVAILABLE:
            logger.warning("⚠️ Advanced features not available - skipping initialization")
            return
            
        try:
            # Initialize Reflection Engine
            self.reflection_engine = ReflectionEngine(self.memory_system, self.analytics_logger)
            
            # Initialize Mirror Mode Manager
            self.mirror_mode_manager = MirrorModeManager(self.analytics_logger)

            # Initialize Connectivity Manager
            self.connectivity_manager = ConnectivityManager(
                self.analytics_logger,
                on_status_change=self._on_handler_status_change,
                mirror_mode_manager=self.mirror_mode_manager,
            )

            # Initialize Private Memory Manager
            self.private_memory_manager = PrivateMemoryManager()

            # Initialize Persona Instruction Manager
            self.persona_instruction_manager = PersonaInstructionManager()
            
            # Initialize System Metrics Collector
            self.metrics_collector = MetricsCollector(self.analytics_logger)
            
            # Start background services
            asyncio.create_task(self.reflection_engine.start_background_reflection())
            asyncio.create_task(self.connectivity_manager.start_monitoring())

            logger.info("✅ All advanced v2.1 features initialized successfully")

        except Exception as e:
            logger.error(f"❌ Error initializing advanced features: {e}")
            # Continue without advanced features if initialization fails

    def _on_handler_status_change(self, status: Dict[str, Any]) -> None:
        """Callback for connectivity status changes."""
        logger.info(f"Handler status updated: {status.get('current_mode')}")

    async def _record_judgment(self, session_id: str, judgment: Dict[str, Any],
                               persona: str, persona_token: Optional[str], request_id: str) -> None:
        """Store judgment in memory and analytics without blocking main flow."""
        try:
            self.memory_system.add_judgment(
                session_id,
                judgment,
                persona=persona,
                persona_token=persona_token,
            )
            self.analytics_logger.log_custom_event(
                "judgment",
                {"session_id": session_id, "judgment": judgment, "persona": persona, "request_id": request_id},
            )
        except Exception as e:
            logger.error(f"Error recording judgment: {e}")
        
    async def get_available_model(self, preferred_model: Optional[str] = None) -> str:
        """
        Get the best available model from Ollama, with fallback support
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ollama_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        available_models = [model["name"] for model in data.get("models", [])]
                        
                        # If specific model requested and available, use it
                        if preferred_model and preferred_model in available_models:
                            return preferred_model
                        
                        # Try primary model first
                        if self.primary_model in available_models:
                            return self.primary_model
                        
                        # Fall back to secondary model
                        if self.fallback_model in available_models:
                            logger.warning(f"Primary model '{self.primary_model}' not available, using fallback '{self.fallback_model}'")
                            return self.fallback_model
                        
                        # If neither is available, use the first available model
                        if available_models:
                            fallback_choice = available_models[0]
                            logger.warning(f"Neither primary nor fallback models available, using '{fallback_choice}'")
                            return fallback_choice
                        
                        # No models available
                        raise Exception("No models available in Ollama")
                    else:
                        raise Exception(f"Failed to connect to Ollama: {response.status}")
        except Exception as e:
            logger.error(f"Error checking available models: {e}")
            # Return primary model as last resort (will fail if not available)
            return self.primary_model
    
    async def process_chat_request(self, request: ChatRequest, persona_token: Optional[str] = None) -> ChatResponse:
        """
        Enhanced chat processing with personality, memory, and analytics
        """
        start_time = time.time()
        request_id = None
        
        try:
            # Set persona if provided
            if request.persona:
                self.personality_system.set_persona(request.persona)
            
            current_persona = self.personality_system.get_current_persona()
            
            # Create or get session
            session_id = request.session_id or self.memory_system.create_session()
            
            # Get session context
            session_context = self.memory_system.get_session_context(
                session_id, persona=current_persona["name"], persona_token=persona_token
            )
            
            # Enhance context with memory
            enhanced_context = {
                **(request.context or {}),
                "session_context": session_context,
                "persona": current_persona["name"],
                "memory_focus": self.personality_system.get_memory_focus_areas()
            }
            
            # Classify task with persona awareness
            route = await self.classify_task(request.message, enhanced_context)
            route = self.personality_system.adjust_routing_for_persona(route.__dict__)
            
            # Log routing decision
            request_id = self.analytics_logger.log_routing_decision(
                request.dict(), route, current_persona["name"]
            )
            
            # Format prompt with persona
            formatted_message = self.personality_system.format_prompt_with_persona(
                request.message, enhanced_context
            )
            
            # Route to appropriate handler
            if route["handler"] == "OPENROUTER":
                response_text = await self.handle_openrouter_request(formatted_message, enhanced_context)
            elif route["handler"] == "N8N":
                response_text = await self.handle_n8n_request(formatted_message, enhanced_context)
            elif route["handler"] == "KIMI_K2":
                response_text = await self.handle_kimi_fallback(formatted_message, enhanced_context)
            else:  # DOLPHIN
                response_text = await self.handle_dolphin_request(formatted_message, enhanced_context)

            # Apply unified persona filter
            response_text = apply_persona_filter(response_text, current_persona["name"])
            
            # Add messages to memory
            self.memory_system.add_message(
                session_id, request.message, "user",
                metadata={"persona": current_persona["name"], "request_id": request_id},
                persona=current_persona["name"], persona_token=persona_token
            )
            
            self.memory_system.add_message(
                session_id, response_text, "assistant",
                handler=route["handler"],
                metadata={"reasoning": route["reasoning"], "request_id": request_id},
                persona=current_persona["name"], persona_token=persona_token
            )

            # Evaluate response with JudgeAgent
            judge = JudgeAgent()
            judgment = judge.evaluate(
                response_text,
                {
                    "session_context": session_context,
                    "persona": current_persona["name"],
                    "session_id": session_id,
                },
            )

            # Store judgment asynchronously
            asyncio.create_task(
                self._record_judgment(session_id, judgment, current_persona["name"], persona_token, request_id)
            )
            
            # Calculate performance metrics
            latency = time.time() - start_time
            
            # Log performance
            self.analytics_logger.log_performance_metrics(
                request_id, route["handler"], latency, True
            )
            
            response = ChatResponse(
                response=response_text,
                handler=route["handler"],
                reasoning=route["reasoning"],
                metadata={
                    "persona_applied": route.get("persona_applied", current_persona["name"]),
                    "confidence": route["confidence"],
                    "latency_seconds": round(latency, 3),
                    "session_message_count": session_context["total_messages"] + 1,
                    "sentiment_trend": session_context["sentiment_trend"]
                },
                timestamp=datetime.now().isoformat(),
                session_id=session_id,
                persona_used=current_persona["name"],
                judgment=judgment
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Chat processing error: {e}")
            
            # Log error performance
            if request_id:
                latency = time.time() - start_time
                self.analytics_logger.log_performance_metrics(
                    request_id, "ERROR", latency, False, error_message=str(e)
                )
            
            return ChatResponse(
                response=f"I encountered an error processing your request: {str(e)}",
                handler="ERROR",
                reasoning="Exception occurred during processing",
                metadata={"error": str(e), "timestamp": datetime.now().isoformat()},
                timestamp=datetime.now().isoformat(),
                session_id=request.session_id or "unknown",
                persona_used=self.personality_system.get_current_persona()["name"],
                judgment=None
            )
        
    async def classify_task(self, message: str, context: Optional[Dict] = None) -> TaskRoute:
        """
        Use Dolphin to classify the task type and determine routing
        """
        classification_prompt = f"""
Analyze this user message and determine the best handler:

Message: "{message}"
Context: {json.dumps(context or {}, indent=2)}

Choose from these handlers:
1. DOLPHIN - General conversation, questions, explanations
2. OPENROUTER - Complex coding, programming tasks, technical documentation
3. N8N - Utilities like email, calendar, file operations, web scraping
4. KIMI_K2 - Data analysis, analytics, when OpenRouter is unavailable

Respond in JSON format:
{{
    "task_type": "conversation|coding|utility|analytics",
    "handler": "DOLPHIN|OPENROUTER|N8N|KIMI_K2",
    "confidence": 0.0-1.0,
    "reasoning": "Brief explanation of choice"
}}
"""

        try:
            # Get the best available model for classification
            model_to_use = await self.get_available_model()
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": model_to_use,
                    "prompt": classification_prompt,
                    "stream": False
                }
                
                async with session.post(f"{self.ollama_url}/api/generate", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Parse Dolphin's response
                        try:
                            classification = json.loads(result['response'])
                            return TaskRoute(**classification)
                        except json.JSONDecodeError:
                            # Fallback if JSON parsing fails
                            return TaskRoute(
                                task_type="conversation",
                                handler="DOLPHIN",
                                confidence=0.8,
                                reasoning="JSON parsing failed, defaulting to conversation"
                            )
                    else:
                        raise Exception(f"Ollama API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Task classification error: {e}")
            # Fallback classification
            if any(keyword in message.lower() for keyword in ['code', 'program', 'function', 'algorithm']):
                return TaskRoute(task_type="coding", handler="OPENROUTER", confidence=0.7, reasoning="Keyword-based fallback")
            elif any(keyword in message.lower() for keyword in ['email', 'calendar', 'schedule', 'send']):
                return TaskRoute(task_type="utility", handler="N8N", confidence=0.7, reasoning="Keyword-based fallback")
            else:
                return TaskRoute(task_type="conversation", handler="DOLPHIN", confidence=0.6, reasoning="Default fallback")

    async def handle_dolphin_request(self, message: str, context: Optional[Dict] = None) -> str:
        """Handle requests with local LLM directly"""
        try:
            # Get the best available model
            model_to_use = await self.get_available_model()
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": model_to_use,
                    "prompt": message,
                    "stream": False
                }
                
                async with session.post(f"{self.ollama_url}/api/generate", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['response']
                    else:
                        raise Exception(f"Dolphin API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Dolphin request error: {e}")
            return f"I'm having trouble accessing my local processing. Error: {str(e)}"

    async def handle_openrouter_request(self, message: str, context: Optional[Dict] = None) -> str:
        """Route complex coding tasks to OpenRouter"""
        if not self.openrouter_key:
            return await self.handle_kimi_fallback(message, context)
            
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": "gpt-4",
                    "messages": [{"role": "user", "content": message}],
                    "stream": False
                }
                
                headers = {
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "Dolphin Backend"
                }
                
                async with session.post("https://openrouter.ai/api/v1/chat/completions", 
                                      json=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['message']['content']
                    else:
                        raise Exception(f"OpenRouter API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"OpenRouter request error: {e}")
            return await self.handle_kimi_fallback(message, context)

    async def handle_n8n_request(self, message: str, context: Optional[Dict] = None) -> str:
        """Route utility tasks to n8n agents"""
        try:
            # For now, simulate n8n integration
            # In production, this would call actual n8n workflows
            utility_response = f"I would handle this utility task via n8n: {message}"
            
            # TODO: Implement actual n8n webhook calls
            # async with aiohttp.ClientSession() as session:
            #     payload = {"message": message, "context": context}
            #     async with session.post(f"{self.n8n_url}/webhook/utility", json=payload) as response:
            #         result = await response.json()
            #         return result['response']
            
            return utility_response
            
        except Exception as e:
            logger.error(f"n8n request error: {e}")
            return f"Utility service temporarily unavailable. Error: {str(e)}"

    async def handle_kimi_fallback(self, message: str, context: Optional[Dict] = None) -> str:
        """Use Kimi K2 as analytics fallback when OpenRouter is unavailable"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": "kimik2",
                    "prompt": f"Analytics mode - {message}",
                    "stream": False
                }
                
                async with session.post(f"{self.ollama_url}/api/generate", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return f"[Analytics Mode] {result['response']}"
                    else:
                        raise Exception(f"Kimi API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Kimi fallback error: {e}")
            return "All AI services are currently unavailable. Please try again later."

# Initialize enhanced orchestrator
orchestrator = DolphinOrchestrator()

# Enhanced API endpoints
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: Request, chat: ChatRequest):
    """Enhanced chat endpoint with personality, memory, and analytics"""
    token = req.headers.get("persona-token")
    return await orchestrator.process_chat_request(chat, persona_token=token)

@app.get("/api/status")
async def status_endpoint():
    """Enhanced status endpoint with system health metrics"""
    try:
        # Test Ollama connection
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{orchestrator.ollama_url}/api/tags") as response:
                ollama_status = response.status == 200
    except:
        ollama_status = False
    
    # Get system analytics
    analytics = orchestrator.analytics_logger.get_real_time_stats()
    memory_summary = orchestrator.memory_system.get_memory_summary()
    
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "backend_status": {
            "services": {
                "ollama": ollama_status,
                "openrouter_configured": bool(orchestrator.openrouter_key),
                "n8n": False  # TODO: Add actual n8n health check
            },
            "analytics": analytics,
            "memory": memory_summary,
            "personality": {
                "current_persona": orchestrator.personality_system.current_persona,
                "available_personas": list(orchestrator.personality_system.personas.keys())
            }
        }
    }

@app.get("/api/handlers")
async def handlers_endpoint():
    """Get available AI handlers and their capabilities"""
    return {
        "handlers": [
            {
                "name": "DOLPHIN",
                "description": "Local conversation and general tasks",
                "icon": "🐬",
                "status": "available"
            },
            {
                "name": "OPENROUTER", 
                "description": "Cloud AI for complex coding tasks",
                "icon": "☁️",
                "status": "available" if orchestrator.openrouter_key else "unavailable"
            },
            {
                "name": "N8N",
                "description": "Workflow automation and utilities", 
                "icon": "🔧",
                "status": "development"
            },
            {
                "name": "KIMI_K2",
                "description": "Analytics and fallback processing",
                "icon": "📊", 
                "status": "available"
            }
        ]
    }

# Personality System Endpoints
@app.get("/api/personas")
async def get_personas():
    """Get all available personas"""
    return {
        "current_persona": orchestrator.personality_system.current_persona,
        "personas": orchestrator.personality_system.get_personas()
    }

@app.post("/api/personas/{persona_id}")
async def set_persona(persona_id: str):
    """Set active persona"""
    success = orchestrator.personality_system.set_persona(persona_id)
    if success:
        return {"success": True, "persona": persona_id}
    else:
        raise HTTPException(status_code=404, detail="Persona not found")

@app.post("/api/personas/create")
async def create_persona(persona_data: Dict[str, Any]):
    """Create a custom persona"""
    persona_id = persona_data.get("id")
    if not persona_id:
        raise HTTPException(status_code=400, detail="Persona ID required")
    
    success = orchestrator.personality_system.create_custom_persona(persona_id, persona_data)
    if success:
        return {"success": True, "persona_id": persona_id}
    else:
        raise HTTPException(status_code=400, detail="Failed to create persona")

# Memory System Endpoints  
@app.get("/api/memory/session/{session_id}")
async def get_session_memory(session_id: str):
    """Get session memory and context"""
    context = orchestrator.memory_system.get_session_context(session_id)
    return {"session_id": session_id, "context": context}

@app.get("/api/memory/longterm")
async def get_longterm_memory():
    """Get long-term memory summary"""
    return orchestrator.memory_system.long_term_memory

@app.post("/api/memory/longterm/goal")
async def add_goal(goal_data: Dict[str, Any]):
    """Add a new goal to long-term memory"""
    goal_text = goal_data.get("text")
    priority = goal_data.get("priority", "medium")
    
    if not goal_text:
        raise HTTPException(status_code=400, detail="Goal text required")
    
    goal_id = orchestrator.memory_system.add_goal(goal_text, priority)
    return {"success": True, "goal_id": goal_id}

@app.post("/api/memory/flush")
async def flush_memory():
    """Flush short-term memory"""
    success = orchestrator.memory_system.flush_short_term()
    return {"success": success}

@app.delete("/api/memory/session/{session_id}")
async def close_session(session_id: str):
    """Close and archive a session"""
    orchestrator.memory_system.close_session(session_id)
    return {"success": True, "session_id": session_id}

# Analytics and Logging Endpoints
@app.get("/api/analytics/realtime")
async def get_realtime_analytics():
    """Get real-time system analytics"""
    return orchestrator.analytics_logger.get_real_time_stats()

@app.get("/api/analytics/daily")
async def get_daily_analytics(days: int = 7):
    """Get daily analytics for past N days"""
    return orchestrator.analytics_logger.get_daily_analytics(days)

@app.get("/api/analytics/performance")
async def get_performance_report():
    """Get handler performance report"""
    return orchestrator.analytics_logger.get_handler_performance_report()

@app.get("/api/logs/search")
async def search_logs(query: str, log_type: str = "routing", hours: int = 24, limit: int = 50):
    """Search through system logs"""
    results = orchestrator.analytics_logger.search_logs(query, log_type, hours, limit)
    return {"query": query, "results": results, "count": len(results)}

@app.get("/api/logs/export")
async def export_analytics():
    """Export comprehensive analytics"""
    export_path = orchestrator.analytics_logger.export_analytics()
    return {"export_path": export_path}

# System Management Endpoints
@app.post("/api/system/cleanup")
async def cleanup_system(days_to_keep: int = 30):
    """Clean up old logs and data"""
    cleaned = orchestrator.analytics_logger.cleanup_old_logs(days_to_keep)
    return {"cleaned_entries": cleaned}

@app.get("/api/system/health")
async def system_health():
    """Comprehensive system health check"""
    analytics = orchestrator.analytics_logger.get_real_time_stats()
    memory = orchestrator.memory_system.get_memory_summary()
    persona = orchestrator.personality_system.get_current_persona()
    
    # Calculate health score
    health_factors = []
    
    # Handler availability
    if analytics.get("handler_details"):
        avg_success_rate = sum(h.get("success_rate", 0) for h in analytics["handler_details"].values()) / len(analytics["handler_details"])
        health_factors.append(avg_success_rate)
    
    # Memory usage (simple heuristic)
    active_sessions = memory["short_term"]["active_sessions"]
    memory_health = max(0, 1.0 - (active_sessions / 50))  # Assume 50+ sessions is heavy
    health_factors.append(memory_health)
    
    # System responsiveness (based on latency)
    avg_latency = analytics.get("performance", {}).get("avg_latency_seconds", 0)
    latency_health = max(0, 1.0 - (avg_latency / 10))  # Assume 10s+ is poor
    health_factors.append(latency_health)
    
    overall_health = sum(health_factors) / len(health_factors) if health_factors else 0.5
    
    if overall_health >= 0.8:
        health_status = "excellent"
    elif overall_health >= 0.6:
        health_status = "good"
    elif overall_health >= 0.4:
        health_status = "fair"
    else:
        health_status = "poor"
    
    return {
        "health_score": round(overall_health, 3),
        "health_status": health_status,
        "timestamp": datetime.now().isoformat(),
        "components": {
            "analytics": analytics,
            "memory": memory,
            "personality": {
                "current": persona["name"],
                "icon": persona["icon"]
            }
        }
    }

# Startup event to initialize advanced features
@app.on_event("startup")
async def startup_event():
    """Initialize advanced features on startup"""
    await orchestrator.initialize_advanced_features()

# =============================================================================
# ADVANCED FEATURES API ENDPOINTS v2.1
# =============================================================================

# Reflection Engine Endpoints
@app.get("/api/reflection/summary")
async def get_reflection_summary():
    """Get reflection engine summary and statistics"""
    if not orchestrator.reflection_engine:
        raise HTTPException(status_code=503, detail="Reflection engine not available")
    return orchestrator.reflection_engine.get_reflection_summary()

@app.post("/api/reflection/enable")
async def enable_reflection_engine():
    """Enable background reflection engine"""
    if not orchestrator.reflection_engine:
        raise HTTPException(status_code=503, detail="Reflection engine not available")
    
    if not orchestrator.reflection_engine.is_running:
        asyncio.create_task(orchestrator.reflection_engine.start_background_reflection())
    
    return {"status": "enabled", "is_running": orchestrator.reflection_engine.is_running}

@app.post("/api/reflection/disable")
async def disable_reflection_engine():
    """Disable background reflection engine"""
    if not orchestrator.reflection_engine:
        raise HTTPException(status_code=503, detail="Reflection engine not available")
    
    orchestrator.reflection_engine.stop_background_reflection()
    return {"status": "disabled"}

# Connectivity Management Endpoints
@app.get("/api/connectivity/status")
async def get_connectivity_status():
    """Get current connectivity status and service health"""
    if not orchestrator.connectivity_manager:
        raise HTTPException(status_code=503, detail="Connectivity manager not available")
    return orchestrator.connectivity_manager.get_status_summary()

@app.get("/api/connectivity/routing-adjustments")
async def get_routing_adjustments():
    """Get routing adjustments based on connectivity"""
    if not orchestrator.connectivity_manager:
        raise HTTPException(status_code=503, detail="Connectivity manager not available")
    return orchestrator.connectivity_manager.get_routing_adjustments()

@app.post("/api/connectivity/force-offline")
async def force_offline_mode(enabled: bool = True):
    """Force offline mode on/off"""
    if not orchestrator.connectivity_manager:
        raise HTTPException(status_code=503, detail="Connectivity manager not available")
    
    orchestrator.connectivity_manager.force_offline_mode(enabled)
    return {"forced_offline": enabled, "current_mode": orchestrator.connectivity_manager.current_mode.value}

@app.post("/api/connectivity/check-services")
async def manual_service_check(service_id: Optional[str] = None):
    """Manually trigger service connectivity check"""
    if not orchestrator.connectivity_manager:
        raise HTTPException(status_code=503, detail="Connectivity manager not available")
    
    result = await orchestrator.connectivity_manager.manual_service_check(service_id)
    return result

@app.get("/api/connectivity/notification")
async def get_connectivity_notification():
    """Get UI notification about connectivity status"""
    if not orchestrator.connectivity_manager:
        return None
    return orchestrator.connectivity_manager.get_ui_notification()

# Additional endpoints for handler status updates and fallback alerts
@app.post("/api/update-handler-status")
async def update_handler_status(handler: str, status: str):
    """Update handler status from frontend/admin."""
    try:
        handler_registry.update(handler, HandlerState(status))
        return {"handler": handler, "status": status}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/fallback-alert")
async def fallback_alert():
    """Notify UI that system entered emergency persona mode."""
    # In real implementation this would push websocket event
    return {"status": "alerted"}

# Private Memory Endpoints
@app.post("/api/private-memory/unlock")
async def unlock_private_memory(password: str = "default_dev_password"):
    """Unlock private memory with password"""
    if not orchestrator.private_memory_manager:
        raise HTTPException(status_code=503, detail="Private memory manager not available")
    
    success = orchestrator.private_memory_manager.unlock_private_memories(password)
    if success:
        return {"status": "unlocked", "message": "Private memories are now accessible"}
    else:
        raise HTTPException(status_code=401, detail="Invalid password")

@app.post("/api/private-memory/lock")
async def lock_private_memory():
    """Lock private memory"""
    if not orchestrator.private_memory_manager:
        raise HTTPException(status_code=503, detail="Private memory manager not available")
    
    orchestrator.private_memory_manager.lock_private_memories()
    return {"status": "locked", "message": "Private memories are now locked"}

@app.get("/api/private-memory/status")
async def get_private_memory_status():
    """Get private memory system status"""
    if not orchestrator.private_memory_manager:
        raise HTTPException(status_code=503, detail="Private memory manager not available")
    return orchestrator.private_memory_manager.get_status()

@app.get("/api/private-memory/preview")
async def get_private_memory_preview():
    """Get non-sensitive preview of private memories"""
    if not orchestrator.private_memory_manager:
        raise HTTPException(status_code=503, detail="Private memory manager not available")
    return orchestrator.private_memory_manager.get_private_memory_preview()

@app.post("/api/private-memory/add")
async def add_private_memory(request: dict):
    """Add a new private memory entry"""
    if not orchestrator.private_memory_manager:
        raise HTTPException(status_code=503, detail="Private memory manager not available")
    
    if not orchestrator.private_memory_manager.is_unlocked:
        raise HTTPException(status_code=403, detail="Private memories are locked")
    
    entry_id = orchestrator.private_memory_manager.add_private_memory(
        content=request.get("content", ""),
        tags=request.get("tags", []),
        category=request.get("category", "private"),
        session_id=request.get("session_id", "default"),
        access_level=request.get("access_level", "private"),
        metadata=request.get("metadata", {})
    )
    
    return {"entry_id": entry_id, "status": "added"}

@app.get("/api/private-memory/{entry_id}")
async def get_private_memory(entry_id: str):
    """Get a specific private memory entry"""
    if not orchestrator.private_memory_manager:
        raise HTTPException(status_code=503, detail="Private memory manager not available")
    
    if not orchestrator.private_memory_manager.is_unlocked:
        raise HTTPException(status_code=403, detail="Private memories are locked")
    
    memory = orchestrator.private_memory_manager.get_private_memory(entry_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Private memory not found")
    
    return memory

@app.get("/api/private-memory/search")
async def search_private_memories(query: Optional[str] = None, category: Optional[str] = None, limit: int = 10):
    """Search private memories"""
    if not orchestrator.private_memory_manager:
        raise HTTPException(status_code=503, detail="Private memory manager not available")
    
    if not orchestrator.private_memory_manager.is_unlocked:
        raise HTTPException(status_code=403, detail="Private memories are locked")
    
    results = orchestrator.private_memory_manager.search_private_memories(
        query=query, category=category, limit=limit
    )
    return {"results": results, "count": len(results)}

# Persona Instruction Management Endpoints
@app.get("/api/personas/manifestos")
async def list_persona_manifestos():
    """List all available persona manifestos"""
    if not orchestrator.persona_instruction_manager:
        raise HTTPException(status_code=503, detail="Persona instruction manager not available")
    return orchestrator.persona_instruction_manager.list_manifestos()

@app.get("/api/personas/manifesto/{persona_id}")
async def get_persona_manifesto(persona_id: str):
    """Get a specific persona manifesto"""
    if not orchestrator.persona_instruction_manager:
        raise HTTPException(status_code=503, detail="Persona instruction manager not available")
    
    manifesto = orchestrator.persona_instruction_manager.get_manifesto(persona_id)
    if not manifesto:
        raise HTTPException(status_code=404, detail="Persona manifesto not found")
    
    return manifesto.to_dict()

@app.post("/api/personas/activate/{persona_id}")
async def activate_persona_manifesto(persona_id: str):
    """Activate a specific persona manifesto"""
    if not orchestrator.persona_instruction_manager:
        raise HTTPException(status_code=503, detail="Persona instruction manager not available")
    
    success = orchestrator.persona_instruction_manager.activate_persona(persona_id)
    if success:
        return {"status": "activated", "persona_id": persona_id}
    else:
        raise HTTPException(status_code=404, detail="Persona manifesto not found")

@app.get("/api/personas/active-instructions")
async def get_active_persona_instructions():
    """Get instruction set for currently active persona"""
    if not orchestrator.persona_instruction_manager:
        raise HTTPException(status_code=503, detail="Persona instruction manager not available")
    
    instructions = orchestrator.persona_instruction_manager.get_active_instructions()
    if not instructions:
        return {"message": "No persona currently active", "instructions": None}
    
    return instructions

@app.put("/api/personas/manifesto/{persona_id}")
async def update_persona_manifesto(persona_id: str, updates: dict):
    """Update an existing persona manifesto"""
    if not orchestrator.persona_instruction_manager:
        raise HTTPException(status_code=503, detail="Persona instruction manager not available")
    
    success = orchestrator.persona_instruction_manager.update_manifesto(persona_id, updates)
    if success:
        return {"status": "updated", "persona_id": persona_id}
    else:
        raise HTTPException(status_code=404, detail="Persona manifesto not found")

# Mirror Mode Endpoints
@app.get("/api/mirror-mode/status")
async def get_mirror_mode_status():
    """Get mirror mode status and statistics"""
    if not orchestrator.mirror_mode_manager:
        raise HTTPException(status_code=503, detail="Mirror mode manager not available")
    return orchestrator.mirror_mode_manager.get_mirror_statistics()

@app.post("/api/mirror-mode/enable")
async def enable_mirror_mode(intensity: float = 0.7, enabled_types: Optional[List[str]] = None):
    """Enable mirror mode with specified settings"""
    if not orchestrator.mirror_mode_manager:
        raise HTTPException(status_code=503, detail="Mirror mode manager not available")
    
    orchestrator.mirror_mode_manager.enable_mirror_mode(intensity, enabled_types)
    return {"status": "enabled", "intensity": intensity, "enabled_types": enabled_types}

@app.post("/api/mirror-mode/disable")
async def disable_mirror_mode():
    """Disable mirror mode"""
    if not orchestrator.mirror_mode_manager:
        raise HTTPException(status_code=503, detail="Mirror mode manager not available")
    
    orchestrator.mirror_mode_manager.disable_mirror_mode()
    return {"status": "disabled"}

@app.get("/api/mirror-mode/session/{session_id}")
async def get_session_reflections(session_id: str):
    """Get all mirror reflections for a specific session"""
    if not orchestrator.mirror_mode_manager:
        raise HTTPException(status_code=503, detail="Mirror mode manager not available")
    
    reflections = orchestrator.mirror_mode_manager.get_session_reflections(session_id)
    return {"session_id": session_id, "reflections": reflections, "count": len(reflections)}

@app.delete("/api/mirror-mode/history")
async def clear_mirror_history(session_id: Optional[str] = None):
    """Clear mirror mode reflection history"""
    if not orchestrator.mirror_mode_manager:
        raise HTTPException(status_code=503, detail="Mirror mode manager not available")
    
    orchestrator.mirror_mode_manager.clear_reflection_history(session_id)
    return {"status": "cleared", "session_id": session_id}

# New Mirror self-report endpoint
@app.post("/api/mirror")
async def get_last_mirror_report(stylized: bool = False):
    """Return the most recent self-report generated by mirror mode."""
    if not orchestrator.mirror_mode_manager:
        raise HTTPException(status_code=503, detail="Mirror mode manager not available")
    if stylized:
        return {"report": orchestrator.mirror_mode_manager.get_last_self_report_styled()}
    report = orchestrator.mirror_mode_manager.get_last_self_report()
    if not report:
        return {"message": "no report"}
    return report

# Search past mirror logs
@app.get("/api/mirror/search")
async def search_mirror_logs(pattern: str, limit: int = 20):
    if not orchestrator.mirror_mode_manager:
        raise HTTPException(status_code=503, detail="Mirror mode manager not available")
    results = orchestrator.mirror_mode_manager.search_log(pattern, limit)
    return {"pattern": pattern, "results": results}

# System Metrics Endpoints
@app.get("/api/metrics/realtime")
async def get_realtime_metrics():
    """Get real-time system metrics"""
    if not orchestrator.metrics_collector:
        raise HTTPException(status_code=503, detail="Metrics collector not available")
    return orchestrator.metrics_collector.get_realtime_status()

@app.get("/api/metrics/models")
async def get_model_usage_metrics():
    """Get detailed model usage statistics"""
    if not orchestrator.metrics_collector:
        raise HTTPException(status_code=503, detail="Metrics collector not available")
    return orchestrator.metrics_collector.get_model_usage_report()

@app.get("/api/metrics/features")
async def get_feature_usage_metrics():
    """Get feature usage statistics"""
    if not orchestrator.metrics_collector:
        raise HTTPException(status_code=503, detail="Metrics collector not available")
    return orchestrator.metrics_collector.get_feature_usage_report()

@app.get("/api/metrics/historical")
async def get_historical_metrics(period: str = "hour", limit: int = 24):
    """Get historical metrics data"""
    if not orchestrator.metrics_collector:
        raise HTTPException(status_code=503, detail="Metrics collector not available")
    
    if period not in ["minute", "hour", "day"]:
        raise HTTPException(status_code=400, detail="Period must be 'minute', 'hour', or 'day'")
    
    return {
        "period": period,
        "limit": limit,
        "data": orchestrator.metrics_collector.get_historical_data(period, limit)
    }

@app.get("/api/metrics/export")
async def export_system_metrics():
    """Export comprehensive system metrics"""
    if not orchestrator.metrics_collector:
        raise HTTPException(status_code=503, detail="Metrics collector not available")
    
    return {
        "export_data": orchestrator.metrics_collector.export_metrics(),
        "export_timestamp": datetime.now().isoformat()
    }

@app.get("/api/metrics/health")
async def get_metrics_health_check():
    """Get system health check from metrics"""
    if not orchestrator.metrics_collector:
        raise HTTPException(status_code=503, detail="Metrics collector not available")
    return orchestrator.metrics_collector.get_health_check()

# =============================================================================
# END ADVANCED FEATURES API ENDPOINTS
# =============================================================================

if __name__ == "__main__":
    port = int(os.getenv('DOLPHIN_PORT', 8000))
    logger.info(f"🐬 Starting Enhanced Dolphin Backend on port {port}")
    logger.info("Features: Personality System, Memory Management, Analytics Logging")
    uvicorn.run(app, host="0.0.0.0", port=port)
