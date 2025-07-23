"""
Safety Integration Helper
Easy integration of ethical safety layer with existing application
"""

import logging
from fastapi import FastAPI
from .routes.safety_routes import safety_router
from .modules.safety.contextual_safety_engine import contextual_safety_engine
from .modules.safety.anchor_processor import anchor_processor
from .modules.safety.session_control import session_control

logger = logging.getLogger(__name__)

def integrate_safety_layer(app: FastAPI):
    """
    Integrate the ethical safety layer with the main FastAPI application
    
    Args:
        app: FastAPI application instance
    """
    try:
        # Add safety routes
        app.include_router(safety_router)
        
        logger.info("🛡️ Safety layer integrated successfully")
        logger.info("   - Contextual safety engine: ✅")
        logger.info("   - Anchor phrase processor: ✅") 
        logger.info("   - Session control system: ✅")
        logger.info("   - Safety API routes: ✅")
        
        # Log available endpoints
        safety_endpoints = [
            "POST /api/safety/content/evaluate",
            "GET  /api/safety/content/categories", 
            "GET  /api/safety/safety-levels",
            "POST /api/safety/anchor/trigger",
            "GET  /api/safety/anchor/phrases",
            "POST /api/safety/anchor/custom",
            "POST /api/safety/session/start",
            "POST /api/safety/session/update", 
            "POST /api/safety/session/end",
            "GET  /api/safety/session/{user_id}/statistics",
            "POST /api/safety/preferences/set",
            "GET  /api/safety/statistics/{user_id}",
            "GET  /api/safety/health"
        ]
        
        logger.info(f"🔗 {len(safety_endpoints)} safety endpoints available")
        
    except Exception as e:
        logger.error(f"❌ Failed to integrate safety layer: {e}")
        raise

# Export the integration function
__all__ = ["integrate_safety_layer"]
