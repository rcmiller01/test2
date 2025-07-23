"""
Session Presence Detection System
Monitors active user engagement and interaction patterns
"""

import logging
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)

class PresenceState(Enum):
    """User presence states"""
    ACTIVE = "active"           # Actively interacting
    FOCUSED = "focused"         # Engaged but not interacting
    IDLE = "idle"               # Present but inactive
    AWAY = "away"               # Not present
    BACKGROUND = "background"   # App in background
    UNKNOWN = "unknown"         # Cannot determine

class EngagementLevel(Enum):
    """User engagement levels"""
    HIGH = "high"               # Rapid interactions, high emotional engagement
    MODERATE = "moderate"       # Regular interaction pace
    LOW = "low"                 # Slow interactions, distracted
    MINIMAL = "minimal"         # Very occasional interactions

class InteractionType(Enum):
    """Types of user interactions"""
    MESSAGE = "message"         # Text message sent
    VOICE = "voice"             # Voice interaction
    TYPING = "typing"           # Currently typing
    FOCUS = "focus"             # App gained focus
    BLUR = "blur"               # App lost focus
    CLICK = "click"             # UI interaction
    SCROLL = "scroll"           # Content scrolling

@dataclass
class PresenceEvent:
    """Individual presence event"""
    user_id: str
    event_type: InteractionType
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class PresenceMetrics:
    """Aggregated presence metrics"""
    user_id: str
    current_state: PresenceState
    engagement_level: EngagementLevel
    last_interaction: datetime
    session_start: datetime
    active_duration: float      # Minutes of active time
    idle_duration: float        # Minutes of idle time
    interaction_count: int
    interaction_rate: float     # Interactions per minute
    focus_percentage: float     # Percentage of time app was focused

