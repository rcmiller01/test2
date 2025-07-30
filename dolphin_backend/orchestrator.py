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
from pydantic import BaseModel, validator
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
from utils.preference_vote_store import PreferenceVoteStore
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

class PreferenceVoteSchema(BaseModel):
    prompt: str
    response_a: str
    response_b: str
    winner: str

    @validator('winner')
    def validate_winner(cls, v):
        if v not in ('a', 'b'):
            raise ValueError("winner must be 'a' or 'b'")
        return v

class TaskRoute(BaseModel):
    task_type: str
    confidence: float
    reasoning: str
    handler: str


class PreferenceVoteRequest(BaseModel):
    prompt: str
    response_a: str
    response_b: str
    winner: str  # 'a' or 'b'

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
        self.preference_vote_store = PreferenceVoteStore()
        
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

