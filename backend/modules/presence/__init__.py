"""
Presence Module
Ambient presence sensing for natural contextual interactions
"""

from .session_presence import session_presence, PresenceState, EngagementLevel, InteractionType
from .idle_detection import idle_detector, IdleState, ActivityType  
from .background_sensing import background_sensor, SensorType, PresenceIndicator
from .presence_orchestrator import presence_orchestrator, UnifiedPresenceState, PresenceContext
from .presence_routes import presence_bp, register_presence_routes
from .integration import presence_integration

__version__ = "1.0.0"

__all__ = [
    # Core orchestrator
    "presence_orchestrator",
    "UnifiedPresenceState", 
    "PresenceContext",
    
    # Individual detection modules
    "session_presence",
    "idle_detector", 
    "background_sensor",
    
    # Enums and types
    "PresenceState",
    "EngagementLevel", 
    "InteractionType",
    "IdleState",
    "ActivityType",
    "SensorType",
    "PresenceIndicator",
    
    # API routes
    "presence_bp",
    "register_presence_routes",
    
    # Integration layer
    "presence_integration"
]
