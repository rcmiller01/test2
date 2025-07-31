#!/usr/bin/env python3
"""
House of Minds Main Application

This is the main entry point for the House of Minds AI system,
integrating MCP, Ollama, and the Dolphin AI backend.

Author: Dolphin AI System
Date: July 30, 2025
"""

import asyncio
import logging
import signal
import sys
import os
import traceback
from pathlib import Path
from typing import Optional, Dict, Any
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import our modules
from config_manager import ConfigManager, DolphinConfig
from ollama_client import OllamaClient, OllamaError, OllamaConfig
from mcp_bridge import MCPBridge, MCPError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('house_of_minds.log')
    ]
)

logger = logging.getLogger(__name__)

class HouseOfMinds:
    """
    Main House of Minds application
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config()
        # Apply environment variables
        self.config.update_from_env()
        self.app = FastAPI(
            title="House of Minds",
            description="Advanced AI System with MCP and Ollama Integration",
            version="2.1.0"
        )
        self.mcp_bridge: Optional[MCPBridge] = None
        self.ollama_client: Optional[OllamaClient] = None
        self.setup_middleware()
        self.setup_routes()
        self._running = False
    
    def setup_middleware(self):
        """Setup FastAPI middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/")
        async def root():
            """Root endpoint"""
            return {
                "name": "House of Minds",
                "version": "2.1.0",
                "status": "running",
                "components": {
                    "mcp": self.mcp_bridge is not None,
                    "ollama": self.ollama_client is not None
                }
            }
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            health_status = {
                "status": "healthy",
                "timestamp": asyncio.get_event_loop().time(),
                "components": {}
            }
            
            # Check MCP bridge
            if self.mcp_bridge:
                try:
                    mcp_health = await self.mcp_bridge.health_check()
                    health_status["components"]["mcp"] = mcp_health
                except Exception as e:
                    health_status["components"]["mcp"] = {"status": "unhealthy", "error": str(e)}
                    health_status["status"] = "degraded"
            
            # Check Ollama client
            if self.ollama_client:
                try:
                    ollama_health = await self.ollama_client.health_check()
                    health_status["components"]["ollama"] = ollama_health
                except Exception as e:
                    health_status["components"]["ollama"] = {"status": "unhealthy", "error": str(e)}
                    health_status["status"] = "degraded"
            
            return health_status
        
        @self.app.get("/config")
        async def get_config():
            """Get current configuration"""
            return {
                "mcp": {"enabled": self.config.mcp.enabled, "base_url": self.config.mcp.base_url},
                "ollama": {"enabled": self.config.ollama.enabled, "base_url": self.config.ollama.base_url},
                "dolphin": {"host": self.config.host, "port": self.config.port}
            }
        
        @self.app.post("/chat")
        async def chat_endpoint(request: Dict[str, Any]):
            """
            Chat endpoint that routes to appropriate backend
            """
            try:
                message = request.get("message", "")
                if not message:
                    raise HTTPException(status_code=400, detail="Message is required")
                
                # Determine routing based on request
                route_to = request.get("route_to", "auto")
                
                if route_to == "mcp" or (route_to == "auto" and self.mcp_bridge):
                    # Route to MCP
                    if not self.mcp_bridge:
                        raise HTTPException(status_code=503, detail="MCP bridge not available")
                    
                    result = await self.mcp_bridge.route_task({
                        "method": "chat",
                        "params": {"message": message}
                    })
                    return {"response": result, "source": "mcp"}
                
                elif route_to == "ollama" or (route_to == "auto" and self.ollama_client):
                    # Route to Ollama
                    if not self.ollama_client:
                        raise HTTPException(status_code=503, detail="Ollama client not available")
                    
                    result = await self.ollama_client.generate(
                        message,
                        model=request.get("model"),
                        stream=False
                    )
                    return {"response": result["response"], "source": "ollama"}
                
                else:
                    raise HTTPException(status_code=503, detail="No backend available")
                    
            except MCPError as e:
                logger.error(f"MCP error in chat: {e}")
                raise HTTPException(status_code=500, detail=f"MCP error: {e}")
            except OllamaError as e:
                logger.error(f"Ollama error in chat: {e}")
                raise HTTPException(status_code=500, detail=f"Ollama error: {e}")
            except Exception as e:
                logger.error(f"Unexpected error in chat: {e}")
                raise HTTPException(status_code=500, detail=f"Internal error: {e}")
        
        @self.app.get("/stats")
        async def get_stats():
            """Get system statistics"""
            stats = {
                "system": {
                    "running": self._running,
                    "config_loaded": self.config_manager is not None
                }
            }
            
            if self.mcp_bridge:
                stats["mcp"] = self.mcp_bridge.get_stats()
            
            if self.ollama_client:
                stats["ollama"] = self.ollama_client.get_stats()
            
            return stats
        
        @self.app.post("/mcp/request")
        async def mcp_request(request: Dict[str, Any]):
            """Direct MCP request endpoint"""
            if not self.mcp_bridge:
                raise HTTPException(status_code=503, detail="MCP bridge not available")
            
            try:
                result = await self.mcp_bridge.route_task(request)
                return {"result": result}
            except MCPError as e:
                logger.error(f"MCP request error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/ollama/generate")
        async def ollama_generate(request: Dict[str, Any]):
            """Direct Ollama generate endpoint"""
            if not self.ollama_client:
                raise HTTPException(status_code=503, detail="Ollama client not available")
            
            try:
                prompt = request.get("prompt", "")
                if not prompt:
                    raise HTTPException(status_code=400, detail="Prompt is required")
                
                result = await self.ollama_client.generate(
                    prompt,
                    model=request.get("model"),
                    stream=request.get("stream", False),
                    options=request.get("options")
                )
                return result
            except OllamaError as e:
                logger.error(f"Ollama generate error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def initialize(self):
        """Initialize the application components"""
        logger.info("Initializing House of Minds...")
        
        try:
            # Initialize MCP bridge if configured
            if self.config.mcp.enabled:
                logger.info("Initializing MCP bridge...")
                # Set environment variables for MCP bridge config
                os.environ["MCP_HOST"] = self.config.mcp.host
                os.environ["MCP_PORT"] = str(self.config.mcp.port)
                os.environ["MCP_BASE_URL"] = self.config.mcp.base_url
                os.environ["MCP_TIMEOUT"] = str(self.config.mcp.timeout)
                os.environ["MCP_MAX_RETRIES"] = str(self.config.mcp.retry_attempts)
                
                self.mcp_bridge = MCPBridge()
                await self.mcp_bridge.__aenter__()
                logger.info("MCP bridge initialized successfully")
            
            # Initialize Ollama client if configured
            if self.config.ollama.enabled:
                logger.info("Initializing Ollama client...")
                # Convert config format
                ollama_config = OllamaConfig(
                    host=self.config.ollama.host,
                    port=self.config.ollama.port,
                    base_url=self.config.ollama.base_url,
                    default_model=self.config.ollama.default_model,
                    timeout=self.config.ollama.timeout,
                    max_retries=self.config.ollama.max_retries,
                    stream=self.config.ollama.stream
                )
                self.ollama_client = OllamaClient(ollama_config)
                await self.ollama_client.__aenter__()
                logger.info("Ollama client initialized successfully")
            
            self._running = True
            logger.info("House of Minds initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize House of Minds: {e}")
            logger.error(traceback.format_exc())
            raise
    
    async def shutdown(self):
        """Shutdown the application components"""
        logger.info("Shutting down House of Minds...")
        
        self._running = False
        
        # Shutdown MCP bridge
        if self.mcp_bridge:
            try:
                await self.mcp_bridge.__aexit__(None, None, None)
                logger.info("MCP bridge shut down successfully")
            except Exception as e:
                logger.error(f"Error shutting down MCP bridge: {e}")
        
        # Shutdown Ollama client
        if self.ollama_client:
            try:
                await self.ollama_client.__aexit__(None, None, None)
                logger.info("Ollama client shut down successfully")
            except Exception as e:
                logger.error(f"Error shutting down Ollama client: {e}")
        
        logger.info("House of Minds shut down complete")

# Global application instance
app_instance: Optional[HouseOfMinds] = None

async def create_app(config_path: Optional[str] = None) -> FastAPI:
    """Create and initialize the FastAPI application"""
    global app_instance
    
    app_instance = HouseOfMinds(config_path)
    await app_instance.initialize()
    
    return app_instance.app

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    if app_instance:
        asyncio.create_task(app_instance.shutdown())

async def main():
    """Main entry point"""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create the application
        app = await create_app()
        
        # Get config for server settings
        config = app_instance.config if app_instance else DolphinConfig()
        
        # Run the server
        uvicorn_config = uvicorn.Config(
            app,
            host=config.host,
            port=config.port,
            log_level="info",
            reload=config.debug
        )
        
        server = uvicorn.Server(uvicorn_config)
        
        logger.info(f"Starting House of Minds server on {config.host}:{config.port}")
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Failed to start House of Minds: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)
    finally:
        if app_instance:
            await app_instance.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
