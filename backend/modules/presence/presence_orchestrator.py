"""
Presence Orchestrator
Unified presence management combining session tracking, idle detection, and background sensing
"""

import logging
import asyncio
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
import json

from .session_presence import session_presence, PresenceState, EngagementLevel, InteractionType
from .idle_detection import idle_detector, IdleState, ActivityType
from .background_sensing import background_sensor, SensorType, PresenceIndicator

logger = logging.getLogger(__name__)

class UnifiedPresenceState(Enum):
    """Unified presence states combining all detection methods"""
    HIGHLY_ENGAGED = "highly_engaged"       # Actively interacting with high engagement
    ACTIVELY_PRESENT = "actively_present"   # Present and interacting normally
    PASSIVELY_PRESENT = "passively_present" # Present but low engagement
    BRIEFLY_AWAY = "briefly_away"          # Short absence, likely returning
    AWAY = "away"                          # Extended absence
    DEEPLY_AWAY = "deeply_away"            # Long absence, unlikely to return soon
    UNKNOWN = "unknown"                    # Cannot determine presence

class PresenceContext(Enum):
    """Context for presence interpretation"""
    FOCUSED_SESSION = "focused_session"     # Deep work or conversation
    CASUAL_BROWSING = "casual_browsing"     # Light engagement
    MULTITASKING = "multitasking"          # Divided attention
    BACKGROUND_MODE = "background_mode"     # App in background
    BREAK_TIME = "break_time"              # Taking a break
    END_OF_SESSION = "end_of_session"      # Winding down

@dataclass
class UnifiedPresenceData:
    """Comprehensive presence information"""
    user_id: str
    unified_state: UnifiedPresenceState
    context: PresenceContext
    confidence: float
    last_interaction: datetime
    presence_duration: float           # Minutes in current state
    availability_score: float          # 0.0 to 1.0, how available for interaction
    attention_level: float             # 0.0 to 1.0, how focused/engaged
    interruption_receptivity: float    # 0.0 to 1.0, how receptive to interruptions
    predicted_return_time: Optional[float]  # Minutes until expected return (if away)
    contributing_sources: List[str]
    metadata: Dict[str, Any]

