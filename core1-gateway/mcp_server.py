#!/usr/bin/env python3
"""
MCP Server - Master Control Program Core Orchestration Layer

This server serves as the central routing and orchestration hub for the MCP system.
It receives structured task requests from Dolphin AI or other modules, classifies
tasks by intent, routes them to appropriate agents (n8n, OpenRouter, file system, etc.),
and returns responses back to the requesting system.

Author: Dolphin AI System
Date: July 30, 2025
Tag: #ref-mcp-integration
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from agent_registry import registry_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# DYNAMIC AGENT REGISTRY - Loaded from agents/registry.json
# ============================================================================

# The agent registry is now managed by the AgentRegistryManager
# and loaded dynamically from agents/registry.json
# This allows hot-swappable agent definitions without server restarts

# ============================================================================
# PYDANTIC MODELS - Request/Response schemas
# ============================================================================

class TaskRequest(BaseModel):
    """Schema for incoming task requests"""
    intent_type: str = Field(..., description="Type of task/intent to route")
    payload: Dict[str, Any] = Field(..., description="Task-specific data payload")
    source: str = Field(default="dolphin", description="Source system making the request")
    request_id: Optional[str] = Field(None, description="Optional request tracking ID")
    priority: int = Field(default=5, ge=1, le=10, description="Task priority (1=highest, 10=lowest)")

class TaskResponse(BaseModel):
    """Schema for task execution responses"""
    success: bool
    request_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    agent_type: Optional[str] = None
    execution_time_ms: Optional[int] = None
    timestamp: str

class AgentStatus(BaseModel):
    """Schema for agent health status"""
    agent_name: str
    type: str
    status: str  # "online", "offline", "error"
    response_time_ms: Optional[int] = None
    last_check: str
    error_message: Optional[str] = None

class SystemStatus(BaseModel):
    """Schema for overall system status"""
    server_status: str
    uptime_seconds: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    agents: List[AgentStatus]
    timestamp: str

# ============================================================================
# GLOBAL STATE - Server metrics and tracking
# ============================================================================

class ServerMetrics:
    def __init__(self):
        self.start_time = time.time()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.agent_health = {}

metrics = ServerMetrics()

# ============================================================================
# UTILITY FUNCTIONS - Agent communication and health checking
# ============================================================================

async def ping_agent(agent_name: str, agent_config: Dict[str, Any]) -> AgentStatus:
    """
    Ping an individual agent to check its health status
    
    Args:
        agent_name: Name of the agent to ping
        agent_config: Configuration dictionary for the agent
        
    Returns:
        AgentStatus object with health information
    """
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            if agent_config["type"] == "n8n":
                # For n8n, try to ping the base URL
                base_url = agent_config["webhook"].rsplit("/webhook", 1)[0]
                response = await client.get(f"{base_url}/healthz")
                
            elif agent_config["type"] == "openrouter":
                # For OpenRouter, try a simple ping to the base URL
                base_url = agent_config["url"].rsplit("/api", 1)[0]
                response = await client.get(f"{base_url}/health")
                
            elif agent_config["type"] == "local":
                # Local handlers are always considered online
                response_time = int((time.time() - start_time) * 1000)
                return AgentStatus(
                    agent_name=agent_name,
                    type=agent_config["type"],
                    status="online",
                    response_time_ms=response_time,
                    last_check=datetime.now().isoformat()
                )
            
            response_time = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                return AgentStatus(
                    agent_name=agent_name,
                    type=agent_config["type"],
                    status="online",
                    response_time_ms=response_time,
                    last_check=datetime.now().isoformat()
                )
            else:
                return AgentStatus(
                    agent_name=agent_name,
                    type=agent_config["type"],
                    status="error",
                    response_time_ms=response_time,
                    last_check=datetime.now().isoformat(),
                    error_message=f"HTTP {response.status_code}"
                )
                
    except Exception as e:
        response_time = int((time.time() - start_time) * 1000)
        return AgentStatus(
            agent_name=agent_name,
            type=agent_config["type"],
            status="offline",
            response_time_ms=response_time,
            last_check=datetime.now().isoformat(),
            error_message=str(e)
        )

async def ping_all_agents() -> List[AgentStatus]:
    """
    Ping all registered agents concurrently to check their health
    
    Returns:
        List of AgentStatus objects for all agents
    """
    enabled_agents = registry_manager.get_enabled_agents()
    tasks = []
    
    for agent_name, agent_config in enabled_agents.items():
        task = ping_agent(agent_name, agent_config)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    agent_statuses = []
    agent_names = list(enabled_agents.keys())
    agent_configs = list(enabled_agents.values())
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            agent_name = agent_names[i]
            agent_config = agent_configs[i]
            agent_statuses.append(AgentStatus(
                agent_name=agent_name,
                type=agent_config["type"],
                status="error",
                last_check=datetime.now().isoformat(),
                error_message=str(result)
            ))
        else:
            agent_statuses.append(result)
    
    return agent_statuses

async def dispatch_to_n8n(webhook_url: str, payload: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
    """
    Dispatch a task to an n8n webhook endpoint
    
    Args:
        webhook_url: The n8n webhook URL to call
        payload: Data to send to the webhook
        timeout: Request timeout in seconds
        
    Returns:
        Response data from n8n
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(webhook_url, json=payload)
        response.raise_for_status()
        
        if response.headers.get("content-type", "").startswith("application/json"):
            return response.json()
        else:
            return {"message": response.text, "status_code": response.status_code}

