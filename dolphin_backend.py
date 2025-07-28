#!/usr/bin/env python3
"""
Dolphin Backend - AI Orchestration Server

Multi-server architecture with Dolphin as the primary orchestrator:
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
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aiohttp
import uvicorn
import os
from pathlib import Path

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

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    handler: str
    reasoning: str
    metadata: Dict[str, Any]
    timestamp: str

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
    Main Dolphin orchestrator that routes tasks intelligently
    """
    
    def __init__(self):
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.openrouter_key = os.getenv('OPENROUTER_KEY')
        self.n8n_url = os.getenv('N8N_URL', 'http://localhost:5678')
        self.session_data = {}
        
        logger.info("🐬 Dolphin Orchestrator initialized")
        
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
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": "dolphin-mixtral",
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
        """Handle requests with Dolphin directly"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": "dolphin-mixtral",
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

    async def process_message(self, message: str, context: Optional[Dict] = None, session_id: Optional[str] = None) -> ChatResponse:
        """
        Main message processing pipeline
        """
        try:
            # Step 1: Classify the task
            route = await self.classify_task(message, context)
            logger.info(f"🎯 Task classified: {route.handler} ({route.confidence:.2f}) - {route.reasoning}")
            
            # Step 2: Route to appropriate handler
            if route.handler == "DOLPHIN":
                response_text = await self.handle_dolphin_request(message, context)
            elif route.handler == "OPENROUTER":
                response_text = await self.handle_openrouter_request(message, context)
            elif route.handler == "N8N":
                response_text = await self.handle_n8n_request(message, context)
            elif route.handler == "KIMI_K2":
                response_text = await self.handle_kimi_fallback(message, context)
            else:
                response_text = await self.handle_dolphin_request(message, context)
            
            # Step 3: Build response
            response = ChatResponse(
                response=response_text,
                handler=route.handler,
                reasoning=route.reasoning,
                metadata={
                    "task_type": route.task_type,
                    "confidence": route.confidence,
                    "session_id": session_id,
                    "processing_time": datetime.now().isoformat()
                },
                timestamp=datetime.now().isoformat()
            )
            
            # Store session data
            if session_id:
                if session_id not in self.session_data:
                    self.session_data[session_id] = []
                self.session_data[session_id].append({
                    "message": message,
                    "response": response_text,
                    "handler": route.handler,
                    "timestamp": datetime.now().isoformat()
                })
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Message processing error: {e}")
            return ChatResponse(
                response=f"I encountered an error processing your request: {str(e)}",
                handler="ERROR",
                reasoning="Exception occurred during processing",
                metadata={"error": str(e)},
                timestamp=datetime.now().isoformat()
            )

# Global orchestrator instance
orchestrator = DolphinOrchestrator()

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint"""
    return await orchestrator.process_message(
        message=request.message,
        context=request.context,
        session_id=request.session_id
    )

@app.get("/api/status")
async def status_endpoint():
    """Health check and system status"""
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "ollama": orchestrator.ollama_url,
            "openrouter_configured": bool(orchestrator.openrouter_key),
            "n8n": orchestrator.n8n_url
        },
        "active_sessions": len(orchestrator.session_data)
    }

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session history"""
    if session_id in orchestrator.session_data:
        return {"session_id": session_id, "history": orchestrator.session_data[session_id]}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@app.delete("/api/sessions/{session_id}")
async def clear_session(session_id: str):
    """Clear session history"""
    if session_id in orchestrator.session_data:
        del orchestrator.session_data[session_id]
        return {"message": "Session cleared"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

if __name__ == "__main__":
    port = int(os.getenv('DOLPHIN_PORT', 8000))
    logger.info(f"🐬 Starting Dolphin Backend on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
