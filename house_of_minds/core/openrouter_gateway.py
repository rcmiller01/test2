"""
OpenRouter Gateway - Flask API for cloud model access

This module provides a Flask-based gateway to OpenRouter API services,
allowing Core2 to make requests to cloud-based AI models through Core1.
"""

import os
import logging
import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

# Optional Flask imports (will be imported when needed)
try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

logger = logging.getLogger(__name__)

class OpenRouterGateway:
    """
    Gateway service for accessing OpenRouter cloud models.
    
    Provides both direct API access and Flask server functionality
    for handling requests from Core2.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the OpenRouter Gateway."""
        self.config = config
        self.api_key = config.get('api_key', os.getenv('OPENROUTER_API_KEY'))
        self.base_url = config.get('base_url', 'https://openrouter.ai/api/v1')
        self.default_model = config.get('default_model', 'anthropic/claude-3-sonnet')
        
        # Model mappings for easier reference
        self.model_mappings = {
            'claude': 'anthropic/claude-3-sonnet',
            'gpt4': 'openai/gpt-4-turbo',
            'gemini': 'google/gemini-pro',
            'claude_opus': 'anthropic/claude-3-opus',
            'gpt4_vision': 'openai/gpt-4-vision-preview'
        }
        
        # Rate limiting and retry configuration
        self.max_retries = config.get('max_retries', 3)
        self.retry_delay = config.get('retry_delay', 1.0)
        self.timeout = config.get('timeout', 30.0)
        
        # Flask app for server mode
        self.flask_app = None
        self.server_port = config.get('server_port', 5000)
        
        logger.info("🌐 OpenRouter Gateway initialized")
    
    async def generate_response(self, user_input: str, model_name: str = None, 
                              context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate response from OpenRouter model.
        
        Args:
            user_input: The user's request
            model_name: Specific model to use (optional)
            context: Previous conversation context
            
        Returns:
            Generated response string
        """
        try:
            # Resolve model name
            actual_model = self._resolve_model_name(model_name)
            
            # Prepare the request payload
            payload = self._prepare_request(user_input, actual_model, context)
            
            # Make the API request with retries
            response = await self._make_request_with_retries(payload)
            
            # Extract and return the response content
            content = self._extract_response_content(response)
            
            logger.info(f"✅ Generated response using {actual_model}")
            return content
            
        except Exception as e:
            logger.error(f"❌ OpenRouter request failed: {e}")
            raise Exception(f"OpenRouter generation failed: {str(e)}")
    
    def _resolve_model_name(self, model_name: Optional[str]) -> str:
        """Resolve friendly model name to actual OpenRouter model ID."""
        if not model_name:
            return self.default_model
        
        # Check if it's a mapped name
        if model_name in self.model_mappings:
            return self.model_mappings[model_name]
        
        # Return as-is if not mapped
        return model_name
    
    def _prepare_request(self, user_input: str, model: str, 
                        context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Prepare the request payload for OpenRouter API."""
        
        # Build conversation history
        messages = []
        
        # Add context if available
        if context and context.get('conversation_history'):
            history = context['conversation_history'][-5:]  # Last 5 exchanges
            for exchange in history:
                messages.extend([
                    {"role": "user", "content": exchange.get('user', '')},
                    {"role": "assistant", "content": exchange.get('ai', '')}
                ])
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": self.config.get('max_tokens', 1000),
            "temperature": self.config.get('temperature', 0.7),
            "top_p": self.config.get('top_p', 0.9),
            "frequency_penalty": self.config.get('frequency_penalty', 0.0),
            "presence_penalty": self.config.get('presence_penalty', 0.0)
        }
        
        return payload
    
    async def _make_request_with_retries(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request with retry logic."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/house-of-minds",
            "X-Title": "House of Minds AI System"
        }
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/chat/completions",
                        json=payload,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                    ) as response:
                        
                        if response.status == 200:
                            return await response.json()
                        else:
                            error_text = await response.text()
                            logger.warning(f"OpenRouter API error {response.status}: {error_text}")
                            
                            if response.status in [429, 500, 502, 503, 504]:
                                # Retry on rate limit or server errors
                                if attempt < self.max_retries - 1:
                                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                                    continue
                            
                            raise Exception(f"API request failed: {response.status} - {error_text}")
            
            except asyncio.TimeoutError:
                logger.warning(f"Request timeout (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                raise Exception("Request timed out after all retries")
            
            except Exception as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                    await asyncio.sleep(self.retry_delay)
                    continue
                raise
        
        raise Exception("All retry attempts failed")
    
    def _extract_response_content(self, response: Dict[str, Any]) -> str:
        """Extract content from OpenRouter API response."""
        try:
            choices = response.get('choices', [])
            if not choices:
                raise ValueError("No choices in response")
            
            message = choices[0].get('message', {})
            content = message.get('content', '')
            
            if not content:
                raise ValueError("No content in response message")
            
            return content.strip()
            
        except Exception as e:
            logger.error(f"Failed to extract response content: {e}")
            logger.debug(f"Response structure: {json.dumps(response, indent=2)}")
            raise ValueError(f"Invalid response format: {e}")
    
    async def health_check(self) -> bool:
        """Check if OpenRouter API is accessible."""
        try:
            # Simple test request
            test_payload = {
                "model": self.default_model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            
            await self._make_request_with_retries(test_payload)
            return True
            
        except Exception as e:
            logger.warning(f"OpenRouter health check failed: {e}")
            return False
    
    def create_flask_server(self) -> Flask:
        """Create Flask server for handling requests from Core2."""
        if not FLASK_AVAILABLE:
            raise ImportError("Flask not available. Install with: pip install flask flask-cors")
        
        app = Flask(__name__)
        CORS(app)  # Enable CORS for cross-origin requests
        
        @app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint."""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'service': 'openrouter_gateway'
            })
        
        @app.route('/generate', methods=['POST'])
        def generate():
            """Generate response endpoint."""
            try:
                data = request.get_json()
                user_input = data.get('input', '')
                model_name = data.get('model', self.default_model)
                context = data.get('context', {})
                
                if not user_input:
                    return jsonify({'error': 'No input provided'}), 400
                
                # Run async function in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    response = loop.run_until_complete(
                        self.generate_response(user_input, model_name, context)
                    )
                finally:
                    loop.close()
                
                return jsonify({
                    'response': response,
                    'model': model_name,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Flask generation error: {e}")
                return jsonify({'error': str(e)}), 500
        
        @app.route('/models', methods=['GET'])
        def list_models():
            """List available models."""
            return jsonify({
                'available_models': list(self.model_mappings.keys()),
                'model_mappings': self.model_mappings,
                'default_model': self.default_model
            })
        
        self.flask_app = app
        return app
    
    def run_server(self, host: str = '0.0.0.0', port: int = None, debug: bool = False):
        """Run the Flask server."""
        if not self.flask_app:
            self.create_flask_server()
        
        port = port or self.server_port
        logger.info(f"🌐 Starting OpenRouter Gateway server on {host}:{port}")
        
        self.flask_app.run(host=host, port=port, debug=debug)
    
    def get_available_models(self) -> Dict[str, str]:
        """Get mapping of available models."""
        return self.model_mappings.copy()
    
    def add_model_mapping(self, friendly_name: str, actual_model: str):
        """Add a new model mapping."""
        self.model_mappings[friendly_name] = actual_model
        logger.info(f"➕ Added model mapping: {friendly_name} -> {actual_model}")
    
    def remove_model_mapping(self, friendly_name: str):
        """Remove a model mapping."""
        if friendly_name in self.model_mappings:
            del self.model_mappings[friendly_name]
            logger.info(f"➖ Removed model mapping: {friendly_name}")
    
    async def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        actual_model = self._resolve_model_name(model_name)
        
        return {
            'friendly_name': model_name,
            'actual_model': actual_model,
            'available': True,  # TODO: Check actual availability
            'context_length': 'unknown',  # TODO: Get from model specs
            'cost_per_token': 'unknown'   # TODO: Get current pricing
        }
