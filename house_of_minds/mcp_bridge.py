#!/usr/bin/env python3
"""
MCP Bridge - Dolphin AI to MCP Server Integration

This module provides a robust bridge between Dolphin AI and the MCP server,
handling task routing, error handling, and response processing.

Author: Dolphin AI System
Date: July 30, 2025
"""

import os
import asyncio
import aiohttp
import logging
import time
from typing import Dict, Any, Optional, List
import json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class MCPConfig:
    """MCP configuration with environment variable support"""
    def __init__(self):
        self.host = os.getenv("MCP_HOST", "localhost")
        self.port = int(os.getenv("MCP_PORT", "8000"))
        self.base_url = os.getenv("MCP_BASE_URL", f"http://{self.host}:{self.port}")
        self.timeout = int(os.getenv("MCP_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("MCP_MAX_RETRIES", "3"))
        self.retry_delay = float(os.getenv("MCP_RETRY_DELAY", "1.0"))

class MCPError(Exception):
    """Custom exception for MCP-related errors"""
    pass

class MCPConnectionError(MCPError):
    """MCP connection-related errors"""
    pass

class MCPTimeoutError(MCPError):
    """MCP timeout-related errors"""
    pass

class MCPValidationError(MCPError):
    """MCP request validation errors"""
    pass

class MCPBridge:
    """
    Advanced MCP bridge with comprehensive error handling and monitoring
    """
    
    def __init__(self, config: Optional[MCPConfig] = None):
        self.config = config or MCPConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'avg_response_time': 0.0,
            'last_error': None,
            'last_success': None
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def _validate_task_request(self, task_request: Dict[str, Any]) -> None:
        """Validate task request structure"""
        required_fields = ['intent_type', 'payload', 'source']
        
        for field in required_fields:
            if field not in task_request:
                raise MCPValidationError(f"Missing required field: {field}")
        
        # Validate intent_type
        if not isinstance(task_request['intent_type'], str) or not task_request['intent_type'].strip():
            raise MCPValidationError("intent_type must be a non-empty string")
        
        # Validate payload
        if not isinstance(task_request['payload'], dict):
            raise MCPValidationError("payload must be a dictionary")
        
        # Validate source
        if not isinstance(task_request['source'], str):
            raise MCPValidationError("source must be a string")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError))
    )
    async def _make_request(self, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request to MCP server with retry logic"""
        if self.session is None:
            raise MCPConnectionError("Session not initialized. Use async context manager.")
        
        try:
            async with self.session.post(url, json=data) as response:
                # Check if the response is successful
                if response.status == 200:
                    return await response.json()
                elif response.status == 400:
                    error_data = await response.json()
                    raise MCPValidationError(f"MCP validation error: {error_data.get('detail', 'Unknown error')}")
                elif response.status == 404:
                    raise MCPError(f"MCP endpoint not found: {url}")
                elif response.status == 500:
                    raise MCPError("MCP server internal error")
                else:
                    response.raise_for_status()
                    return {"error": f"Unexpected status code: {response.status}"}
                    
        except asyncio.TimeoutError:
            raise MCPTimeoutError(f"Request to {url} timed out after {self.config.timeout}s")
        except aiohttp.ClientConnectionError as e:
            raise MCPConnectionError(f"Failed to connect to MCP server: {e}")
        except aiohttp.ClientError as e:
            raise MCPError(f"HTTP client error: {e}")
    
    async def route_task(self, task_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route a task to the MCP server with comprehensive error handling
        
        Args:
            task_request: Dictionary containing:
                - intent_type: Type of task/intent to route
                - payload: Task-specific data
                - source: Source system (usually "dolphin")
                - request_id: Optional request tracking ID
                - priority: Optional priority level
        
        Returns:
            Dictionary containing the MCP response or error information
        """
        start_time = time.time()
        self.stats['total_requests'] += 1
        
        try:
            # Validate request
            self._validate_task_request(task_request)
            
            # Add metadata
            if 'request_id' not in task_request:
                task_request['request_id'] = f"dolphin_{int(time.time() * 1000)}"
            
            if 'priority' not in task_request:
                task_request['priority'] = 5  # Default priority
            
            # Log the request
            logger.info(
                "Routing task to MCP: intent=%s, source=%s, request_id=%s",
                task_request.get('intent_type'),
                task_request.get('source'),
                task_request.get('request_id')
            )
            
            # Make the request
            url = f"{self.config.base_url.rstrip('/')}/api/mcp/route-task"
            response_data = await self._make_request(url, task_request)
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            
            # Update statistics
            self.stats['successful_requests'] += 1
            self.stats['last_success'] = time.time()
            self._update_avg_response_time(response_time)
            
            # Log success
            logger.info(
                "MCP task completed: intent=%s, request_id=%s, time=%.2fms, success=%s",
                task_request.get('intent_type'),
                task_request.get('request_id'),
                response_time,
                response_data.get('success', False)
            )
            
            return response_data
            
        except MCPValidationError as e:
            self.stats['failed_requests'] += 1
            self.stats['last_error'] = str(e)
            logger.error("MCP validation error: %s", e)
            return {
                'success': False,
                'error': f"Validation error: {e}",
                'error_type': 'validation',
                'request_id': task_request.get('request_id'),
                'timestamp': time.time()
            }
            
        except MCPConnectionError as e:
            self.stats['failed_requests'] += 1
            self.stats['last_error'] = str(e)
            logger.error("MCP connection error: %s", e)
            return {
                'success': False,
                'error': f"Connection error: {e}",
                'error_type': 'connection',
                'request_id': task_request.get('request_id'),
                'timestamp': time.time()
            }
            
        except MCPTimeoutError as e:
            self.stats['failed_requests'] += 1
            self.stats['last_error'] = str(e)
            logger.error("MCP timeout error: %s", e)
            return {
                'success': False,
                'error': f"Timeout error: {e}",
                'error_type': 'timeout',
                'request_id': task_request.get('request_id'),
                'timestamp': time.time()
            }
            
        except MCPError as e:
            self.stats['failed_requests'] += 1
            self.stats['last_error'] = str(e)
            logger.error("MCP error: %s", e)
            return {
                'success': False,
                'error': f"MCP error: {e}",
                'error_type': 'mcp',
                'request_id': task_request.get('request_id'),
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            self.stats['last_error'] = str(e)
            logger.error("Unexpected error in MCP routing: %s", e, exc_info=True)
            return {
                'success': False,
                'error': f"Unexpected error: {e}",
                'error_type': 'unexpected',
                'request_id': task_request.get('request_id'),
                'timestamp': time.time()
            }
    
    def _update_avg_response_time(self, new_time: float):
        """Update average response time using exponential moving average"""
        if self.stats['avg_response_time'] == 0:
            self.stats['avg_response_time'] = new_time
        else:
            # Use 0.1 as smoothing factor
            self.stats['avg_response_time'] = (0.9 * self.stats['avg_response_time']) + (0.1 * new_time)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check MCP server health"""
        try:
            url = f"{self.config.base_url.rstrip('/')}/api/mcp/health"
            
            if self.session is None:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            return {'status': 'unhealthy', 'error': f'HTTP {response.status}'}
            else:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {'status': 'unhealthy', 'error': f'HTTP {response.status}'}
                        
        except Exception as e:
            logger.error("MCP health check failed: %s", e)
            return {'status': 'unhealthy', 'error': str(e)}
    
    async def get_agent_capabilities(self) -> Dict[str, Any]:
        """Get available agent capabilities from MCP server"""
        try:
            url = f"{self.config.base_url.rstrip('/')}/api/mcp/agents/capabilities"
            
            if self.session is None:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            return {'error': f'HTTP {response.status}'}
            else:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {'error': f'HTTP {response.status}'}
                        
        except Exception as e:
            logger.error("Failed to get agent capabilities: %s", e)
            return {'error': str(e)}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bridge statistics"""
        success_rate = 0.0
        if self.stats['total_requests'] > 0:
            success_rate = (self.stats['successful_requests'] / self.stats['total_requests']) * 100
        
        return {
            **self.stats,
            'success_rate': success_rate,
            'config': {
                'base_url': self.config.base_url,
                'timeout': self.config.timeout,
                'max_retries': self.config.max_retries
            }
        }

# Global MCP bridge instance
_global_bridge: Optional[MCPBridge] = None

async def get_mcp_bridge() -> MCPBridge:
    """Get or create the global MCP bridge instance"""
    global _global_bridge
    if _global_bridge is None:
        _global_bridge = MCPBridge()
    return _global_bridge

async def route_to_mcp(task_request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function for routing tasks to MCP server
    
    This function maintains backward compatibility while providing
    the enhanced error handling and monitoring capabilities.
    """
    async with MCPBridge() as bridge:
        return await bridge.route_task(task_request)

# Backward compatibility function
async def route_to_mcp_simple(prompt: str, intent_type: str = "ai_chat") -> str:
    """
    Simple MCP routing function for basic prompts
    
    Args:
        prompt: The prompt/message to send
        intent_type: The type of intent (default: "ai_chat")
    
    Returns:
        String response from MCP or error message
    """
    task_request = {
        "intent_type": intent_type,
        "payload": {"message": prompt},
        "source": "dolphin",
        "request_id": f"simple_{int(time.time() * 1000)}"
    }
    
    response = await route_to_mcp(task_request)
    
    if response.get('success'):
        result = response.get('result', {})
        return result.get('message', str(result))
    else:
        error = response.get('error', 'Unknown error')
        logger.error(f"MCP routing failed: {error}")
        return f"Error: {error}"
