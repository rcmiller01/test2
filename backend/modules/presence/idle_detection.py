"""
Idle Detection System
Advanced idle time tracking with smart activity detection
"""

import logging
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)

class IdleState(Enum):
    """Idle detection states"""
    ACTIVE = "active"           # User actively interacting
    SHORT_IDLE = "short_idle"   # Brief pause (1-5 minutes)
    MEDIUM_IDLE = "medium_idle" # Extended pause (5-15 minutes)
    LONG_IDLE = "long_idle"     # Long absence (15-30 minutes)
    DEEP_IDLE = "deep_idle"     # Very long absence (30+ minutes)

class ActivityType(Enum):
    """Types of user activity"""
    KEYBOARD = "keyboard"       # Typing activity
    MOUSE = "mouse"            # Mouse movement/clicks
    VOICE = "voice"            # Voice input
    UI_INTERACTION = "ui_interaction" # Button clicks, form submissions
    CONTENT_CONSUMPTION = "content_consumption" # Reading, listening
    NAVIGATION = "navigation"   # Page/section changes

@dataclass
class ActivityEvent:
    """Individual activity event"""
    activity_type: ActivityType
    timestamp: datetime
    intensity: float           # 0.0 to 1.0, how engaged the activity suggests
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IdlePattern:
    """User's idle behavior patterns"""
    user_id: str
    typical_session_length: float    # Minutes
    average_idle_frequency: float    # Times per hour
    preferred_break_duration: float  # Minutes
    activity_patterns: Dict[str, float] # Activity type frequencies
    last_updated: datetime

