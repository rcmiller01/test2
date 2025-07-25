"""
Backend Module

Main backend components for the unified companion system.
"""

# Core backend imports
try:
    from .app import app
    from .main import *
except ImportError:
    # Graceful degradation
    pass
