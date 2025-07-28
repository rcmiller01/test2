"""
Model Router - Core routing logic for House of Minds

This module handles the delegation of tasks to appropriate AI models
and services based on task type, availability, and fallback logic.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from models.dolphin_interface import DolphinInterface
from models.kimi_interface import KimiInterface
from core.openrouter_gateway import OpenRouterGateway
from core.n8n_client import N8NClient
from memory.memory_handler import MemoryHandler

logger = logging.getLogger(__name__)

class ModelRouter:
    """
    Central routing system for delegating tasks to appropriate AI models and services.
    
    Handles fallback logic, load balancing, and ensures requests are routed to the
    most suitable handler based on task type and system availability.
    """
    
    def __init__(self, config):
        """Initialize the model router with all available handlers."""
        self.config = config
        
        # Initialize all interfaces
        self.dolphin = DolphinInterface(config.get_model_config('dolphin'))
        self.kimi = KimiInterface(config.get_model_config('kimi'))
        self.openrouter = OpenRouterGateway(config.get_openrouter_config())
        self.n8n = N8NClient(config.get_n8n_config())
        self.memory = MemoryHandler(config.get_memory_config())
        
        # Routing configuration
        self.routing_rules = {
            'conversation': ['dolphin', 'kimi'],
            'planning': ['kimi', 'openrouter_claude'],
            'code': ['openrouter_gpt4', 'openrouter_claude', 'kimi'],
            'utility': ['n8n', 'dolphin'],
            'memory': ['memory', 'kimi'],
            'analysis': ['kimi', 'openrouter_claude'],
            'creative': ['openrouter_claude', 'openrouter_gpt4', 'dolphin']
        }
        
        # Track handler availability and performance
        self.handler_status = {}
        self.last_health_check = None
        
        logger.info("🔀 Model Router initialized with all handlers")
    
    async def route_request(self, user_input: str, task_type: str, 
                          context: Optional[Dict[str, Any]] = None,
                          intent_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Route a request to the most appropriate handler.
        
        Args:
            user_input: The user's request
            task_type: Classified task type
            context: Previous conversation context
            intent_metadata: Additional metadata from intent classification
            
        Returns:
            Dict containing the response and handler information
        """
        try:
            # Get ordered list of handlers for this task type
            handlers = self.routing_rules.get(task_type, ['dolphin'])
            
            logger.info(f"🔀 Routing {task_type} task to handlers: {handlers}")
            
            # Try each handler in order until one succeeds
            for handler_name in handlers:
                try:
                    result = await self._execute_with_handler(
                        handler_name, user_input, task_type, context, intent_metadata
                    )
                    
                    if result and result.get('content'):
                        logger.info(f"✅ Successfully handled by {handler_name}")
                        return {
                            'content': result['content'],
                            'handler': handler_name,
                            'metadata': result.get('metadata', {}),
                            'execution_time': result.get('execution_time', 0),
                            'fallback_used': len(handlers) > 1 and handler_name != handlers[0]
                        }
                
                except Exception as e:
                    logger.warning(f"⚠️ Handler {handler_name} failed: {e}")
                    continue
            
            # If all handlers fail, use Dolphin as final fallback
            logger.warning(f"🚨 All handlers failed for {task_type}, using Dolphin fallback")
            result = await self._fallback_response(user_input, task_type, context)
            
            return {
                'content': result,
                'handler': 'dolphin_fallback',
                'metadata': {'fallback_reason': 'all_handlers_failed'},
                'execution_time': 0,
                'fallback_used': True
            }
            
        except Exception as e:
            logger.error(f"❌ Critical routing error: {e}")
            return {
                'content': "I'm experiencing technical difficulties. Please try again.",
                'handler': 'error_fallback',
                'metadata': {'error': str(e)},
                'execution_time': 0,
                'fallback_used': True
            }
    
    async def _execute_with_handler(self, handler_name: str, user_input: str, 
                                  task_type: str, context: Optional[Dict[str, Any]] = None,
                                  intent_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute request with a specific handler."""
        start_time = datetime.now()
        
        try:
            if handler_name == 'dolphin':
                response = await self.dolphin.generate_response(user_input, context)
                
            elif handler_name == 'kimi':
                response = await self.kimi.generate_response(user_input, context, task_type)
                
            elif handler_name.startswith('openrouter_'):
                model_name = handler_name.replace('openrouter_', '')
                response = await self.openrouter.generate_response(user_input, model_name, context)
                
            elif handler_name == 'n8n':
                response = await self.n8n.execute_workflow(user_input, task_type, context)
                
            elif handler_name == 'memory':
                response = await self.memory.query_memory(user_input, context)
                
            else:
                raise ValueError(f"Unknown handler: {handler_name}")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'content': response,
                'metadata': {
                    'handler': handler_name,
                    'task_type': task_type,
                    'timestamp': datetime.now().isoformat()
                },
                'execution_time': execution_time
            }
            
        except Exception as e:
            logger.error(f"Handler {handler_name} execution failed: {e}")
            raise
    
    async def _fallback_response(self, user_input: str, task_type: str, 
                               context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a fallback response when all handlers fail."""
        try:
            # Try simple Dolphin response as last resort
            return await self.dolphin.generate_simple_response(user_input)
        except Exception:
            # Absolute fallback
            return f"I understand you're asking about {task_type}-related matters, but I'm having technical difficulties right now. Could you please try again in a moment?"
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get the current status of all handlers and the routing system."""
        status = {
            'timestamp': datetime.now().isoformat(),
            'handlers': {},
            'routing_rules': self.routing_rules,
            'total_handlers': 0,
            'available_handlers': 0
        }
        
        # Check each handler
        for handler_name in ['dolphin', 'kimi', 'openrouter', 'n8n', 'memory']:
            try:
                handler_status = await self._check_handler_health(handler_name)
                status['handlers'][handler_name] = handler_status
                status['total_handlers'] += 1
                if handler_status['available']:
                    status['available_handlers'] += 1
            except Exception as e:
                status['handlers'][handler_name] = {
                    'available': False,
                    'error': str(e),
                    'last_check': datetime.now().isoformat()
                }
        
        status['system_health'] = status['available_handlers'] / status['total_handlers']
        
        return status
    
    async def _check_handler_health(self, handler_name: str) -> Dict[str, Any]:
        """Check the health status of a specific handler."""
        try:
            if handler_name == 'dolphin':
                available = await self.dolphin.health_check()
            elif handler_name == 'kimi':
                available = await self.kimi.health_check()
            elif handler_name == 'openrouter':
                available = await self.openrouter.health_check()
            elif handler_name == 'n8n':
                available = await self.n8n.health_check()
            elif handler_name == 'memory':
                available = await self.memory.health_check()
            else:
                available = False
            
            return {
                'available': available,
                'last_check': datetime.now().isoformat(),
                'response_time': 0  # TODO: Implement actual response time measurement
            }
            
        except Exception as e:
            return {
                'available': False,
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
    
    async def update_routing_rules(self, new_rules: Dict[str, List[str]]):
        """Update the routing rules dynamically."""
        self.routing_rules.update(new_rules)
        logger.info(f"🔄 Routing rules updated: {json.dumps(new_rules, indent=2)}")
    
    def get_routing_rules(self) -> Dict[str, List[str]]:
        """Get the current routing rules."""
        return self.routing_rules.copy()
    
    async def add_handler(self, handler_name: str, task_types: List[str]):
        """Add a new handler to the routing system."""
        for task_type in task_types:
            if task_type not in self.routing_rules:
                self.routing_rules[task_type] = []
            if handler_name not in self.routing_rules[task_type]:
                self.routing_rules[task_type].append(handler_name)
        
        logger.info(f"➕ Added handler {handler_name} for task types: {task_types}")
    
    async def remove_handler(self, handler_name: str):
        """Remove a handler from all routing rules."""
        for task_type, handlers in self.routing_rules.items():
            if handler_name in handlers:
                handlers.remove(handler_name)
        
        logger.info(f"➖ Removed handler {handler_name} from all routing rules")
