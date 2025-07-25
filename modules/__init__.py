"""
Unified Companion System Modules

Core modules for the emotional AI companion system.
"""

# Import key components for easier access
try:
    from .core.unified_companion import UnifiedCompanion
    from .database.database_interface import create_database_interface
    from .core.crisis_safety_override import CrisisSafetyOverride
except ImportError:
    # Graceful degradation for missing dependencies
    pass

__version__ = "3.0.0"
__author__ = "Unified Companion Development Team"