async def dispatch_to_openrouter(api_url: str, payload: Dict[str, Any], timeout: int = 60) -> Dict[str, Any]:
    """
    Dispatch a task to an OpenRouter API endpoint
    
    Args:
        api_url: The OpenRouter API URL to call
        payload: Data to send to the API
        timeout: Request timeout in seconds
        
    Returns:
        Response data from OpenRouter
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(api_url, json=payload)
        response.raise_for_status()
        return response.json()

async def handle_local_task(handler: str, intent_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle local tasks that don't require external API calls
    
    Args:
        handler: Type of local handler (file_system, system_monitor, etc.)
        intent_type: Specific intent type
        payload: Task data
        
    Returns:
        Result of the local operation
    """
    if handler == "file_system":
        return await handle_file_system_task(intent_type, payload)
    elif handler == "system_monitor":
        return await handle_system_monitor_task(intent_type, payload)
    else:
        raise ValueError(f"Unknown local handler: {handler}")

async def handle_file_system_task(intent_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle file system related tasks"""
    # TODO: Implement file system operations
    # This is a stub for future implementation
    return {
        "message": f"File system task '{intent_type}' received",
        "payload": payload,
        "note": "File system operations not yet implemented"
    }

async def handle_system_monitor_task(intent_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle system monitoring tasks"""
    # TODO: Implement system monitoring operations
    # This is a stub for future implementation
    return {
        "message": f"System monitor task '{intent_type}' received",
        "payload": payload,
        "note": "System monitoring operations not yet implemented"
    }

# ============================================================================
# FASTAPI APPLICATION SETUP
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("MCP Server starting up...")
    
    # Initialize the agent registry manager
    try:
        await registry_manager.initialize(enable_file_watching=True)
        logger.info("Agent registry manager initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent registry manager: {e}")
        raise
    
    yield
    
    logger.info("MCP Server shutting down...")
    
    # Shutdown the agent registry manager
    try:
        await registry_manager.shutdown()
        logger.info("Agent registry manager shutdown successfully")
    except Exception as e:
        logger.error(f"Error shutting down agent registry manager: {e}")

app = FastAPI(
    title="MCP Server - Master Control Program",
    description="Core orchestration layer for routing tasks to various agents",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for development (TODO: Restrict origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.post("/api/mcp/route-task", response_model=TaskResponse)
async def route_task(task: TaskRequest, background_tasks: BackgroundTasks) -> TaskResponse:
    """
    Route a task to the appropriate agent based on intent type
    
    This is the main endpoint that receives structured task requests,
    classifies them by intent, and dispatches to the appropriate agent.
    """
    start_time = time.time()
    metrics.total_requests += 1
    
    logger.info(f"Received task request: intent={task.intent_type}, source={task.source}, id={task.request_id}")
    
    try:
        # Validate intent type
        enabled_agents = registry_manager.get_enabled_agents()
        if task.intent_type not in enabled_agents:
            metrics.failed_requests += 1
            raise HTTPException(
                status_code=400,
                detail=f"Unknown intent type: {task.intent_type}. Available intents: {list(enabled_agents.keys())}"
            )
        
        agent_config = enabled_agents[task.intent_type]
        agent_type = agent_config["type"]
        timeout = agent_config.get("timeout", 30)
        
        # Dispatch to appropriate agent type
        result = None
        if agent_type == "n8n":
            result = await dispatch_to_n8n(agent_config["webhook"], task.payload, timeout)
        elif agent_type == "openrouter":
            result = await dispatch_to_openrouter(agent_config["url"], task.payload, timeout)
        elif agent_type == "local":
            result = await handle_local_task(agent_config["handler"], task.intent_type, task.payload)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        execution_time = int((time.time() - start_time) * 1000)
        metrics.successful_requests += 1
        
        response = TaskResponse(
            success=True,
            request_id=task.request_id,
            result=result,
            agent_type=agent_type,
            execution_time_ms=execution_time,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"Task completed successfully: intent={task.intent_type}, time={execution_time}ms")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        metrics.failed_requests += 1
        
        error_msg = str(e)
        logger.error(f"Task failed: intent={task.intent_type}, error={error_msg}, time={execution_time}ms")
        
        return TaskResponse(
            success=False,
            request_id=task.request_id,
            error=error_msg,
            agent_type=agent_config.get("type") if 'agent_config' in locals() else None,
            execution_time_ms=execution_time,
            timestamp=datetime.now().isoformat()
        )

@app.get("/api/mcp/status", response_model=SystemStatus)
async def get_system_status() -> SystemStatus:
    """
    Get the overall system status including agent health
    
    Returns comprehensive status information about the MCP server
    and all registered agents.
    """
    logger.info("System status requested")
    
    # Get agent health status
    agent_statuses = await ping_all_agents()
    
    uptime = int(time.time() - metrics.start_time)
    
    return SystemStatus(
        server_status="online",
        uptime_seconds=uptime,
        total_requests=metrics.total_requests,
        successful_requests=metrics.successful_requests,
        failed_requests=metrics.failed_requests,
        agents=agent_statuses,
        timestamp=datetime.now().isoformat()
    )

@app.get("/api/mcp/agents")
async def get_agent_registry() -> Dict[str, Any]:
    """
    Get the current agent registry configuration
    
    Returns information about all registered agents and their configurations.
    """
    enabled_agents = registry_manager.get_enabled_agents()
    all_agents = registry_manager.agents
    
    return {
        "total_agents": len(all_agents),
        "enabled_agents": len(enabled_agents),
        "registry_info": registry_manager.get_registry_info(),
        "agents": {
            name: {
                "type": config["type"],
                "enabled": config.get("enabled", True),
                "description": config.get("description", "No description available"),
                "timeout": config.get("timeout", 30),
                "capabilities": config.get("capabilities", []),
                "priority": config.get("priority", 5)
            }
            for name, config in all_agents.items()
        }
    }

@app.get("/api/mcp/health")
async def health_check() -> Dict[str, Any]:
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": int(time.time() - metrics.start_time)
    }

@app.get("/api/mcp/agents/capabilities")
async def get_agents_by_capability(capability: Optional[str] = None) -> Dict[str, Any]:
    """
    Get agents by capability or list all capabilities
    
    Args:
        capability: Optional capability to filter by
    """
    if capability:
        agents = registry_manager.get_agents_by_capability(capability)
        return {
            "capability": capability,
            "agents": agents,
            "count": len(agents)
        }
    else:
        # Return all unique capabilities
        all_capabilities = set()
        for agent_config in registry_manager.get_enabled_agents().values():
            all_capabilities.update(agent_config.get('capabilities', []))
        
        return {
            "all_capabilities": sorted(list(all_capabilities)),
            "total_capabilities": len(all_capabilities)
        }

@app.get("/api/mcp/agents/{agent_name}")
async def get_agent_details(agent_name: str) -> Dict[str, Any]:
    """Get detailed information about a specific agent"""
    agent_config = registry_manager.get_agent_config(agent_name)
    if not agent_config:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_name}")
    
    health_status = registry_manager.get_agent_health(agent_name)
    
    return {
        "name": agent_name,
        "config": agent_config,
        "health": health_status,
        "enabled": registry_manager.is_agent_enabled(agent_name)
    }

@app.post("/api/mcp/agents/{agent_name}/enable")
async def enable_agent(agent_name: str) -> Dict[str, Any]:
    """Enable a specific agent at runtime"""
    if not registry_manager.get_agent_config(agent_name):
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_name}")
    
    success = await registry_manager.enable_agent(agent_name)
    return {
        "agent": agent_name,
        "enabled": success,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/mcp/agents/{agent_name}/disable")
async def disable_agent(agent_name: str) -> Dict[str, Any]:
    """Disable a specific agent at runtime"""
    if not registry_manager.get_agent_config(agent_name):
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_name}")
    
    success = await registry_manager.disable_agent(agent_name)
    return {
        "agent": agent_name,
        "disabled": success,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/mcp/registry/reload")
async def reload_registry() -> Dict[str, Any]:
    """Manually reload the agent registry"""
    try:
        await registry_manager.reload_registry()
        return {
            "success": True,
            "message": "Registry reloaded successfully",
            "registry_info": registry_manager.get_registry_info(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reload registry: {str(e)}")

@app.get("/api/mcp/registry/info")
async def get_registry_info() -> Dict[str, Any]:
    """Get registry metadata and statistics"""
    return registry_manager.get_registry_info()

# ============================================================================
# FUTURE PROOFING STUBS
# ============================================================================

async def validate_auth_token(token: str) -> bool:
    """
    Validate authentication token (future implementation)
    
    TODO: Implement proper token validation for production security
    """
    # Stub for future auth implementation
    return True

async def enqueue_async_task(task: TaskRequest) -> str:
    """
    Enqueue task for asynchronous processing (future implementation)
    
    TODO: Integrate with message queue system (Redis, RabbitMQ, etc.)
    """
    # Stub for future async job dispatch
    return "task_queue_not_implemented"

async def dispatch_to_local_service(service_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dispatch to local services (future implementation)
    
    TODO: Implement local service dispatch for speech, I/O, etc.
    """
    # Stub for future local service integration
    return {"message": f"Local service '{service_name}' not yet implemented"}

# ============================================================================
# MAIN APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting MCP Server...")
    
    # Run the server
    uvicorn.run(
        "mcp_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
