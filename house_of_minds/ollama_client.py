#!/usr/bin/env python3
"""
Ollama Integration for Dolphin AI

This module provides robust integration with Ollama for local LLM inference,
including error handling, model management, and response streaming.

Author: Dolphin AI System
Date: July 30, 2025
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List, AsyncGenerator
import json
import aiohttp
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class OllamaConfig:
    """Ollama configuration"""
    host: str = "localhost"
    port: int = 11434
    base_url: str = ""
    default_model: str = "llama2"
    timeout: int = 120
    max_retries: int = 3
    stream: bool = True
    
    def __post_init__(self):
        if not self.base_url:
            self.base_url = f"http://{self.host}:{self.port}"

class OllamaError(Exception):
    """Base Ollama error"""
    pass

class OllamaConnectionError(OllamaError):
    """Ollama connection error"""
    pass

class OllamaModelError(OllamaError):
    """Ollama model error"""
    pass

class OllamaTimeoutError(OllamaError):
    """Ollama timeout error"""
    pass

class OllamaClient:
    """
    Advanced Ollama client with comprehensive error handling
    """
    
    def __init__(self, config: Optional[OllamaConfig] = None):
        self.config = config or OllamaConfig()
        self.session: Optional["aiohttp.ClientSession"] = None
        self.available_models: List[str] = []
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_tokens': 0,
            'avg_response_time': 0.0
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
        await self.refresh_models()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Ollama server health"""
        try:
            url = f"{self.config.base_url}/api/tags"
            
            if self.session is None:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                        if response.status == 200:
                            return {'status': 'healthy', 'timestamp': time.time()}
                        else:
                            return {'status': 'unhealthy', 'error': f'HTTP {response.status}'}
            else:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return {'status': 'healthy', 'timestamp': time.time()}
                    else:
                        return {'status': 'unhealthy', 'error': f'HTTP {response.status}'}
                        
        except Exception as e:
            logger.error("Ollama health check failed: %s", e)
            return {'status': 'unhealthy', 'error': str(e)}
    
    async def refresh_models(self) -> List[str]:
        """Refresh the list of available models"""
        try:
            url = f"{self.config.base_url}/api/tags"
            
            if self.session is None:
                raise OllamaConnectionError("Session not initialized")
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    self.available_models = [model['name'] for model in data.get('models', [])]
                    logger.info(f"Found {len(self.available_models)} available models")
                    return self.available_models
                else:
                    raise OllamaError(f"Failed to get models: HTTP {response.status}")
                    
        except Exception as e:
            logger.error("Failed to refresh models: %s", e)
            raise OllamaError(f"Failed to refresh models: {e}")
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        stream: Optional[bool] = None,
        options: Optional[Dict[str, Any]] = None,
        system: Optional[str] = None,
        template: Optional[str] = None,
        context: Optional[List[int]] = None,
        raw: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a response using Ollama
        
        Args:
            prompt: The input prompt
            model: Model to use (default: config.default_model)
            stream: Whether to stream response (default: config.stream)
            options: Additional options for generation
            system: System message
            template: Template to use
            context: Context from previous generation
            raw: Whether to return raw response
        
        Returns:
            Dictionary with generated response and metadata
        """
        start_time = time.time()
        self.stats['total_requests'] += 1
        
        try:
            # Validate model
            model = model or self.config.default_model
            if self.available_models and model not in self.available_models:
                logger.warning(f"Model '{model}' not in available models: {self.available_models}")
            
            # Prepare request
            stream = stream if stream is not None else self.config.stream
            
            request_data = {
                'model': model,
                'prompt': prompt,
                'stream': stream
            }
            
            # Add optional parameters
            if options:
                request_data['options'] = options
            if system:
                request_data['system'] = system
            if template:
                request_data['template'] = template
            if context:
                request_data['context'] = context
            if raw:
                request_data['raw'] = raw
            
            # Make request
            url = f"{self.config.base_url}/api/generate"
            
            if self.session is None:
                raise OllamaConnectionError("Session not initialized")
            
            logger.info(f"Generating with Ollama: model={model}, stream={stream}")
            
            if stream:
                return await self._generate_stream(url, request_data, start_time)
            else:
                return await self._generate_single(url, request_data, start_time)
                
        except Exception as e:
            self.stats['failed_requests'] += 1
            logger.error(f"Ollama generation failed: {e}")
            raise
    
    async def _generate_single(self, url: str, request_data: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        """Generate single response"""
        if self.session is None:
            raise OllamaConnectionError("Session not initialized")
            
        try:
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Calculate metrics
                    response_time = (time.time() - start_time) * 1000
                    self.stats['successful_requests'] += 1
                    self._update_avg_response_time(response_time)
                    
                    # Extract tokens if available
                    if 'eval_count' in data:
                        self.stats['total_tokens'] += data['eval_count']
                    
                    logger.info(f"Ollama generation completed in {response_time:.2f}ms")
                    
                    return {
                        'response': data.get('response', ''),
                        'model': data.get('model', request_data['model']),
                        'created_at': data.get('created_at'),
                        'done': data.get('done', True),
                        'context': data.get('context', []),
                        'total_duration': data.get('total_duration'),
                        'load_duration': data.get('load_duration'),
                        'prompt_eval_count': data.get('prompt_eval_count'),
                        'prompt_eval_duration': data.get('prompt_eval_duration'),
                        'eval_count': data.get('eval_count'),
                        'eval_duration': data.get('eval_duration'),
                        'response_time_ms': response_time
                    }
                else:
                    error_text = await response.text()
                    raise OllamaError(f"HTTP {response.status}: {error_text}")
                    
        except asyncio.TimeoutError:
            raise OllamaTimeoutError(f"Request timed out after {self.config.timeout}s")
        except aiohttp.ClientConnectionError as e:
            raise OllamaConnectionError(f"Connection error: {e}")
    
    async def _generate_stream(self, url: str, request_data: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        """Generate streaming response"""
        if self.session is None:
            raise OllamaConnectionError("Session not initialized")
            
        try:
            full_response = ""
            last_context = []
            total_tokens = 0
            
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    async for line in response.content:
                        if line:
                            try:
                                chunk = json.loads(line.decode('utf-8'))
                                if 'response' in chunk:
                                    full_response += chunk['response']
                                if 'context' in chunk:
                                    last_context = chunk['context']
                                if 'eval_count' in chunk:
                                    total_tokens = chunk['eval_count']
                                    
                                # Check if generation is done
                                if chunk.get('done', False):
                                    break
                                    
                            except json.JSONDecodeError as e:
                                logger.warning(f"Failed to decode chunk: {e}")
                                continue
                    
                    # Calculate metrics
                    response_time = (time.time() - start_time) * 1000
                    self.stats['successful_requests'] += 1
                    self.stats['total_tokens'] += total_tokens
                    self._update_avg_response_time(response_time)
                    
                    logger.info(f"Ollama streaming completed in {response_time:.2f}ms")
                    
                    return {
                        'response': full_response,
                        'model': request_data['model'],
                        'done': True,
                        'context': last_context,
                        'eval_count': total_tokens,
                        'response_time_ms': response_time,
                        'streaming': True
                    }
                else:
                    error_text = await response.text()
                    raise OllamaError(f"HTTP {response.status}: {error_text}")
                    
        except asyncio.TimeoutError:
            raise OllamaTimeoutError(f"Streaming request timed out after {self.config.timeout}s")
        except aiohttp.ClientConnectionError as e:
            raise OllamaConnectionError(f"Connection error: {e}")
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        stream: Optional[bool] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Chat with Ollama using the chat API
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use
            stream: Whether to stream
            options: Additional options
        
        Returns:
            Chat response dictionary
        """
        start_time = time.time()
        self.stats['total_requests'] += 1
        
        try:
            model = model or self.config.default_model
            stream = stream if stream is not None else self.config.stream
            
            request_data = {
                'model': model,
                'messages': messages,
                'stream': stream
            }
            
            if options:
                request_data['options'] = options
            
            url = f"{self.config.base_url}/api/chat"
            
            if self.session is None:
                raise OllamaConnectionError("Session not initialized")
            
            logger.info(f"Chat with Ollama: model={model}, messages={len(messages)}")
            
            async with self.session.post(url, json=request_data) as response:
                if response.status == 200:
                    if stream:
                        # Handle streaming chat
                        full_content = ""
                        async for line in response.content:
                            if line:
                                try:
                                    chunk = json.loads(line.decode('utf-8'))
                                    if 'message' in chunk and 'content' in chunk['message']:
                                        full_content += chunk['message']['content']
                                    if chunk.get('done', False):
                                        break
                                except json.JSONDecodeError:
                                    continue
                        
                        response_time = (time.time() - start_time) * 1000
                        self.stats['successful_requests'] += 1
                        self._update_avg_response_time(response_time)
                        
                        return {
                            'message': {'role': 'assistant', 'content': full_content},
                            'model': model,
                            'done': True,
                            'response_time_ms': response_time
                        }
                    else:
                        # Handle single chat response
                        data = await response.json()
                        response_time = (time.time() - start_time) * 1000
                        self.stats['successful_requests'] += 1
                        self._update_avg_response_time(response_time)
                        
                        return {
                            **data,
                            'response_time_ms': response_time
                        }
                else:
                    error_text = await response.text()
                    raise OllamaError(f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.stats['failed_requests'] += 1
            logger.error(f"Ollama chat failed: {e}")
            raise
    
    def _update_avg_response_time(self, new_time: float):
        """Update average response time"""
        if self.stats['avg_response_time'] == 0:
            self.stats['avg_response_time'] = new_time
        else:
            self.stats['avg_response_time'] = (0.9 * self.stats['avg_response_time']) + (0.1 * new_time)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics"""
        success_rate = 0.0
        if self.stats['total_requests'] > 0:
            success_rate = (self.stats['successful_requests'] / self.stats['total_requests']) * 100
        
        return {
            **self.stats,
            'success_rate': success_rate,
            'available_models': self.available_models,
            'config': {
                'base_url': self.config.base_url,
                'default_model': self.config.default_model,
                'timeout': self.config.timeout
            }
        }

# Global Ollama client instance
_global_client: Optional[OllamaClient] = None

async def get_ollama_client() -> OllamaClient:
    """Get or create the global Ollama client"""
    global _global_client
    if _global_client is None:
        _global_client = OllamaClient()
    return _global_client

async def generate_response(prompt: str, model: Optional[str] = None) -> str:
    """
    Simple function to generate a response using Ollama
    
    Args:
        prompt: Input prompt
        model: Model to use (optional)
    
    Returns:
        Generated response string
    """
    try:
        async with OllamaClient() as client:
            result = await client.generate(prompt, model=model, stream=False)
            return result.get('response', '')
    except Exception as e:
        logger.error(f"Failed to generate response: {e}")
        return f"Error: {e}"

async def chat_with_ollama(messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
    """
    Simple function to chat with Ollama
    
    Args:
        messages: Chat messages
        model: Model to use (optional)
    
    Returns:
        Chat response string
    """
    try:
        async with OllamaClient() as client:
            result = await client.chat(messages, model=model, stream=False)
            message = result.get('message', {})
            return message.get('content', '')
    except Exception as e:
        logger.error(f"Failed to chat with Ollama: {e}")
        return f"Error: {e}"
