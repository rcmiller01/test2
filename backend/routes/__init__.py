"""
Backend Routes Module

API routes and handlers for the unified companion system.
"""

try:
    from .phase2_routes import *
    from .romantic_routes import *
except ImportError:
    # Routes may not be fully implemented yet
    pass
