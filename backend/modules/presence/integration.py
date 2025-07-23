"""
Presence Integration
Helper functions for integrating presence system with other modules
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta

from .presence_orchestrator import presence_orchestrator, UnifiedPresenceState, PresenceContext

logger = logging.getLogger(__name__)

class PresenceIntegration:
    """
    Integration layer for connecting presence system with other modules
    """
    
    def __init__(self):
        self.integration_callbacks: Dict[str, List[Callable]] = {}
        self.persona_presence_cache: Dict[str, Dict[str, Any]] = {}
    
    async def initialize(self):
        """Initialize presence integration"""
        try:
            await presence_orchestrator.initialize()
            logger.info("🔗 Presence integration initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize presence integration: {e}")
            raise
    
    # Persona System Integration
    async def get_presence_for_persona(self, user_id: str) -> Dict[str, Any]:
        """Get presence information formatted for persona system"""
        try:
            presence_data = await presence_orchestrator.get_unified_presence(user_id)
            
            if not presence_data:
                return {
                    "available": False,
                    "state": "unknown",
                    "engagement": 0.0,
                    "context": "unknown"
                }
            
            # Format for persona system
            persona_presence = {
                "available": presence_data.get('is_available', False),
                "interruptible": presence_data.get('is_interruptible', False),
                "state": presence_data.get('unified_state', 'unknown'),
                "context": presence_data.get('context', 'unknown'),
                "engagement": presence_data.get('attention_level', 0.0),
                "availability_score": presence_data.get('availability_score', 0.0),
                "interruption_receptivity": presence_data.get('interruption_receptivity', 0.0),
                "predicted_return_minutes": presence_data.get('predicted_return_minutes'),
                "last_interaction": presence_data.get('last_interaction'),
                "session_duration": presence_data.get('presence_duration_minutes', 0),
                "confidence": presence_data.get('confidence', 0.0)
            }
            
            # Cache for quick access
            self.persona_presence_cache[user_id] = persona_presence
            
            return persona_presence
            
        except Exception as e:
            logger.error(f"❌ Failed to get presence for persona: {e}")
            return {"available": False, "state": "error", "engagement": 0.0}
    
    async def should_persona_proactively_engage(self, user_id: str) -> Dict[str, Any]:
        """Determine if persona should proactively engage with user"""
        try:
            presence_data = await self.get_presence_for_persona(user_id)
            
            state = presence_data.get('state', 'unknown')
            interruption_receptivity = presence_data.get('interruption_receptivity', 0.0)
            session_duration = presence_data.get('session_duration', 0)
            
            # Proactive engagement rules
            should_engage = False
            engagement_type = None
            confidence = 0.0
            reasons = []
            
            # User just returned from being away
            if state == 'actively_present' and session_duration < 2:
                should_engage = True
                engagement_type = 'welcome_back'
                confidence = 0.8
                reasons.append('User returned from being away')
            
            # User is highly receptive and has been active for a while
            elif interruption_receptivity > 0.8 and session_duration > 15:
                should_engage = True
                engagement_type = 'check_in'
                confidence = 0.7
                reasons.append('User highly receptive and in long session')
            
            # User seems to be taking a break
            elif state == 'briefly_away' and interruption_receptivity > 0.6:
                should_engage = True
                engagement_type = 'gentle_presence'
                confidence = 0.6
                reasons.append('User on break but receptive')
            
            return {
                "should_engage": should_engage,
                "engagement_type": engagement_type,
                "confidence": confidence,
                "reasons": reasons,
                "presence_state": state,
                "interruption_receptivity": interruption_receptivity
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to determine proactive engagement: {e}")
            return {"should_engage": False, "confidence": 0.0}
    
    # Memory System Integration
    async def get_presence_context_for_memory(self, user_id: str) -> Dict[str, Any]:
        """Get presence context for memory system"""
        try:
            presence_data = await presence_orchestrator.get_unified_presence(user_id)
            
            if not presence_data:
                return {"context": "no_presence_data"}
            
            # Format for memory system
            memory_context = {
                "interaction_context": {
                    "presence_state": presence_data.get('unified_state'),
                    "attention_level": presence_data.get('attention_level'),
                    "availability": presence_data.get('availability_score'),
                    "session_duration": presence_data.get('presence_duration_minutes'),
                    "interaction_quality": "high" if presence_data.get('attention_level', 0) > 0.7 else "normal"
                },
                "emotional_context": {
                    "engagement_level": "high" if presence_data.get('attention_level', 0) > 0.8 else 
                                      "medium" if presence_data.get('attention_level', 0) > 0.5 else "low",
                    "receptivity": presence_data.get('interruption_receptivity'),
                    "focus_state": presence_data.get('context')
                },
                "temporal_context": {
                    "session_start": presence_data.get('last_interaction'),
                    "duration_minutes": presence_data.get('presence_duration_minutes'),
                    "predicted_availability": presence_data.get('predicted_return_minutes')
                }
            }
            
            return memory_context
            
        except Exception as e:
            logger.error(f"❌ Failed to get presence context for memory: {e}")
            return {"context": "error_retrieving_presence"}
    
    # Safety System Integration
    async def get_presence_safety_context(self, user_id: str) -> Dict[str, Any]:
        """Get presence context for safety system"""
        try:
            presence_data = await presence_orchestrator.get_unified_presence(user_id)
            
            if not presence_data:
                return {"safety_mode": "cautious", "confidence": 0.3}
            
            state = presence_data.get('unified_state')
            attention = presence_data.get('attention_level', 0)
            context = presence_data.get('context')
            
            # Determine safety context based on presence
            if state in ['highly_engaged', 'actively_present'] and attention > 0.7:
                safety_mode = "attentive"
                safety_confidence = 0.9
            elif state == 'passively_present' or attention < 0.5:
                safety_mode = "cautious"
                safety_confidence = 0.6
            elif state in ['briefly_away', 'away']:
                safety_mode = "minimal_interaction"
                safety_confidence = 0.8
            else:
                safety_mode = "cautious"
                safety_confidence = 0.4
            
            return {
                "safety_mode": safety_mode,
                "confidence": safety_confidence,
                "presence_state": state,
                "attention_level": attention,
                "context": context,
                "interaction_appropriateness": attention > 0.5
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get presence safety context: {e}")
            return {"safety_mode": "cautious", "confidence": 0.3}
    
    # Voice System Integration
    async def get_voice_interaction_context(self, user_id: str) -> Dict[str, Any]:
        """Get presence context for voice interactions"""
        try:
            presence_data = await presence_orchestrator.get_unified_presence(user_id)
            
            if not presence_data:
                return {"voice_mode": "text_preferred", "confidence": 0.3}
            
            state = presence_data.get('unified_state')
            context = presence_data.get('context')
            attention = presence_data.get('attention_level', 0)
            
            # Determine voice interaction appropriateness
            voice_appropriate = False
            voice_mode = "text_preferred"
            
            if state in ['highly_engaged', 'actively_present'] and attention > 0.6:
                if context in ['focused_session', 'casual_browsing']:
                    voice_appropriate = True
                    voice_mode = "voice_preferred"
            
            elif state == 'passively_present' and attention > 0.4:
                voice_appropriate = True
                voice_mode = "voice_optional"
            
            return {
                "voice_appropriate": voice_appropriate,
                "voice_mode": voice_mode,
                "attention_level": attention,
                "presence_state": state,
                "context": context,
                "recommendations": {
                    "use_voice": voice_appropriate,
                    "voice_volume": "normal" if attention > 0.7 else "soft",
                    "interaction_style": "conversational" if attention > 0.6 else "brief"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get voice interaction context: {e}")
            return {"voice_mode": "text_preferred", "confidence": 0.3}
    
    # Unified Integration Methods
    async def start_session_with_presence(
        self, 
        user_id: str, 
        session_id: str,
        additional_callbacks: Optional[List[Callable]] = None
    ) -> Dict[str, Any]:
        """Start a session with full presence monitoring"""
        try:
            # Start presence monitoring
            presence_data = await presence_orchestrator.start_comprehensive_monitoring(user_id, session_id)
            
            # Register integration callbacks
            if additional_callbacks:
                for callback in additional_callbacks:
                    presence_orchestrator.register_presence_callback(user_id, callback)
            
            # Get initial context for all systems
            persona_context = await self.get_presence_for_persona(user_id)
            memory_context = await self.get_presence_context_for_memory(user_id)
            safety_context = await self.get_presence_safety_context(user_id)
            voice_context = await self.get_voice_interaction_context(user_id)
            
            return {
                "session_started": True,
                "user_id": user_id,
                "session_id": session_id,
                "presence_monitoring": True,
                "initial_contexts": {
                    "persona": persona_context,
                    "memory": memory_context,
                    "safety": safety_context,
                    "voice": voice_context
                },
                "presence_data": {
                    "state": presence_data.unified_state.value,
                    "context": presence_data.context.value,
                    "confidence": presence_data.confidence
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to start session with presence: {e}")
            raise
    
    async def record_interaction_across_systems(
        self, 
        user_id: str,
        interaction_type: str,
        interaction_data: Dict[str, Any]
    ):
        """Record interaction and update all integrated systems"""
        try:
            # Record in presence system
            await presence_orchestrator.record_interaction(user_id, interaction_type, interaction_data)
            
            # Get updated presence context
            updated_presence = await self.get_presence_for_persona(user_id)
            
            # Trigger integration callbacks if needed
            callbacks = self.integration_callbacks.get(user_id, [])
            for callback in callbacks:
                try:
                    await callback(user_id, interaction_type, updated_presence)
                except Exception as e:
                    logger.error(f"❌ Integration callback error: {e}")
            
        except Exception as e:
            logger.error(f"❌ Failed to record interaction across systems: {e}")
    
    def register_integration_callback(self, user_id: str, callback: Callable):
        """Register callback for integration events"""
        if user_id not in self.integration_callbacks:
            self.integration_callbacks[user_id] = []
        self.integration_callbacks[user_id].append(callback)
    
    async def cleanup_user_integration(self, user_id: str):
        """Clean up integration data for user"""
        try:
            # Stop presence monitoring
            await presence_orchestrator.stop_comprehensive_monitoring(user_id)
            
            # Clean up caches and callbacks
            if user_id in self.persona_presence_cache:
                del self.persona_presence_cache[user_id]
            
            if user_id in self.integration_callbacks:
                del self.integration_callbacks[user_id]
            
            logger.info(f"🔗 Cleaned up presence integration for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup user integration: {e}")

# Global instance
presence_integration = PresenceIntegration()

__all__ = ["presence_integration"]
