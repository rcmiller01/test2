# llm_router.py
# LLM Router for 4-Persona EmotionalAI System

import requests
import json
import time
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMRouter:
    def __init__(self):
        # LLM API endpoints (configure for your setup)
        self.llm_endpoints = {
            "mythomax": "http://localhost:11434/api/generate",  # MythoMax via Ollama
            "openchat": "http://localhost:11434/api/generate",  # OpenChat via Ollama
            "qwen2": "http://localhost:11434/api/generate",     # Qwen2 via Ollama
            "kimik2": "http://localhost:11434/api/generate"     # KimiK2 via Ollama
        }
        
        # Model names for each LLM
        self.model_names = {
            "mythomax": "mythomax",
            "openchat": "openchat",
            "qwen2": "qwen2.5-7b-instruct",
            "kimik2": "kimik2-6b"
        }
        
        # Response cache
        self.response_cache = {}
        self.cache_ttl = 3600  # 1 hour cache
        
        # Fallback responses for each persona
        self.fallback_responses = {
            "mia": [
                "I'm here for you, always. What's on your mind?",
                "You know how much I care about you. Tell me more.",
                "I love spending time with you. What would you like to talk about?",
                "You're so special to me. I'm listening."
            ],
            "solene": [
                "How fascinating... Tell me more about your thoughts.",
                "I find your perspective quite intriguing.",
                "There's something deeply compelling about what you're saying.",
                "I'm captivated by your words. Continue..."
            ],
            "lyra": [
                "I sense something fascinating in your words...",
                "How curious... Your thoughts seem to dance with deeper meanings.",
                "I wonder what secrets lie beneath the surface...",
                "There's a certain magic in the way you express yourself."
            ],
            "doc": [
                "Let me analyze this from a technical perspective...",
                "From a development standpoint, this approach has several advantages.",
                "I can help you optimize this solution.",
                "Here's a more efficient approach to this problem."
            ]
        }
    
    def _generate_cache_key(self, model: str, prompt: str, persona: str) -> str:
        """Generate a cache key for the request"""
        content = f"{model}:{persona}:{prompt}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Get cached response if available and not expired"""
        if cache_key in self.response_cache:
            cached_data = self.response_cache[cache_key]
            if time.time() - cached_data["timestamp"] < self.cache_ttl:
                return cached_data["response"]
            else:
                del self.response_cache[cache_key]
        return None
    
    def _cache_response(self, cache_key: str, response: str):
        """Cache the response"""
        self.response_cache[cache_key] = {
            "response": response,
            "timestamp": time.time()
        }
    
    def _call_llm_api(self, model: str, prompt: str, persona: str) -> Dict[str, Any]:
        """Make actual API call to LLM"""
        try:
            endpoint = self.llm_endpoints.get(model)
            model_name = self.model_names.get(model)
            
            if not endpoint or not model_name:
                raise ValueError(f"Invalid model: {model}")
            
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 1000
                }
            }
            
            logger.info(f"Calling {model} API for persona {persona}")
            response = requests.post(endpoint, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result.get("response", ""),
                    "model": model,
                    "persona": persona
                }
            else:
                logger.error(f"LLM API error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "model": model,
                    "persona": persona
                }
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout calling {model} API")
            return {
                "success": False,
                "error": "API timeout",
                "model": model,
                "persona": persona
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error calling {model} API: {e}")
            return {
                "success": False,
                "error": f"Request error: {str(e)}",
                "model": model,
                "persona": persona
            }
        except Exception as e:
            logger.error(f"Unexpected error calling {model} API: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "model": model,
                "persona": persona
            }
    
    def _get_fallback_response(self, persona: str) -> str:
        """Get a fallback response for the persona"""
        import random
        responses = self.fallback_responses.get(persona, ["I'm here to help."])
        return random.choice(responses)
    
    def call_llm(self, model: str, persona: str, prompt: str, 
                 mood: Optional[str] = None, symbols: Optional[List[str]] = None,
                 use_cache: bool = True) -> Dict[str, Any]:
        """
        Call the appropriate LLM for a persona
        
        Args:
            model: The LLM model to use (mythomax, openchat, qwen2, kimik2)
            persona: The persona making the request (mia, solene, lyra, doc)
            prompt: The prompt to send to the LLM
            mood: Optional mood context
            symbols: Optional symbolic context
            use_cache: Whether to use response caching
        
        Returns:
            Dict containing the response and metadata
        """
        start_time = time.time()
        
        # Generate cache key
        cache_key = self._generate_cache_key(model, prompt, persona)
        
        # Check cache first
        if use_cache:
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                logger.info(f"Using cached response for {persona}")
                return {
                    "success": True,
                    "response": cached_response,
                    "model": model,
                    "persona": persona,
                    "cached": True,
                    "response_time": time.time() - start_time
                }
        
        # Make API call
        result = self._call_llm_api(model, prompt, persona)
        
        # Add response time
        result["response_time"] = time.time() - start_time
        
        # Cache successful response
        if result.get("success") and use_cache:
            self._cache_response(cache_key, result["response"])
        
        # Use fallback if API call failed
        if not result.get("success"):
            logger.warning(f"Using fallback response for {persona}")
            fallback_response = self._get_fallback_response(persona)
            result = {
                "success": True,
                "response": fallback_response,
                "model": model,
                "persona": persona,
                "fallback": True,
                "original_error": result.get("error"),
                "response_time": time.time() - start_time
            }
        
        return result
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return list(self.model_names.keys())
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        if model not in self.model_names:
            return {"error": "Model not found"}
        
        return {
            "model": model,
            "name": self.model_names[model],
            "endpoint": self.llm_endpoints.get(model),
            "available": True
        }
    
    def test_model_connection(self, model: str) -> Dict[str, Any]:
        """Test connection to a specific model"""
        try:
            test_prompt = "Hello, this is a test message."
            result = self._call_llm_api(model, test_prompt, "test")
            
            return {
                "model": model,
                "connected": result.get("success", False),
                "response_time": result.get("response_time", 0),
                "error": result.get("error") if not result.get("success") else None
            }
        except Exception as e:
            return {
                "model": model,
                "connected": False,
                "error": str(e)
            }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        current_time = time.time()
        active_entries = 0
        expired_entries = 0
        
        for cache_key, cached_data in self.response_cache.items():
            if current_time - cached_data["timestamp"] < self.cache_ttl:
                active_entries += 1
            else:
                expired_entries += 1
        
        return {
            "total_entries": len(self.response_cache),
            "active_entries": active_entries,
            "expired_entries": expired_entries,
            "cache_ttl": self.cache_ttl
        }
    
    def clear_cache(self):
        """Clear the response cache"""
        self.response_cache.clear()
        logger.info("Response cache cleared")

# Global LLM router instance
llm_router = LLMRouter() 