class SessionPresenceDetector:
    """
    Detects and tracks user presence within active sessions
    """
    
    def __init__(self):
        self.active_sessions: Dict[str, PresenceMetrics] = {}
        self.presence_events: Dict[str, List[PresenceEvent]] = {}
        self.presence_rules = {}
        self.engagement_thresholds = {}
        self._initialize_rules()
        
    def _initialize_rules(self):
        """Initialize presence detection rules"""
        
        # State transition rules (seconds)
        self.presence_rules = {
            "active_to_idle": 60,        # 1 minute without interaction
            "idle_to_away": 300,         # 5 minutes idle
            "away_timeout": 1800,        # 30 minutes away = session end
            "focus_required": True,      # App must be focused for active state
            "typing_timeout": 10,        # Typing indicator timeout
        }
        
        # Engagement level thresholds
        self.engagement_thresholds = {
            "high_interaction_rate": 2.0,    # >2 interactions per minute
            "moderate_interaction_rate": 0.5, # 0.5-2 interactions per minute
            "low_interaction_rate": 0.1,     # 0.1-0.5 interactions per minute
            "high_emotion_threshold": 0.7,   # High emotional intensity
            "session_engagement_time": 5,    # Minutes to assess engagement
        }
    
    async def start_session_tracking(
        self, 
        user_id: str, 
        session_id: str
    ) -> PresenceMetrics:
        """Start tracking presence for a session"""
        try:
            now = datetime.now()
            
            # Initialize presence metrics
            metrics = PresenceMetrics(
                user_id=user_id,
                current_state=PresenceState.ACTIVE,
                engagement_level=EngagementLevel.MODERATE,
                last_interaction=now,
                session_start=now,
                active_duration=0.0,
                idle_duration=0.0,
                interaction_count=0,
                interaction_rate=0.0,
                focus_percentage=100.0
            )
            
            self.active_sessions[session_id] = metrics
            self.presence_events[session_id] = []
            
            # Start monitoring loop
            asyncio.create_task(self._monitor_session_presence(session_id))
            
            logger.info(f"👁️ Started presence tracking for session {session_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Failed to start session tracking: {e}")
            raise
    
    async def record_interaction(
        self,
        session_id: str,
        interaction_type: InteractionType,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record a user interaction event"""
        try:
            if session_id not in self.active_sessions:
                logger.warning(f"⚠️ Session {session_id} not found for interaction recording")
                return
            
            metrics = self.active_sessions[session_id]
            now = datetime.now()
            
            # Create presence event
            event = PresenceEvent(
                user_id=metrics.user_id,
                event_type=interaction_type,
                timestamp=now,
                metadata=metadata or {}
            )
            
            # Store event
            self.presence_events[session_id].append(event)
            
            # Update metrics
            metrics.last_interaction = now
            metrics.interaction_count += 1
            
            # Update presence state based on interaction
            await self._update_presence_state(session_id, interaction_type)
            
            # Recalculate engagement level
            await self._calculate_engagement_level(session_id)
            
            logger.debug(f"📊 Recorded {interaction_type.value} interaction for session {session_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to record interaction: {e}")
    
    async def _monitor_session_presence(self, session_id: str):
        """Monitor session presence continuously"""
        try:
            while session_id in self.active_sessions:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                if session_id in self.active_sessions:
                    await self._update_presence_metrics(session_id)
                    await self._check_state_transitions(session_id)
                    
        except Exception as e:
            logger.error(f"❌ Presence monitoring error for session {session_id}: {e}")
    
    async def _update_presence_state(
        self, 
        session_id: str, 
        interaction_type: InteractionType
    ):
        """Update presence state based on interaction"""
        try:
            metrics = self.active_sessions[session_id]
            
            # Interaction resets idle/away states
            if interaction_type in [InteractionType.MESSAGE, InteractionType.VOICE, 
                                  InteractionType.TYPING, InteractionType.CLICK]:
                if metrics.current_state in [PresenceState.IDLE, PresenceState.AWAY]:
                    metrics.current_state = PresenceState.ACTIVE
                    logger.debug(f"👁️ User returned to active state in session {session_id}")
            
            # Focus events
            elif interaction_type == InteractionType.FOCUS:
                if metrics.current_state == PresenceState.BACKGROUND:
                    metrics.current_state = PresenceState.ACTIVE
                    logger.debug(f"👁️ App focused, user active in session {session_id}")
            
            # Blur events
            elif interaction_type == InteractionType.BLUR:
                metrics.current_state = PresenceState.BACKGROUND
                logger.debug(f"👁️ App blurred, user in background for session {session_id}")
                
        except Exception as e:
            logger.error(f"❌ Failed to update presence state: {e}")
    
    async def _check_state_transitions(self, session_id: str):
        """Check for automatic state transitions based on time"""
        try:
            metrics = self.active_sessions[session_id]
            now = datetime.now()
            time_since_interaction = (now - metrics.last_interaction).total_seconds()
            
            # Active to idle transition
            if (metrics.current_state == PresenceState.ACTIVE and 
                time_since_interaction > self.presence_rules["active_to_idle"]):
                metrics.current_state = PresenceState.IDLE
                logger.debug(f"👁️ User went idle in session {session_id}")
            
            # Idle to away transition
            elif (metrics.current_state == PresenceState.IDLE and 
                  time_since_interaction > self.presence_rules["idle_to_away"]):
                metrics.current_state = PresenceState.AWAY
                logger.debug(f"👁️ User went away in session {session_id}")
            
            # Away timeout - end session
            elif (metrics.current_state == PresenceState.AWAY and 
                  time_since_interaction > self.presence_rules["away_timeout"]):
                logger.info(f"👁️ Session {session_id} ended due to extended away time")
                await self.end_session_tracking(session_id)
                
        except Exception as e:
            logger.error(f"❌ Failed to check state transitions: {e}")
    
    async def _update_presence_metrics(self, session_id: str):
        """Update calculated presence metrics"""
        try:
            metrics = self.active_sessions[session_id]
            now = datetime.now()
            
            # Calculate session duration
            session_duration = (now - metrics.session_start).total_seconds() / 60
            
            # Calculate interaction rate
            if session_duration > 0:
                metrics.interaction_rate = metrics.interaction_count / session_duration
            
            # Calculate active/idle durations and focus percentage
            await self._calculate_time_metrics(session_id)
            
        except Exception as e:
            logger.error(f"❌ Failed to update presence metrics: {e}")
    
    async def _calculate_time_metrics(self, session_id: str):
        """Calculate time-based metrics from events"""
        try:
            events = self.presence_events.get(session_id, [])
            metrics = self.active_sessions[session_id]
            
            if not events:
                return
            
            # Calculate focus percentage
            focus_time = 0
            total_time = (datetime.now() - metrics.session_start).total_seconds()
            
            app_focused = True  # Start assuming focused
            last_event_time = metrics.session_start
            
            for event in events:
                if app_focused:
                    focus_time += (event.timestamp - last_event_time).total_seconds()
                
                # Update focus state
                if event.event_type == InteractionType.FOCUS:
                    app_focused = True
                elif event.event_type == InteractionType.BLUR:
                    app_focused = False
                
                last_event_time = event.timestamp
            
            # Add time from last event to now
            if app_focused:
                focus_time += (datetime.now() - last_event_time).total_seconds()
            
            metrics.focus_percentage = (focus_time / max(total_time, 1)) * 100
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate time metrics: {e}")
    
    async def _calculate_engagement_level(self, session_id: str):
        """Calculate user engagement level"""
        try:
            metrics = self.active_sessions[session_id]
            
            # Base engagement on interaction rate
            if metrics.interaction_rate >= self.engagement_thresholds["high_interaction_rate"]:
                metrics.engagement_level = EngagementLevel.HIGH
            elif metrics.interaction_rate >= self.engagement_thresholds["moderate_interaction_rate"]:
                metrics.engagement_level = EngagementLevel.MODERATE
            elif metrics.interaction_rate >= self.engagement_thresholds["low_interaction_rate"]:
                metrics.engagement_level = EngagementLevel.LOW
            else:
                metrics.engagement_level = EngagementLevel.MINIMAL
            
            # Adjust based on focus percentage
            if metrics.focus_percentage < 50:
                # Reduce engagement if app not focused
                if metrics.engagement_level == EngagementLevel.HIGH:
                    metrics.engagement_level = EngagementLevel.MODERATE
                elif metrics.engagement_level == EngagementLevel.MODERATE:
                    metrics.engagement_level = EngagementLevel.LOW
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate engagement level: {e}")
    
    async def get_presence_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current presence status for a session"""
        try:
            if session_id not in self.active_sessions:
                return None
            
            metrics = self.active_sessions[session_id]
            now = datetime.now()
            
            # Calculate time since last interaction
            time_since_interaction = (now - metrics.last_interaction).total_seconds()
            
            return {
                "session_id": session_id,
                "user_id": metrics.user_id,
                "presence_state": metrics.current_state.value,
                "engagement_level": metrics.engagement_level.value,
                "last_interaction_seconds": int(time_since_interaction),
                "session_duration_minutes": round((now - metrics.session_start).total_seconds() / 60, 1),
                "interaction_count": metrics.interaction_count,
                "interaction_rate": round(metrics.interaction_rate, 2),
                "focus_percentage": round(metrics.focus_percentage, 1),
                "is_available": metrics.current_state in [PresenceState.ACTIVE, PresenceState.FOCUSED],
                "timestamp": now.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get presence status: {e}")
            return None
    
    async def end_session_tracking(self, session_id: str) -> Optional[Dict[str, Any]]:
        """End session tracking and return summary"""
        try:
            if session_id not in self.active_sessions:
                return None
            
            metrics = self.active_sessions[session_id]
            events = self.presence_events.get(session_id, [])
            
            # Calculate final metrics
            await self._update_presence_metrics(session_id)
            
            # Create summary
            summary = {
                "session_id": session_id,
                "user_id": metrics.user_id,
                "total_duration_minutes": round((datetime.now() - metrics.session_start).total_seconds() / 60, 1),
                "final_state": metrics.current_state.value,
                "final_engagement": metrics.engagement_level.value,
                "total_interactions": metrics.interaction_count,
                "avg_interaction_rate": round(metrics.interaction_rate, 2),
                "focus_percentage": round(metrics.focus_percentage, 1),
                "event_count": len(events)
            }
            
            # Cleanup
            del self.active_sessions[session_id]
            del self.presence_events[session_id]
            
            logger.info(f"👁️ Ended presence tracking for session {session_id}")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Failed to end session tracking: {e}")
            return None
    
    async def get_user_availability(self, user_id: str) -> Dict[str, Any]:
        """Get overall availability status for a user across all sessions"""
        try:
            user_sessions = {
                sid: metrics for sid, metrics in self.active_sessions.items() 
                if metrics.user_id == user_id
            }
            
            if not user_sessions:
                return {
                    "user_id": user_id,
                    "available": False,
                    "status": "no_active_sessions",
                    "session_count": 0
                }
            
            # Find most engaged session
            most_engaged = max(
                user_sessions.values(),
                key=lambda m: (
                    m.engagement_level.value,
                    m.interaction_rate,
                    -((datetime.now() - m.last_interaction).total_seconds())
                )
            )
            
            # Determine overall availability
            available = (
                most_engaged.current_state in [PresenceState.ACTIVE, PresenceState.FOCUSED] and
                most_engaged.engagement_level != EngagementLevel.MINIMAL
            )
            
            return {
                "user_id": user_id,
                "available": available,
                "status": most_engaged.current_state.value,
                "engagement_level": most_engaged.engagement_level.value,
                "session_count": len(user_sessions),
                "last_interaction": most_engaged.last_interaction.isoformat(),
                "best_session_id": next(sid for sid, m in user_sessions.items() if m == most_engaged)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get user availability: {e}")
            return {
                "user_id": user_id,
                "available": False,
                "status": "error",
                "session_count": 0
            }

# Global instance
session_presence = SessionPresenceDetector()

__all__ = ["session_presence", "PresenceState", "EngagementLevel", "InteractionType"]
