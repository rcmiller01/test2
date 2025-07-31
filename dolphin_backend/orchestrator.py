
import asyncio
import logging
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

import aiohttp
from .mcp_bridge import route_to_mcp

from personality_system import PersonalitySystem
from memory_system import MemorySystem
from analytics_logger import AnalyticsLogger
from utils.preference_vote_store import PreferenceVoteStore
from handler_registry import handler_registry, HandlerState
from fallback_personas import get as get_fallback_persona
from judge_agent import JudgeAgent
from agents.n8n_agent import N8nAgent

# Advanced features

try:
    from reflection_engine import ReflectionEngine
    from connectivity_manager import ConnectivityManager
    from private_memory import PrivateMemoryManager
    from persona_instruction_manager import PersonaInstructionManager
    from mirror_mode import MirrorModeManager
    from system_metrics import MetricsCollector
    ADVANCED_FEATURES_AVAILABLE = True

except ImportError:
    ADVANCED_FEATURES_AVAILABLE = False

logger = logging.getLogger(__name__)

MCP_HOST = os.getenv("MCP_HOST", "http://localhost:8000")


async def route_to_mcp(task_request: Dict[str, Any]) -> Dict[str, Any]:
    """Send a structured task to the MCP server and return the response."""
    start = time.time()
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"{MCP_HOST}/api/mcp/route-task", json=task_request
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                elapsed = int((time.time() - start) * 1000)
                logger.info(
                    f"MCP response: request_id={task_request.get('request_id')}, "
                    f"intent_type={task_request.get('intent_type')}, "
                    f"time_ms={elapsed}"
                )
                return data
    except Exception as e:
        logger.error(f"Error routing to MCP: {e}")
        return {"success": False, "error": str(e)}

