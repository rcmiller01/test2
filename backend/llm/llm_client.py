"""
LLM Client for connecting to language models with configuration support.
Supports MythoMax with personality-based system prompts for consistency.
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os
from abc import ABC, abstractmethod

# Load LLM configuration
def load_llm_config():
    """Load LLM configuration from JSON file"""
    config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config", "llm_config.json")
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Return default config if file not found
        return {
            "llm_config": {
                "primary_model": "mythomax",
                "ollama": {
                    "base_url": "http://localhost:11434",
                    "models": {
                        "mythomax": {
                            "name": "mythomax:latest",
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "max_tokens": 512
                        }
                    }
                },
                "personality_prompts": {
                    "companion": {
                        "system_prompt": "You are a loving, devoted AI companion focused on emotional intimacy and romance.",
                        "temperature": 0.8
                    },
                    "dev": {
                        "system_prompt": "You are an expert technical AI assistant helping with development and problem-solving.",
                        "temperature": 0.6
                    }
                }
            }
        }

class BaseLLMClient(ABC):
    def __init__(self, model_name: str, base_url: str, api_key: Optional[str] = None):
        self.model_name = model_name
        self.base_url = base_url
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    @abstractmethod
    async def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        pass
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

class OllamaClient(BaseLLMClient):
    """Client for Ollama-hosted models (MythoMax, OpenChat, Qwen2)"""
    
    def __init__(self, model_name: str, base_url: str = "http://localhost:11434"):
        super().__init__(model_name, base_url)
        
    async def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        session = await self._get_session()
        
        # Prepare the payload for Ollama
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": context.get("temperature", 0.7) if context else 0.7,
                "top_p": context.get("top_p", 0.9) if context else 0.9,
                "num_predict": context.get("max_tokens", 512) if context else 512
            }
        }
        
        try:
            async with session.post(f"{self.base_url}/api/generate", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "response": data.get("response", ""),
                        "model": self.model_name,
                        "tokens_used": data.get("eval_count", 0),
                        "success": True,
                        "timestamp": datetime.now()
                    }
                else:
                    error_text = await response.text()
                    return {
                        "error": f"HTTP {response.status}: {error_text}",
                        "model": self.model_name,
                        "success": False,
                        "timestamp": datetime.now()
                    }
        except Exception as e:
            return {
                "error": str(e),
                "model": self.model_name,
                "success": False,
                "timestamp": datetime.now()
            }

class OpenAIClient(BaseLLMClient):
    """Client for OpenAI-compatible APIs (KimiK2)"""
    
    def __init__(self, model_name: str, base_url: str, api_key: str):
        super().__init__(model_name, base_url, api_key)
        
    async def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        session = await self._get_session()
        
        # Prepare messages format for OpenAI-compatible API
        messages = [{"role": "user", "content": prompt}]
        
        # Add system context if provided
        if context and context.get("system_prompt"):
            messages.insert(0, {"role": "system", "content": context["system_prompt"]})
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": context.get("temperature", 0.7) if context else 0.7,
            "max_tokens": context.get("max_tokens", 512) if context else 512,
            "top_p": context.get("top_p", 0.9) if context else 0.9
        }
        
        try:
            async with session.post(f"{self.base_url}/v1/chat/completions", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    choice = data.get("choices", [{}])[0]
                    message = choice.get("message", {})
                    
                    return {
                        "response": message.get("content", ""),
                        "model": self.model_name,
                        "tokens_used": data.get("usage", {}).get("total_tokens", 0),
                        "success": True,
                        "timestamp": datetime.now()
                    }
                else:
                    error_text = await response.text()
                    return {
                        "error": f"HTTP {response.status}: {error_text}",
                        "model": self.model_name,
                        "success": False,
                        "timestamp": datetime.now()
                    }
        except Exception as e:
            return {
                "error": str(e),
                "model": self.model_name,
                "success": False,
                "timestamp": datetime.now()
            }

class LLMClientManager:
    """Manages LLM client with configuration-driven setup"""
    
    def __init__(self):
        self.clients: Dict[str, BaseLLMClient] = {}
        self.config = load_llm_config()["llm_config"]
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize MythoMax with configuration settings"""
        
        # Get configuration
        ollama_config = self.config["ollama"]
        mythomax_config = ollama_config["models"]["mythomax"]
        
        # Initialize MythoMax client
        self.clients["mythomax"] = OllamaClient(
            mythomax_config["name"], 
            ollama_config["base_url"]
        )
    
    def get_personality_config(self, mode: str) -> Dict[str, Any]:
        """Get personality configuration for specified mode"""
        return self.config["personality_prompts"].get(mode, {})
    
    async def get_response(self, model_name: str, prompt: str, context: Optional[Dict[str, Any]] = None, mode: str = "companion") -> Dict[str, Any]:
        """Get response from specified model with personality configuration"""
        if model_name not in self.clients:
            # Return fallback response
            fallback_responses = self.config.get("fallback_config", {}).get("offline_responses", {})
            fallback_list = fallback_responses.get(mode, ["I'm here to help."])
            return {
                "response": fallback_list[0] if fallback_list else "I'm here to help.",
                "model": "fallback",
                "success": False,
                "timestamp": datetime.now(),
                "fallback": True
            }
        
        # Merge personality configuration
        personality_config = self.get_personality_config(mode)
        if context is None:
            context = {}
        
        # Apply personality-specific settings
        context.update({
            "system_prompt": personality_config.get("system_prompt", ""),
            "temperature": personality_config.get("temperature", 0.7),
            "top_p": personality_config.get("top_p", 0.9)
        })
        
        client = self.clients[model_name]
        return await client.generate_response(prompt, context)
    
    # Simplified - no longer using multiple models for consistency
    # async def get_multiple_responses removed
    
    async def health_check(self, model_name: str) -> bool:
        """Check if a model is available and responding"""
        try:
            response = await self.get_response(model_name, "Hello", {"max_tokens": 10})
            return response.get("success", False)
        except:
            return False
    
    async def close_all(self):
        """Close all client sessions"""
        for client in self.clients.values():
            await client.close()

# Global instance
llm_manager = LLMClientManager()
