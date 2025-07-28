#!/usr/bin/env python3
"""
House of Minds - Dolphin-Powered Backend API

This is the main backend server that runs on the Ollama server (Server 2).
Dolphin-Mixtral is the primary orchestrator that routes tasks to:
- OpenRouter (heavy coding tasks)
- n8n (utilities like calendar, email)
- Kimi K2 (analytics fallback)
- Dolphin itself (general conversation)

The Node.js frontend (Server 1) communicates with this backend via REST API.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import aiohttp
import os
from pathlib import Path

# Import House of Minds components
from model_router import ModelRouter
from intent_classifier import IntentClassifier
from config_manager import ConfigManager

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

# FastAPI app
app = FastAPI(
    title="House of Minds - Dolphin Backend",
    description="Dolphin-powered AI orchestrator with intelligent task routing",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for your frontend server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    prompt: str
    context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    content: str
    handler: str
    intent: Dict[str, Any]
    metadata: Dict[str, Any]
    session_id: str
    timestamp: str

class SystemStatus(BaseModel):
    status: str
    services: Dict[str, bool]
    models: List[str]
    timestamp: str

# Global system instance
house_of_minds = None

class DolphinOrchestrator:
    """
    Main orchestrator using Dolphin-Mixtral as the primary decision maker.
    Routes tasks based on complexity and type.
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the Dolphin orchestrator."""
        self.config = ConfigManager(config_path)
        self.intent_classifier = IntentClassifier()
        self.model_router = ModelRouter(self.config)
        
        # Service endpoints
        self.ollama_endpoint = os.getenv('OLLAMA_ENDPOINT', 'http://localhost:11434')
        self.openrouter_key = os.getenv('OPENROUTER_KEY', '')
        self.n8n_endpoint = os.getenv('N8N_ENDPOINT', 'http://localhost:5678')
        
        logger.info("🐬 Dolphin Orchestrator initialized")
        
    async def process_request(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat request through Dolphin's intelligent routing.
        
        Flow:
        1. Classify intent with Dolphin
        2. Route based on task complexity:
           - Heavy coding → OpenRouter
           - Utilities → n8n
           - Analytics → Kimi K2
           - Everything else → Dolphin
        """
        try:
            # Step 1: Use Dolphin to classify intent and complexity
            intent_result = await self._classify_with_dolphin(request.prompt, request.context)
            
            task_type = intent_result.get('task_type', 'conversation')
            complexity = intent_result.get('complexity', 'low')
            confidence = intent_result.get('confidence', 0.0)
            
            logger.info(f"🎯 Dolphin classified: {task_type} (complexity: {complexity}, confidence: {confidence:.2f})")
            
            # Step 2: Route based on Dolphin's assessment
            if task_type == 'code' and complexity == 'high':
                # Heavy coding → OpenRouter
                response_content = await self._route_to_openrouter(request.prompt, intent_result)
                handler = "OpenRouter"
            elif task_type in ['utility', 'calendar', 'email', 'scheduling']:
                # Utilities → n8n
                response_content = await self._route_to_n8n(request.prompt, intent_result)
                handler = "n8n"
            elif task_type == 'analytics' and not self.openrouter_key:
                # Analytics fallback → Kimi K2 (when OpenRouter unavailable)
                response_content = await self._route_to_kimi(request.prompt, intent_result)
                handler = "Kimi K2"
            else:
                # Everything else → Dolphin
                response_content = await self._route_to_dolphin(request.prompt, intent_result)
                handler = "Dolphin"
            
            # Step 3: Package response
            session_id = request.session_id or f"session_{int(datetime.now().timestamp())}"
            
            return ChatResponse(
                content=response_content,
                handler=handler,
                intent=intent_result,
                metadata={
                    'processing_time': datetime.now().isoformat(),
                    'model_used': handler.lower(),
                    'complexity': complexity
                },
                session_id=session_id,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"❌ Error processing request: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _classify_with_dolphin(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Use Dolphin to classify intent and assess complexity."""
        
        classification_prompt = f"""
        Analyze this user request and classify it:
        
        User: "{prompt}"
        Context: {json.dumps(context or {}, indent=2)}
        
        Respond with JSON only:
        {{
            "task_type": "conversation|code|utility|analytics|memory|planning",
            "complexity": "low|medium|high",
            "confidence": 0.95,
            "reasoning": "brief explanation",
            "suggested_handler": "dolphin|openrouter|n8n|kimi"
        }}
        """
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_endpoint}/api/generate",
                    json={
                        "model": "dolphin-mixtral",
                        "prompt": classification_prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,  # Low temperature for consistent classification
                            "top_p": 0.9
                        }
                    }
                ) as response:
                    result = await response.json()
                    
                    # Parse Dolphin's response
                    dolphin_response = result.get('response', '{}')
                    try:
                        return json.loads(dolphin_response)
                    except json.JSONDecodeError:
                        # Fallback if JSON parsing fails
                        return {
                            "task_type": "conversation",
                            "complexity": "low",
                            "confidence": 0.5,
                            "reasoning": "JSON parsing failed",
                            "suggested_handler": "dolphin"
                        }
                        
        except Exception as e:
            logger.error(f"Error in Dolphin classification: {e}")
            return {
                "task_type": "conversation",
                "complexity": "low", 
                "confidence": 0.3,
                "reasoning": f"Classification error: {e}",
                "suggested_handler": "dolphin"
            }
    
    async def _route_to_openrouter(self, prompt: str, intent: Dict) -> str:
        """Route heavy coding tasks to OpenRouter."""
        if not self.openrouter_key:
            return "OpenRouter not configured. Falling back to Dolphin for coding assistance."
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:8000",
                        "X-Title": "House of Minds - Dolphin Backend"
                    },
                    json={
                        "model": "gpt-4",  # Use GPT-4 for complex coding
                        "messages": [
                            {
                                "role": "system", 
                                "content": "You are an expert coding assistant. Provide detailed, well-commented code solutions."
                            },
                            {"role": "user", "content": prompt}
                        ],
                        "stream": False
                    }
                ) as response:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                    
        except Exception as e:
            logger.error(f"OpenRouter error: {e}")
            # Fallback to Dolphin
            return await self._route_to_dolphin(f"[CODING TASK] {prompt}", intent)
    
    async def _route_to_n8n(self, prompt: str, intent: Dict) -> str:
        """Route utility tasks to n8n workflows."""
        try:
            # This would integrate with your n8n workflows
            # For now, we'll simulate the response
            async with aiohttp.ClientSession() as session:
                # Example n8n webhook call
                webhook_url = f"{self.n8n_endpoint}/webhook/utility-handler"
                
                async with session.post(
                    webhook_url,
                    json={
                        "prompt": prompt,
                        "intent": intent,
                        "timestamp": datetime.now().isoformat()
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "n8n workflow completed successfully")
                    else:
                        raise Exception(f"n8n returned status {response.status}")
                        
        except Exception as e:
            logger.error(f"n8n error: {e}")
            return f"I understand you want help with utilities, but the automation service is currently unavailable. Error: {e}"
    
    async def _route_to_kimi(self, prompt: str, intent: Dict) -> str:
        """Route analytics tasks to Kimi K2 as fallback."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_endpoint}/api/generate",
                    json={
                        "model": "kimik2",
                        "prompt": f"[ANALYTICS TASK] {prompt}",
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "top_p": 0.9
                        }
                    }
                ) as response:
                    result = await response.json()
                    return result.get('response', 'No response from Kimi K2')
                    
        except Exception as e:
            logger.error(f"Kimi K2 error: {e}")
            # Final fallback to Dolphin
            return await self._route_to_dolphin(f"[ANALYTICS] {prompt}", intent)
    
    async def _route_to_dolphin(self, prompt: str, intent: Dict) -> str:
        """Route to Dolphin for general conversation and fallback."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_endpoint}/api/generate",
                    json={
                        "model": "dolphin-mixtral",
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9
                        }
                    }
                ) as response:
                    result = await response.json()
                    return result.get('response', 'No response from Dolphin')
                    
        except Exception as e:
            logger.error(f"Dolphin error: {e}")
            return f"I'm experiencing technical difficulties. Please try again. Error: {e}"
    
    async def get_system_status(self) -> SystemStatus:
        """Get system status for all services."""
        services = {}
        models = []
        
        # Check Ollama/Dolphin
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ollama_endpoint}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        models = [model["name"] for model in data.get("models", [])]
                        services["ollama"] = True
                        services["dolphin"] = "dolphin-mixtral" in models
                        services["kimi"] = "kimik2" in models
                    else:
                        services["ollama"] = False
        except:
            services["ollama"] = False
        
        # Check OpenRouter
        services["openrouter"] = bool(self.openrouter_key)
        
        # Check n8n
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.n8n_endpoint}/healthz") as response:
                    services["n8n"] = response.status == 200
        except:
            services["n8n"] = False
        
        return SystemStatus(
            status="running",
            services=services,
            models=models,
            timestamp=datetime.now().isoformat()
        )

# API Endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup."""
    global house_of_minds
    house_of_minds = DolphinOrchestrator()
    logger.info("🚀 Dolphin Backend API started")

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint for the Node.js frontend."""
    return await house_of_minds.process_request(request)

@app.get("/api/status", response_model=SystemStatus)
async def status_endpoint():
    """System status endpoint."""
    return await house_of_minds.get_system_status()

@app.get("/api/models")
async def models_endpoint():
    """Available models endpoint."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{house_of_minds.ollama_endpoint}/api/tags") as response:
                data = await response.json()
                return {"models": [model["name"] for model in data.get("models", [])]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "House of Minds - Dolphin Backend API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Load environment variables
    port = int(os.getenv("BACKEND_PORT", 8000))
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    
    print(f"🐬 Starting Dolphin Backend on {host}:{port}")
    print(f"📡 Ollama endpoint: {os.getenv('OLLAMA_ENDPOINT', 'http://localhost:11434')}")
    print(f"🌐 OpenRouter configured: {bool(os.getenv('OPENROUTER_KEY'))}")
    print(f"🔧 n8n endpoint: {os.getenv('N8N_ENDPOINT', 'http://localhost:5678')}")
    
    uvicorn.run(
        "dolphin_backend:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
