#!/usr/bin/env python3
"""
MCP Server Startup Script

This script provides a convenient way to start the MCP server with proper
configuration and logging. It handles environment setup and graceful shutdown.

Usage:
    python start_mcp_server.py [--port PORT] [--host HOST] [--reload]

Author: Dolphin AI System
Date: July 30, 2025
Tag: #ref-mcp-integration
"""

import argparse
import asyncio
import logging
import os
import signal
import sys
from pathlib import Path

import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Setup environment variables and paths"""
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    # Set default environment variables if not already set
    os.environ.setdefault('MCP_LOG_LEVEL', 'INFO')
    os.environ.setdefault('MCP_REGISTRY_PATH', str(current_dir / 'agents' / 'registry.json'))

def check_dependencies():
    """Check that required dependencies are available"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'httpx',
        'pydantic',
        'watchdog'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {missing_packages}")
        logger.error("Please install with: pip install -r requirements_mcp.txt")
        return False
    
    return True

def check_registry_file():
    """Check that the agent registry file exists"""
    registry_path = os.environ.get('MCP_REGISTRY_PATH')
    if not registry_path or not Path(registry_path).exists():
        logger.error(f"Agent registry file not found: {registry_path}")
        logger.error("Please ensure agents/registry.json exists")
        return False
    
    logger.info(f"Using agent registry: {registry_path}")
    return True

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)

def main():
    """Main startup function"""
    parser = argparse.ArgumentParser(description="Start the MCP Server")
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to (default: 8000)')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload for development')
    parser.add_argument('--log-level', default='info', choices=['debug', 'info', 'warning', 'error'],
                       help='Log level (default: info)')
    parser.add_argument('--workers', type=int, default=1, help='Number of worker processes (default: 1)')
    
    args = parser.parse_args()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Setup environment
    setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check registry file
    if not check_registry_file():
        sys.exit(1)
    
    # Start the server
    logger.info("🚀 Starting MCP Server...")
    logger.info(f"   Host: {args.host}")
    logger.info(f"   Port: {args.port}")
    logger.info(f"   Reload: {args.reload}")
    logger.info(f"   Log Level: {args.log_level}")
    logger.info(f"   Workers: {args.workers}")
    
    try:
        uvicorn.run(
            "mcp_server:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level,
            workers=args.workers if not args.reload else 1,  # Reload mode requires 1 worker
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