class PresenceOrchestrator:
    """
    Orchestrates multiple presence detection systems to provide unified presence intelligence
    """
    
    def __init__(self, db_path: str = "presence.db"):
        self.db_path = db_path
        self.active_users: Dict[str, UnifiedPresenceData] = {}
        self.presence_callbacks: Dict[str, List[Callable]] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.fusion_rules = {}
        self._initialize_fusion_rules()
    
    async def initialize(self):
        """Initialize the presence orchestrator"""
        try:
            # Create database tables
            conn = sqlite3.connect(self.db_path)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS presence_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    unified_state TEXT NOT NULL,
                    context TEXT NOT NULL,
                    confidence REAL,
                    availability_score REAL,
                    attention_level REAL,
                    session_duration REAL,
                    contributing_sources TEXT,
                    metadata JSON,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS presence_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    pattern_type TEXT NOT NULL,
                    pattern_data JSON,
                    confidence REAL,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(user_id, pattern_type)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS presence_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    source_system TEXT NOT NULL,
                    event_data JSON,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.close()
            logger.info("👁️ Presence Orchestrator initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize presence orchestrator: {e}")
            raise
    
    def _initialize_fusion_rules(self):
        """Initialize presence fusion rules and weights"""
        
        # Source weights for unified presence calculation
        self.fusion_rules = {
            "source_weights": {
                "session_presence": 0.4,       # Direct interaction data
                "idle_detection": 0.3,         # User activity patterns  
                "background_sensing": 0.3,     # Ambient signals
            },
            "state_transitions": {
                # Rules for state transition delays and thresholds
                "engagement_threshold_high": 0.8,
                "engagement_threshold_medium": 0.5,
                "attention_threshold_high": 0.7,
                "attention_threshold_medium": 0.4,
                "availability_threshold": 0.6,
            },
            "context_rules": {
                # Rules for determining presence context
                "focused_session_indicators": ["high_interaction_rate", "focused_app", "minimal_idle"],
                "casual_browsing_indicators": ["moderate_interaction", "mixed_focus", "occasional_idle"],
                "multitasking_indicators": ["app_switching", "background_activity", "divided_attention"],
                "break_indicators": ["idle_period", "system_away", "low_engagement"],
            }
        }
    
    async def start_comprehensive_monitoring(self, user_id: str, session_id: str):
        """Start comprehensive presence monitoring for a user"""
        try:
            # Start all monitoring systems
            session_metrics = await session_presence.start_session_tracking(user_id, session_id)
            await idle_detector.start_monitoring(user_id)
            await background_sensor.start_background_sensing(user_id)
            
            # Initialize unified presence data
            self.active_users[user_id] = UnifiedPresenceData(
                user_id=user_id,
                unified_state=UnifiedPresenceState.ACTIVELY_PRESENT,
                context=PresenceContext.FOCUSED_SESSION,
                confidence=0.8,
                last_interaction=datetime.now(),
                presence_duration=0.0,
                availability_score=0.8,
                attention_level=0.7,
                interruption_receptivity=0.6,
                predicted_return_time=None,
                contributing_sources=["session_presence"],
                metadata={"session_id": session_id}
            )
            
            # Start unified monitoring
            task = asyncio.create_task(self._monitor_unified_presence(user_id))
            self.monitoring_tasks[user_id] = task
            
            logger.info(f"👁️ Started comprehensive presence monitoring for user {user_id}")
            return self.active_users[user_id]
            
        except Exception as e:
            logger.error(f"❌ Failed to start comprehensive monitoring: {e}")
            raise
    
    async def _monitor_unified_presence(self, user_id: str):
        """Monitor and fuse presence data from all sources"""
        try:
            while user_id in self.monitoring_tasks:
                await asyncio.sleep(15)  # Update every 15 seconds
                
                if user_id in self.active_users:
                    await self._update_unified_presence(user_id)
                    await self._trigger_presence_callbacks(user_id)
                    
        except asyncio.CancelledError:
            logger.debug(f"👁️ Unified presence monitoring cancelled for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Unified presence monitoring error for user {user_id}: {e}")
    
    async def _update_unified_presence(self, user_id: str):
        """Update unified presence by fusing data from all sources"""
        try:
            if user_id not in self.active_users:
                return
            
            unified_data = self.active_users[user_id]
            
            # Collect data from all sources
            sources_data = await self._collect_source_data(user_id)
            
            # Fuse presence states
            unified_state, confidence = await self._fuse_presence_states(sources_data)
            
            # Determine context
            context = await self._determine_presence_context(sources_data)
            
            # Calculate derived metrics
            availability_score = await self._calculate_availability_score(sources_data, unified_state)
            attention_level = await self._calculate_attention_level(sources_data)
            interruption_receptivity = await self._calculate_interruption_receptivity(
                unified_state, attention_level, availability_score
            )
            
            # Update presence duration
            now = datetime.now()
            if unified_data.unified_state == unified_state:
                unified_data.presence_duration += (now - unified_data.last_interaction).total_seconds() / 60
            else:
                unified_data.presence_duration = 0
            
            # Predict return time if away
            predicted_return = await self._predict_return_time(user_id, sources_data, unified_state)
            
            # Update unified data
            old_state = unified_data.unified_state
            unified_data.unified_state = unified_state
            unified_data.context = context
            unified_data.confidence = confidence
            unified_data.last_interaction = now
            unified_data.availability_score = availability_score
            unified_data.attention_level = attention_level
            unified_data.interruption_receptivity = interruption_receptivity
            unified_data.predicted_return_time = predicted_return
            unified_data.contributing_sources = list(sources_data.keys())
            
            # Log state changes
            if old_state != unified_state:
                logger.info(f"👁️ User {user_id} presence: {old_state.value} → {unified_state.value}")
                await self._log_presence_change(user_id, old_state, unified_state, unified_data)
            
        except Exception as e:
            logger.error(f"❌ Failed to update unified presence: {e}")
    
    async def _collect_source_data(self, user_id: str) -> Dict[str, Any]:
        """Collect data from all presence sources"""
        sources_data = {}
        
        try:
            # Get session presence data
            session_id = self.active_users[user_id].metadata.get("session_id")
            if session_id:
                session_status = await session_presence.get_presence_status(session_id)
                if session_status:
                    sources_data["session_presence"] = session_status
        except Exception as e:
            logger.error(f"❌ Failed to get session presence data: {e}")
        
        try:
            # Get idle detection data
            idle_status = await idle_detector.get_idle_status(user_id)
            if idle_status and idle_status.get("monitoring"):
                sources_data["idle_detection"] = idle_status
        except Exception as e:
            logger.error(f"❌ Failed to get idle detection data: {e}")
        
        try:
            # Get background sensing data
            background_signal = await background_sensor.get_presence_signal(user_id)
            if background_signal:
                sources_data["background_sensing"] = background_signal
        except Exception as e:
            logger.error(f"❌ Failed to get background sensing data: {e}")
        
        return sources_data
    
    async def _fuse_presence_states(self, sources_data: Dict[str, Any]) -> Tuple[UnifiedPresenceState, float]:
        """Fuse presence states from multiple sources"""
        try:
            # Extract presence indicators from each source
            session_state = None
            idle_state = None
            background_state = None
            
            if "session_presence" in sources_data:
                session_data = sources_data["session_presence"]
                session_state = session_data.get("presence_state")
                engagement = session_data.get("engagement_level")
            
            if "idle_detection" in sources_data:
                idle_data = sources_data["idle_detection"]
                idle_state = idle_data.get("idle_state")
            
            if "background_sensing" in sources_data:
                background_data = sources_data["background_sensing"]
                background_state = background_data.get("presence_indicator")
            
            # Fusion logic
            weights = self.fusion_rules["source_weights"]
            total_weight = 0
            weighted_presence_score = 0
            
            # Session presence contribution
            if session_state:
                weight = weights["session_presence"]
                score = self._map_session_state_to_score(session_state, engagement)
                weighted_presence_score += weight * score
                total_weight += weight
            
            # Idle detection contribution
            if idle_state:
                weight = weights["idle_detection"]
                score = self._map_idle_state_to_score(idle_state)
                weighted_presence_score += weight * score
                total_weight += weight
            
            # Background sensing contribution
            if background_state:
                weight = weights["background_sensing"]
                score = self._map_background_state_to_score(background_state)
                weighted_presence_score += weight * score
                total_weight += weight
            
            # Calculate unified score
            if total_weight > 0:
                unified_score = weighted_presence_score / total_weight
                confidence = min(1.0, total_weight / sum(weights.values()))
            else:
                unified_score = 0.5
                confidence = 0.3
            
            # Map score to unified state
            unified_state = self._map_score_to_unified_state(unified_score, sources_data)
            
            return unified_state, confidence
            
        except Exception as e:
            logger.error(f"❌ Failed to fuse presence states: {e}")
            return UnifiedPresenceState.UNKNOWN, 0.3
    
    def _map_session_state_to_score(self, state: str, engagement: str) -> float:
        """Map session presence state to numerical score"""
        state_scores = {
            "active": 0.9,
            "focused": 0.8,
            "idle": 0.3,
            "away": 0.1,
            "background": 0.2
        }
        
        engagement_multiplier = {
            "high": 1.0,
            "moderate": 0.8,
            "low": 0.6,
            "minimal": 0.4
        }
        
        base_score = state_scores.get(state, 0.5)
        multiplier = engagement_multiplier.get(engagement, 0.8)
        
        return base_score * multiplier
    
    def _map_idle_state_to_score(self, state: str) -> float:
        """Map idle state to numerical score"""
        idle_scores = {
            "active": 0.9,
            "short_idle": 0.6,
            "medium_idle": 0.3,
            "long_idle": 0.1,
            "deep_idle": 0.05
        }
        return idle_scores.get(state, 0.5)
    
    def _map_background_state_to_score(self, state: str) -> float:
        """Map background sensing state to numerical score"""
        background_scores = {
            "strong_presence": 0.9,
            "likely_present": 0.7,
            "uncertain": 0.5,
            "likely_away": 0.3,
            "strong_absence": 0.1
        }
        return background_scores.get(state, 0.5)
    
    def _map_score_to_unified_state(self, score: float, sources_data: Dict[str, Any]) -> UnifiedPresenceState:
        """Map unified score to unified presence state"""
        
        # Check for high engagement indicators
        high_engagement = (
            score > 0.8 and
            sources_data.get("session_presence", {}).get("engagement_level") == "high"
        )
        
        if high_engagement:
            return UnifiedPresenceState.HIGHLY_ENGAGED
        elif score >= 0.7:
            return UnifiedPresenceState.ACTIVELY_PRESENT
        elif score >= 0.4:
            return UnifiedPresenceState.PASSIVELY_PRESENT
        elif score >= 0.2:
            return UnifiedPresenceState.BRIEFLY_AWAY
        elif score >= 0.1:
            return UnifiedPresenceState.AWAY
        else:
            return UnifiedPresenceState.DEEPLY_AWAY
    
    async def _determine_presence_context(self, sources_data: Dict[str, Any]) -> PresenceContext:
        """Determine presence context from source data"""
        try:
            # Analyze patterns to determine context
            session_data = sources_data.get("session_presence", {})
            idle_data = sources_data.get("idle_detection", {})
            background_data = sources_data.get("background_sensing", {})
            
            # High interaction rate + focused app = focused session
            if (session_data.get("interaction_rate", 0) > 2.0 and
                session_data.get("focus_percentage", 0) > 80):
                return PresenceContext.FOCUSED_SESSION
            
            # App in background = background mode
            if session_data.get("presence_state") == "background":
                return PresenceContext.BACKGROUND_MODE
            
            # Medium idle + some activity = break time
            if idle_data.get("idle_state") in ["medium_idle", "long_idle"]:
                return PresenceContext.BREAK_TIME
            
            # Multiple sensors with mixed signals = multitasking
            if len(sources_data) >= 2 and background_data.get("confidence", 0) < 0.6:
                return PresenceContext.MULTITASKING
            
            # Default to casual browsing
            return PresenceContext.CASUAL_BROWSING
            
        except Exception as e:
            logger.error(f"❌ Failed to determine presence context: {e}")
            return PresenceContext.CASUAL_BROWSING
    
    async def _calculate_availability_score(
        self, 
        sources_data: Dict[str, Any], 
        unified_state: UnifiedPresenceState
    ) -> float:
        """Calculate how available the user is for interaction"""
        try:
            base_scores = {
                UnifiedPresenceState.HIGHLY_ENGAGED: 0.9,
                UnifiedPresenceState.ACTIVELY_PRESENT: 0.8,
                UnifiedPresenceState.PASSIVELY_PRESENT: 0.5,
                UnifiedPresenceState.BRIEFLY_AWAY: 0.2,
                UnifiedPresenceState.AWAY: 0.1,
                UnifiedPresenceState.DEEPLY_AWAY: 0.05,
                UnifiedPresenceState.UNKNOWN: 0.3
            }
            
            base_score = base_scores.get(unified_state, 0.3)
            
            # Adjust based on focus and engagement
            session_data = sources_data.get("session_presence", {})
            focus_percentage = session_data.get("focus_percentage", 50) / 100
            engagement_level = session_data.get("engagement_level", "moderate")
            
            engagement_multiplier = {
                "high": 1.0,
                "moderate": 0.9,
                "low": 0.7,
                "minimal": 0.5
            }
            
            adjusted_score = base_score * focus_percentage * engagement_multiplier.get(engagement_level, 0.8)
            
            return min(1.0, adjusted_score)
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate availability score: {e}")
            return 0.5
    
    async def _calculate_attention_level(self, sources_data: Dict[str, Any]) -> float:
        """Calculate user's attention level"""
        try:
            session_data = sources_data.get("session_presence", {})
            idle_data = sources_data.get("idle_detection", {})
            
            # Base attention from interaction patterns
            interaction_rate = session_data.get("interaction_rate", 0)
            attention_from_interaction = min(1.0, interaction_rate / 3.0)  # Max at 3 interactions/min
            
            # Adjust for idle state
            idle_state = idle_data.get("idle_state", "active")
            idle_attention_map = {
                "active": 1.0,
                "short_idle": 0.8,
                "medium_idle": 0.4,
                "long_idle": 0.2,
                "deep_idle": 0.1
            }
            
            idle_attention = idle_attention_map.get(idle_state, 0.5)
            
            # Combine metrics
            attention_level = (attention_from_interaction * 0.6 + idle_attention * 0.4)
            
            return attention_level
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate attention level: {e}")
            return 0.5
    
    async def _calculate_interruption_receptivity(
        self, 
        unified_state: UnifiedPresenceState,
        attention_level: float,
        availability_score: float
    ) -> float:
        """Calculate how receptive user is to interruptions"""
        try:
            # Base receptivity from presence state
            base_receptivity = {
                UnifiedPresenceState.HIGHLY_ENGAGED: 0.3,  # Low - deeply focused
                UnifiedPresenceState.ACTIVELY_PRESENT: 0.7,
                UnifiedPresenceState.PASSIVELY_PRESENT: 0.9,
                UnifiedPresenceState.BRIEFLY_AWAY: 0.8,   # High when returning
                UnifiedPresenceState.AWAY: 0.2,
                UnifiedPresenceState.DEEPLY_AWAY: 0.1,
                UnifiedPresenceState.UNKNOWN: 0.5
            }
            
            base = base_receptivity.get(unified_state, 0.5)
            
            # Adjust based on attention (high attention = lower receptivity to interruption)
            attention_factor = 1.0 - (attention_level * 0.5)
            
            # Adjust based on availability
            availability_factor = availability_score
            
            receptivity = base * attention_factor * availability_factor
            
            return min(1.0, max(0.0, receptivity))
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate interruption receptivity: {e}")
            return 0.5
    
    async def _predict_return_time(
        self, 
        user_id: str, 
        sources_data: Dict[str, Any], 
        unified_state: UnifiedPresenceState
    ) -> Optional[float]:
        """Predict when user might return if currently away"""
        try:
            if unified_state not in [UnifiedPresenceState.BRIEFLY_AWAY, 
                                   UnifiedPresenceState.AWAY, 
                                   UnifiedPresenceState.DEEPLY_AWAY]:
                return None
            
            # Get idle prediction
            prediction = await idle_detector.predict_break_time(user_id)
            if prediction:
                predicted_minutes = prediction.get("predicted_break_in_minutes", 0)
                if predicted_minutes > 0:
                    return predicted_minutes
            
            # Fallback predictions based on state
            state_predictions = {
                UnifiedPresenceState.BRIEFLY_AWAY: 2.0,   # 2 minutes
                UnifiedPresenceState.AWAY: 10.0,          # 10 minutes
                UnifiedPresenceState.DEEPLY_AWAY: 30.0    # 30 minutes
            }
            
            return state_predictions.get(unified_state)
            
        except Exception as e:
            logger.error(f"❌ Failed to predict return time: {e}")
            return None
    
    async def _trigger_presence_callbacks(self, user_id: str):
        """Trigger registered presence callbacks"""
        try:
            callbacks = self.presence_callbacks.get(user_id, [])
            unified_data = self.active_users.get(user_id)
            
            if not unified_data:
                return
            
            for callback in callbacks:
                try:
                    await callback(user_id, unified_data)
                except Exception as e:
                    logger.error(f"❌ Presence callback error: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Failed to trigger presence callbacks: {e}")
    
    async def _log_presence_change(
        self, 
        user_id: str, 
        old_state: UnifiedPresenceState,
        new_state: UnifiedPresenceState,
        unified_data: UnifiedPresenceData
    ):
        """Log presence state change to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                INSERT INTO presence_history 
                (user_id, unified_state, context, confidence, availability_score, 
                 attention_level, session_duration, contributing_sources, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                new_state.value,
                unified_data.context.value,
                unified_data.confidence,
                unified_data.availability_score,
                unified_data.attention_level,
                unified_data.presence_duration,
                json.dumps(unified_data.contributing_sources),
                json.dumps(unified_data.metadata)
            ))
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to log presence change: {e}")
    
    def register_presence_callback(self, user_id: str, callback: Callable):
        """Register callback for presence changes"""
        if user_id not in self.presence_callbacks:
            self.presence_callbacks[user_id] = []
        self.presence_callbacks[user_id].append(callback)
    
    async def record_interaction(
        self, 
        user_id: str, 
        interaction_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record user interaction across all systems"""
        try:
            # Update session presence
            session_id = None
            if user_id in self.active_users:
                session_id = self.active_users[user_id].metadata.get("session_id")
            
            if session_id:
                # Map interaction type to session interaction type
                session_interaction_map = {
                    "message": InteractionType.MESSAGE,
                    "voice": InteractionType.VOICE,
                    "typing": InteractionType.TYPING,
                    "click": InteractionType.CLICK,
                    "scroll": InteractionType.SCROLL,
                    "focus": InteractionType.FOCUS,
                    "blur": InteractionType.BLUR
                }
                
                session_type = session_interaction_map.get(interaction_type, InteractionType.MESSAGE)
                await session_presence.record_interaction(session_id, session_type, metadata)
            
            # Update idle detection
            activity_map = {
                "message": ActivityType.KEYBOARD,
                "voice": ActivityType.VOICE,
                "typing": ActivityType.KEYBOARD,
                "click": ActivityType.UI_INTERACTION,
                "scroll": ActivityType.NAVIGATION,
                "focus": ActivityType.UI_INTERACTION,
                "blur": ActivityType.UI_INTERACTION
            }
            
            activity_type = activity_map.get(interaction_type, ActivityType.UI_INTERACTION)
            await idle_detector.record_activity(user_id, activity_type, metadata=metadata)
            
            # Update background sensing for browser signals
            if interaction_type in ["focus", "blur", "click", "scroll", "typing"]:
                value = 0.9 if interaction_type in ["click", "typing"] else 0.7
                await background_sensor.record_browser_signal(user_id, interaction_type, value, metadata)
            
        except Exception as e:
            logger.error(f"❌ Failed to record interaction: {e}")
    
    async def get_unified_presence(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get unified presence data for user"""
        try:
            if user_id not in self.active_users:
                return None
            
            unified_data = self.active_users[user_id]
            
            return {
                "user_id": user_id,
                "unified_state": unified_data.unified_state.value,
                "context": unified_data.context.value,
                "confidence": round(unified_data.confidence, 2),
                "presence_duration_minutes": round(unified_data.presence_duration, 1),
                "availability_score": round(unified_data.availability_score, 2),
                "attention_level": round(unified_data.attention_level, 2),
                "interruption_receptivity": round(unified_data.interruption_receptivity, 2),
                "predicted_return_minutes": unified_data.predicted_return_time,
                "last_interaction": unified_data.last_interaction.isoformat(),
                "contributing_sources": unified_data.contributing_sources,
                "is_available": unified_data.availability_score > 0.5,
                "is_interruptible": unified_data.interruption_receptivity > 0.6,
                "metadata": unified_data.metadata,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get unified presence: {e}")
            return None
    
    async def stop_comprehensive_monitoring(self, user_id: str):
        """Stop all presence monitoring for a user"""
        try:
            # Stop orchestrator monitoring
            if user_id in self.monitoring_tasks:
                self.monitoring_tasks[user_id].cancel()
                del self.monitoring_tasks[user_id]
            
            # Stop individual systems
            session_id = None
            if user_id in self.active_users:
                session_id = self.active_users[user_id].metadata.get("session_id")
            
            if session_id:
                await session_presence.end_session_tracking(session_id)
            
            await idle_detector.stop_monitoring(user_id)
            await background_sensor.stop_background_sensing(user_id)
            
            # Clean up data
            if user_id in self.active_users:
                del self.active_users[user_id]
            if user_id in self.presence_callbacks:
                del self.presence_callbacks[user_id]
            
            logger.info(f"👁️ Stopped comprehensive presence monitoring for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to stop comprehensive monitoring: {e}")

# Global instance
presence_orchestrator = PresenceOrchestrator()

__all__ = ["presence_orchestrator", "UnifiedPresenceState", "PresenceContext"]
