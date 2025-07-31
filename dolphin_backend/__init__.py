#!/usr/bin/env python3
"""
Dolphin Backend Package

This package contains the backend modules for the Dolphin AI system.
"""

__version__ = "2.1.0"
__author__ = "Dolphin AI System"

# Package imports
try:
    from .main import app
    from .mcp_bridge import MCPBridge, MCPError
except ImportError:
    # Handle case where dependencies might not be available
    app = None
    MCPBridge = None
    MCPError = Exception

__all__ = ["app", "MCPBridge", "MCPError"]