class IdleDetectionSystem:
    """
    Advanced idle detection with pattern learning and smart notifications
    """
    
    def __init__(self):
        self.user_activities: Dict[str, List[ActivityEvent]] = {}
        self.idle_states: Dict[str, IdleState] = {}
        self.idle_patterns: Dict[str, IdlePattern] = {}
        self.idle_callbacks: Dict[str, List[Callable]] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.idle_thresholds = {}
        self._initialize_thresholds()
    
    def _initialize_thresholds(self):
        """Initialize idle detection thresholds"""
        self.idle_thresholds = {
            IdleState.SHORT_IDLE: 60,      # 1 minute
            IdleState.MEDIUM_IDLE: 300,    # 5 minutes
            IdleState.LONG_IDLE: 900,      # 15 minutes
            IdleState.DEEP_IDLE: 1800,     # 30 minutes
        }
        
        # Activity intensity weights
        self.activity_weights = {
            ActivityType.KEYBOARD: 1.0,        # High engagement
            ActivityType.VOICE: 1.0,           # High engagement
            ActivityType.UI_INTERACTION: 0.8,  # Medium-high engagement
            ActivityType.MOUSE: 0.6,           # Medium engagement
            ActivityType.NAVIGATION: 0.4,      # Low-medium engagement
            ActivityType.CONTENT_CONSUMPTION: 0.3, # Low engagement
        }
    
    async def start_monitoring(self, user_id: str):
        """Start idle monitoring for a user"""
        try:
            if user_id in self.monitoring_tasks:
                # Already monitoring
                return
            
            # Initialize user data
            self.user_activities[user_id] = []
            self.idle_states[user_id] = IdleState.ACTIVE
            self.idle_callbacks[user_id] = []
            
            # Load or create idle pattern
            if user_id not in self.idle_patterns:
                self.idle_patterns[user_id] = IdlePattern(
                    user_id=user_id,
                    typical_session_length=45.0,
                    average_idle_frequency=2.0,
                    preferred_break_duration=5.0,
                    activity_patterns={},
                    last_updated=datetime.now()
                )
            
            # Start monitoring task
            task = asyncio.create_task(self._monitor_idle_state(user_id))
            self.monitoring_tasks[user_id] = task
            
            logger.info(f"⏱️ Started idle monitoring for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start idle monitoring: {e}")
            raise
    
    async def record_activity(
        self, 
        user_id: str, 
        activity_type: ActivityType,
        intensity: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record user activity event"""
        try:
            if user_id not in self.user_activities:
                await self.start_monitoring(user_id)
            
            # Calculate intensity if not provided
            if intensity is None:
                intensity = self.activity_weights.get(activity_type, 0.5)
            
            # Create activity event
            event = ActivityEvent(
                activity_type=activity_type,
                timestamp=datetime.now(),
                intensity=intensity,
                metadata=metadata or {}
            )
            
            # Store event
            self.user_activities[user_id].append(event)
            
            # Keep only recent events (last 2 hours)
            cutoff = datetime.now() - timedelta(hours=2)
            self.user_activities[user_id] = [
                e for e in self.user_activities[user_id] 
                if e.timestamp > cutoff
            ]
            
            # Update idle state
            await self._update_idle_state(user_id)
            
            # Update activity patterns
            await self._update_activity_patterns(user_id, activity_type)
            
            logger.debug(f"📊 Recorded {activity_type.value} activity for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to record activity: {e}")
    
    async def _monitor_idle_state(self, user_id: str):
        """Monitor user idle state continuously"""
        try:
            while user_id in self.monitoring_tasks:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                if user_id in self.user_activities:
                    await self._check_idle_transitions(user_id)
                    await self._trigger_idle_callbacks(user_id)
                    
        except asyncio.CancelledError:
            logger.debug(f"⏱️ Idle monitoring cancelled for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Idle monitoring error for user {user_id}: {e}")
    
    async def _update_idle_state(self, user_id: str):
        """Update idle state based on recent activity"""
        try:
            activities = self.user_activities.get(user_id, [])
            if not activities:
                return
            
            # Get last activity
            last_activity = max(activities, key=lambda a: a.timestamp)
            time_since_activity = (datetime.now() - last_activity.timestamp).total_seconds()
            
            # Determine idle state
            old_state = self.idle_states.get(user_id, IdleState.DEEP_IDLE)
            new_state = IdleState.ACTIVE
            
            if time_since_activity >= self.idle_thresholds[IdleState.DEEP_IDLE]:
                new_state = IdleState.DEEP_IDLE
            elif time_since_activity >= self.idle_thresholds[IdleState.LONG_IDLE]:
                new_state = IdleState.LONG_IDLE
            elif time_since_activity >= self.idle_thresholds[IdleState.MEDIUM_IDLE]:
                new_state = IdleState.MEDIUM_IDLE
            elif time_since_activity >= self.idle_thresholds[IdleState.SHORT_IDLE]:
                new_state = IdleState.SHORT_IDLE
            
            # Update state if changed
            if old_state != new_state:
                self.idle_states[user_id] = new_state
                logger.debug(f"⏱️ User {user_id} idle state: {old_state.value} → {new_state.value}")
            
        except Exception as e:
            logger.error(f"❌ Failed to update idle state: {e}")
    
    async def _check_idle_transitions(self, user_id: str):
        """Check for idle state transitions and patterns"""
        try:
            current_state = self.idle_states.get(user_id, IdleState.ACTIVE)
            
            # Check for return from idle
            if current_state != IdleState.ACTIVE:
                activities = self.user_activities.get(user_id, [])
                if activities:
                    last_activity = max(activities, key=lambda a: a.timestamp)
                    time_since_activity = (datetime.now() - last_activity.timestamp).total_seconds()
                    
                    # If recent activity, user has returned
                    if time_since_activity < 30:  # 30 seconds
                        old_state = current_state
                        self.idle_states[user_id] = IdleState.ACTIVE
                        await self._handle_return_from_idle(user_id, old_state)
            
        except Exception as e:
            logger.error(f"❌ Failed to check idle transitions: {e}")
    
    async def _handle_return_from_idle(self, user_id: str, previous_state: IdleState):
        """Handle user returning from idle state"""
        try:
            idle_duration = self._get_idle_duration_name(previous_state)
            logger.info(f"👋 User {user_id} returned from {idle_duration} idle")
            
            # Update patterns based on idle duration
            pattern = self.idle_patterns.get(user_id)
            if pattern:
                # This could be used to learn user break preferences
                if previous_state == IdleState.SHORT_IDLE:
                    # Short break, probably still engaged
                    pass
                elif previous_state in [IdleState.MEDIUM_IDLE, IdleState.LONG_IDLE]:
                    # Medium break, might need gentle re-engagement
                    pass
                elif previous_state == IdleState.DEEP_IDLE:
                    # Long break, might need context restoration
                    pass
            
        except Exception as e:
            logger.error(f"❌ Failed to handle return from idle: {e}")
    
    def _get_idle_duration_name(self, state: IdleState) -> str:
        """Get human-readable idle duration name"""
        names = {
            IdleState.SHORT_IDLE: "brief",
            IdleState.MEDIUM_IDLE: "medium",
            IdleState.LONG_IDLE: "extended",
            IdleState.DEEP_IDLE: "long"
        }
        return names.get(state, "unknown")
    
    async def _update_activity_patterns(self, user_id: str, activity_type: ActivityType):
        """Update user activity patterns for learning"""
        try:
            pattern = self.idle_patterns.get(user_id)
            if not pattern:
                return
            
            # Update activity frequency
            activity_key = activity_type.value
            if activity_key not in pattern.activity_patterns:
                pattern.activity_patterns[activity_key] = 0
            
            pattern.activity_patterns[activity_key] += 1
            pattern.last_updated = datetime.now()
            
            # Decay old patterns (weekly)
            if (datetime.now() - pattern.last_updated).days >= 7:
                for key in pattern.activity_patterns:
                    pattern.activity_patterns[key] *= 0.9  # 10% decay
            
        except Exception as e:
            logger.error(f"❌ Failed to update activity patterns: {e}")
    
    async def _trigger_idle_callbacks(self, user_id: str):
        """Trigger registered idle callbacks"""
        try:
            callbacks = self.idle_callbacks.get(user_id, [])
            current_state = self.idle_states.get(user_id, IdleState.ACTIVE)
            
            for callback in callbacks:
                try:
                    await callback(user_id, current_state)
                except Exception as e:
                    logger.error(f"❌ Idle callback error: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Failed to trigger idle callbacks: {e}")
    
    def register_idle_callback(self, user_id: str, callback: Callable):
        """Register callback for idle state changes"""
        if user_id not in self.idle_callbacks:
            self.idle_callbacks[user_id] = []
        self.idle_callbacks[user_id].append(callback)
    
    async def get_idle_status(self, user_id: str) -> Dict[str, Any]:
        """Get current idle status for user"""
        try:
            if user_id not in self.idle_states:
                return {
                    "user_id": user_id,
                    "idle_state": "not_monitored",
                    "monitoring": False
                }
            
            activities = self.user_activities.get(user_id, [])
            current_state = self.idle_states[user_id]
            
            # Calculate time since last activity
            last_activity_time = None
            idle_duration = 0
            
            if activities:
                last_activity = max(activities, key=lambda a: a.timestamp)
                last_activity_time = last_activity.timestamp
                idle_duration = (datetime.now() - last_activity_time).total_seconds()
            
            # Calculate activity summary
            recent_activities = [
                a for a in activities 
                if a.timestamp > datetime.now() - timedelta(minutes=30)
            ]
            
            activity_summary = {}
            for activity in recent_activities:
                activity_type = activity.activity_type.value
                if activity_type not in activity_summary:
                    activity_summary[activity_type] = 0
                activity_summary[activity_type] += 1
            
            return {
                "user_id": user_id,
                "idle_state": current_state.value,
                "idle_duration_seconds": int(idle_duration),
                "last_activity": last_activity_time.isoformat() if last_activity_time else None,
                "recent_activity_count": len(recent_activities),
                "activity_summary": activity_summary,
                "monitoring": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get idle status: {e}")
            return {
                "user_id": user_id,
                "idle_state": "error",
                "monitoring": False
            }
    
    async def get_activity_insights(self, user_id: str) -> Dict[str, Any]:
        """Get activity insights and patterns for user"""
        try:
            pattern = self.idle_patterns.get(user_id)
            activities = self.user_activities.get(user_id, [])
            
            if not pattern or not activities:
                return {
                    "user_id": user_id,
                    "insights_available": False
                }
            
            # Calculate recent activity trends
            recent_activities = [
                a for a in activities 
                if a.timestamp > datetime.now() - timedelta(hours=24)
            ]
            
            # Activity distribution
            activity_distribution = {}
            total_intensity = 0
            
            for activity in recent_activities:
                activity_type = activity.activity_type.value
                if activity_type not in activity_distribution:
                    activity_distribution[activity_type] = {"count": 0, "intensity": 0}
                
                activity_distribution[activity_type]["count"] += 1
                activity_distribution[activity_type]["intensity"] += activity.intensity
                total_intensity += activity.intensity
            
            # Calculate engagement score
            avg_intensity = total_intensity / max(len(recent_activities), 1)
            
            return {
                "user_id": user_id,
                "insights_available": True,
                "typical_session_length": pattern.typical_session_length,
                "preferred_break_duration": pattern.preferred_break_duration,
                "recent_activity_count": len(recent_activities),
                "activity_distribution": activity_distribution,
                "average_engagement": round(avg_intensity, 2),
                "patterns_last_updated": pattern.last_updated.isoformat(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get activity insights: {e}")
            return {
                "user_id": user_id,
                "insights_available": False
            }
    
    async def stop_monitoring(self, user_id: str):
        """Stop idle monitoring for a user"""
        try:
            # Cancel monitoring task
            if user_id in self.monitoring_tasks:
                self.monitoring_tasks[user_id].cancel()
                del self.monitoring_tasks[user_id]
            
            # Clean up data
            if user_id in self.user_activities:
                del self.user_activities[user_id]
            if user_id in self.idle_states:
                del self.idle_states[user_id]
            if user_id in self.idle_callbacks:
                del self.idle_callbacks[user_id]
            
            logger.info(f"⏱️ Stopped idle monitoring for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to stop idle monitoring: {e}")
    
    async def predict_break_time(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Predict when user might take a break based on patterns"""
        try:
            pattern = self.idle_patterns.get(user_id)
            activities = self.user_activities.get(user_id, [])
            
            if not pattern or not activities:
                return None
            
            # Calculate time since session start (approximate)
            recent_session_start = None
            
            # Find start of current session (after significant idle period)
            sorted_activities = sorted(activities, key=lambda a: a.timestamp)
            for i, activity in enumerate(sorted_activities):
                if i == 0:
                    recent_session_start = activity.timestamp
                    continue
                
                time_gap = (activity.timestamp - sorted_activities[i-1].timestamp).total_seconds()
                if time_gap > 900:  # 15 minute gap indicates new session
                    recent_session_start = activity.timestamp
            
            if not recent_session_start:
                return None
            
            # Calculate current session duration
            current_session_duration = (datetime.now() - recent_session_start).total_seconds() / 60
            
            # Predict break based on typical session length
            time_until_break = pattern.typical_session_length - current_session_duration
            
            # Adjust based on current engagement
            current_state = self.idle_states.get(user_id, IdleState.ACTIVE)
            if current_state != IdleState.ACTIVE:
                time_until_break = 0  # Already on break
            
            break_probability = min(1.0, current_session_duration / pattern.typical_session_length)
            
            return {
                "user_id": user_id,
                "current_session_duration": round(current_session_duration, 1),
                "predicted_break_in_minutes": max(0, round(time_until_break, 1)),
                "break_probability": round(break_probability, 2),
                "typical_session_length": pattern.typical_session_length,
                "recommendation": "break_soon" if time_until_break <= 5 else "continue_session"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to predict break time: {e}")
            return None

# Global instance
idle_detector = IdleDetectionSystem()

__all__ = ["idle_detector", "IdleState", "ActivityType"]