class DolphinOrchestrator:
    """Dolphin orchestrator with personality, memory and analytics"""


    def __init__(self):
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.openrouter_key = os.getenv('OPENROUTER_KEY')
        self.n8n_url = os.getenv('N8N_URL', 'http://localhost:5678')

        # External agents
        self.n8n_agent = N8nAgent(self.n8n_url)


        # Model configuration
        self.primary_model = os.getenv('PRIMARY_MODEL', 'llama2-uncensored')
        self.fallback_model = os.getenv('FALLBACK_MODEL', 'mistral:7b-instruct-q4_K_M')

        # Initialize subsystems

        self.personality_system = PersonalitySystem()
        self.memory_system = MemorySystem()
        self.analytics_logger = AnalyticsLogger()
        self.preference_vote_store = PreferenceVoteStore()


        # Advanced features placeholders

        self.reflection_engine = None
        self.connectivity_manager = None
        self.private_memory_manager = None
        self.persona_instruction_manager = None
        self.mirror_mode_manager = None
        self.metrics_collector = None


        logger.info("🐬 Dolphin Orchestrator initialized")

    async def initialize_advanced_features(self):
        if not ADVANCED_FEATURES_AVAILABLE:
            logger.warning("Advanced features not available")
            return
        try:
            self.reflection_engine = ReflectionEngine(self.memory_system, self.analytics_logger)
            self.mirror_mode_manager = MirrorModeManager(self.analytics_logger)

            self.connectivity_manager = ConnectivityManager(
                self.analytics_logger,
                on_status_change=self._on_handler_status_change,
                mirror_mode_manager=self.mirror_mode_manager,
            )

            self.private_memory_manager = PrivateMemoryManager()
            self.persona_instruction_manager = PersonaInstructionManager()
            self.metrics_collector = MetricsCollector(self.analytics_logger)

            asyncio.create_task(self.reflection_engine.start_background_reflection())
            asyncio.create_task(self.connectivity_manager.start_monitoring())
            logger.info("Advanced features initialized")
        except Exception as e:
            logger.error(f"Error initializing advanced features: {e}")

    def _on_handler_status_change(self, status: Dict[str, Any]) -> None:
        logger.info(f"Handler status updated: {status.get('current_mode')}")

    async def _record_judgment(self, session_id: str, judgment: Dict[str, Any], persona: str, persona_token: Optional[str], request_id: str) -> None:

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

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ollama_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        available_models = [model["name"] for model in data.get("models", [])]

                        if preferred_model and preferred_model in available_models:
                            return preferred_model
                        if self.primary_model in available_models:
                            return self.primary_model
                        if self.fallback_model in available_models:
                            logger.warning(
                                f"Primary model '{self.primary_model}' not available, using fallback '{self.fallback_model}'"
                            )
                            return self.fallback_model
                        if available_models:
                            return available_models[0]

                        raise Exception("No models available in Ollama")
                    else:
                        raise Exception(f"Failed to connect to Ollama: {response.status}")
        except Exception as e:
            logger.error(f"Error checking available models: {e}")

            return self.primary_model

    async def process_chat_request(self, request, persona_token: Optional[str] = None):
        start_time = time.time()
        request_id = None
        try:
            if request.persona:
                self.personality_system.set_persona(request.persona)
            current_persona = self.personality_system.get_current_persona()
            session_id = request.session_id or self.memory_system.create_session()
            session_context = self.memory_system.get_session_context(
                session_id, persona=current_persona["name"], persona_token=persona_token
            )

            enhanced_context = {
                **(request.context or {}),
                "session_context": session_context,
                "persona": current_persona["name"],
                "memory_focus": self.personality_system.get_memory_focus_areas()
            }

            route = await self.classify_task(request.message, enhanced_context)
            route = self.personality_system.adjust_routing_for_persona(route.__dict__)
            request_id = self.analytics_logger.log_routing_decision(
                request.dict(), route, current_persona["name"]
            )
            formatted_message = self.personality_system.format_prompt_with_persona(
                request.message, enhanced_context
            )
            intent_type = route.get("intent_type") or route.get("task_type")

            if route["handler"].lower() in ("utility", "agent"):
                task_payload = {
                    "intent_type": intent_type,
                    "payload": {
                        "message": request.message,
                        "context": enhanced_context,
                    },
                    "source": "dolphin",
                    "request_id": request_id,
                }
                logger.info(f"Routed to MCP: intent_type={intent_type}")
                mcp_start = time.time()
                mcp_result = await route_to_mcp(task_payload)
                mcp_latency = time.time() - mcp_start
                self.analytics_logger.log_performance_metrics(
                    request_id, "MCP", mcp_latency, mcp_result.get("success", False)
                )
                if mcp_result.get("success"):
                    return mcp_result
                logger.warning("MCP server unavailable, falling back to local handler")

            if route.get("task_type") in {"utility", "agent"}:
                task_request = {
                    "intent_type": route.get("task_type"),
                    "payload": {"message": request.message, **(request.context or {})},
                    "source": "dolphin",
                    "request_id": request_id,
                }
                mcp_start = time.time()
                mcp_response = await route_to_mcp(task_request)
                logger.info(
                    "Routed to MCP: intent_type=%s request_id=%s time_ms=%d",
                    task_request["intent_type"],
                    request_id,
                    int((time.time() - mcp_start) * 1000),
                )
                return mcp_response

            if route["handler"] == "OPENROUTER":
                response_text = await self.handle_openrouter_request(formatted_message, enhanced_context)
            elif route["handler"] == "N8N":
                response_text = await self.handle_n8n_request(formatted_message, enhanced_context)
            elif route["handler"] == "KIMI_K2":
                response_text = await self.handle_kimi_fallback(formatted_message, enhanced_context)
            else:
                response_text = await self.handle_dolphin_request(formatted_message, enhanced_context)

            response_text = apply_persona_filter(response_text, current_persona["name"])

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

            judge = JudgeAgent()
            judgment = judge.evaluate(
                response_text,
                {
                    "session_context": session_context,
                    "persona": current_persona["name"],
                    "session_id": session_id,
                },
            )

            asyncio.create_task(
                self._record_judgment(session_id, judgment, current_persona["name"], persona_token, request_id)
            )
            latency = time.time() - start_time
            self.analytics_logger.log_performance_metrics(
                request_id, route["handler"], latency, True
            )
            return {
                "response": response_text,
                "handler": route["handler"],
                "reasoning": route["reasoning"],
                "metadata": {

                    "persona_applied": route.get("persona_applied", current_persona["name"]),
                    "confidence": route["confidence"],
                    "latency_seconds": round(latency, 3),
                    "session_message_count": session_context["total_messages"] + 1,
                    "sentiment_trend": session_context["sentiment_trend"]
                },

                "timestamp": datetime.now().isoformat(),
                "session_id": session_id,
                "persona_used": current_persona["name"],
                "judgment": judgment
            }
        except Exception as e:
            logger.error(f"Chat processing error: {e}")

            if request_id:
                latency = time.time() - start_time
                self.analytics_logger.log_performance_metrics(
                    request_id, "ERROR", latency, False, error_message=str(e)
                )

            return {
                "response": f"I encountered an error processing your request: {str(e)}",
                "handler": "ERROR",
                "reasoning": "Exception occurred during processing",
                "metadata": {"error": str(e), "timestamp": datetime.now().isoformat()},
                "timestamp": datetime.now().isoformat(),
                "session_id": request.session_id or "unknown",
                "persona_used": self.personality_system.get_current_persona()["name"],
                "judgment": None
            }

    async def classify_task(self, message: str, context: Optional[Dict] = None):
        classification_prompt = f"""Analyze this user message and determine the best handler:\n\nMessage: \"{message}\"\nContext: {json.dumps(context or {}, indent=2)}\n\nChoose from these handlers:\n1. DOLPHIN - General conversation, questions, explanations\n2. OPENROUTER - Complex coding, programming tasks, technical documentation\n3. N8N - Utilities like email, calendar, file operations, web scraping\n4. KIMI_K2 - Data analysis, analytics, when OpenRouter is unavailable\n\nRespond in JSON format:\n{{\n    \"task_type\": \"conversation|coding|utility|analytics\",\n    \"handler\": \"DOLPHIN|OPENROUTER|N8N|KIMI_K2\",\n    \"confidence\": 0.0-1.0,\n    \"reasoning\": \"Brief explanation of choice\"\n}}"""
        try:
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
                        data = json.loads(result.get("response", "{}"))
                        return data
                    else:
                        raise Exception(f"Ollama classification error: {response.status}")
        except Exception as e:
            logger.error(f"Classification error: {e}")
            return {"task_type": "conversation", "handler": "DOLPHIN", "confidence": 0.0, "reasoning": str(e)}

    async def handle_dolphin_request(self, message: str, context: Optional[Dict] = None) -> str:
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"model": self.primary_model, "prompt": message, "stream": False}
                async with session.post(f"{self.ollama_url}/api/generate", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "")
                    else:
                        raise Exception(f"Ollama generation error: {response.status}")
        except Exception as e:
            logger.error(f"Dolphin request error: {e}")
            return f"Dolphin service unavailable. Error: {str(e)}"

    async def handle_openrouter_request(self, message: str, context: Optional[Dict] = None) -> str:
        if not self.openrouter_key:
            return "OpenRouter key not configured"
        try:
            headers = {"Authorization": f"Bearer {self.openrouter_key}"}
            async with aiohttp.ClientSession() as session:
                payload = {"model": "gpt-4", "prompt": message, "stream": False}
                async with session.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    else:
                        raise Exception(f"OpenRouter error: {response.status}")
        except Exception as e:
            logger.error(f"OpenRouter request error: {e}")
            return f"OpenRouter service unavailable. Error: {str(e)}"

    async def handle_n8n_request(self, message: str, context: Optional[Dict] = None, task_type: str = "workflow") -> str:
        """Send utility tasks to the n8n agent and fallback on failure."""
        payload = {"message": message, "context": context or {}}
        try:
            result = await self.n8n_agent.execute(task_type, payload)
            self.analytics_logger.log_custom_event(
                "n8n_task",
                {"task_type": task_type, "success": result.get("success", False)}
            )
            if result.get("success"):
                data = result.get("data", {})
                # n8n workflows may return {'message': 'text'} or generic data
                return data.get("message") or str(data)
            # Fallback to OpenRouter if configured
            if self.openrouter_key:
                return await self.handle_openrouter_request(message, context)
            return result.get("error", "Utility task failed")
        except Exception as e:
            logger.error(f"n8n request error: {e}")
            if self.openrouter_key:
                return await self.handle_openrouter_request(message, context)
            return f"Utility service temporarily unavailable. Error: {str(e)}"

    async def handle_kimi_fallback(self, message: str, context: Optional[Dict] = None) -> str:

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

# Singleton orchestrator
orchestrator = DolphinOrchestrator()

orchestrator = DolphinOrchestrator()

